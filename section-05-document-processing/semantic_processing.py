#!/usr/bin/env python3
# Semantic chunking (minimal, practical).
# - Uses sentence-transformers to find topic boundaries via similarity dips.
# - Prefers boundaries where adjacent-paragraph cosine similarity is a local minimum.
# - Packs semantically coherent chunks to ~target_tokens with small overlap.

# pip install sentence-transformers numpy

import re, sys, json, math
from typing import List, Tuple, Iterable
import numpy as np
from sentence_transformers import SentenceTransformer
from numpy.linalg import norm

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# ---------- basic token estimator ----------
def approx_tokens(s: str) -> int:
    # ~1 token per 4 chars as a simple, fast proxy
    return max(1, int(len(s) / 4))

# ---------- lightweight parsing ----------
CODE_FENCE_RE = re.compile(r"^```.*?$", re.M)

def split_paragraphs(text: str) -> List[str]:
    # Keep fenced code blocks atomic; split other text on blank lines.
    parts = []
    i = 0
    lines = text.splitlines()
    in_code = False
    buf = []

    def flush():
        nonlocal buf
        if buf and any(line.strip() for line in buf):
            # collapse multiple intra-paragraph newlines
            p = re.sub(r"\n{2,}", "\n", "\n".join(buf)).strip()
            if p:
                parts.append(p)
        buf = []

    while i < len(lines):
        line = lines[i]
        if line.strip().startswith("```"):
            # flush pending text para
            flush()
            code = [line]
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code.append(lines[i]); i += 1
            if i < len(lines):  # closing fence
                code.append(lines[i]); i += 1
            parts.append("\n".join(code))
            continue
        # text
        if line.strip() == "":
            flush()
            i += 1
            continue
        buf.append(line)
        i += 1
    flush()
    return parts

def is_code_block(p: str) -> bool:
    return p.strip().startswith("```") and p.strip().endswith("```")

# ---------- embeddings & boundaries ----------
def embed_paragraphs(model, paras: List[str]) -> np.ndarray:
    # For code blocks, prepend a hint so embeddings stay meaningful.
    inputs = [
        ("Code:\n" + p if is_code_block(p) else p)
        for p in paras
    ]
    embs = model.encode(inputs, normalize_embeddings=True, show_progress_bar=False)
    return np.array(embs, dtype=np.float32)

def cosine(a: np.ndarray, b: np.ndarray) -> float:
    # embeddings are normalized; dot equals cosine
    return float(np.dot(a, b))

def similarity_dips(embs: np.ndarray) -> List[int]:
    """
    Compute cosine similarity between adjacent paragraphs; find local minima
    that are significantly below the mean (z-score threshold).
    Returns indices i indicating a boundary *after* paragraph i.
    """
    if len(embs) < 2:
        return []
    sims = np.array([cosine(embs[i], embs[i+1]) for i in range(len(embs)-1)])
    # Smooth a bit
    if len(sims) >= 3:
        kernel = np.array([0.25, 0.5, 0.25])
        pad = np.pad(sims, (1,1), mode="edge")
        sims_s = np.convolve(pad, kernel, mode="same")[1:-1]
    else:
        sims_s = sims

    mu, sigma = float(np.mean(sims_s)), float(np.std(sims_s) + 1e-6)
    z = (sims_s - mu) / sigma

    boundaries = []
    for i in range(len(sims_s)):
        # Local minimum & sufficiently low similarity (z < -0.75 default)
        left = sims_s[i-1] if i-1 >= 0 else sims_s[i]
        right = sims_s[i+1] if i+1 < len(sims_s) else sims_s[i]
        if sims_s[i] <= left and sims_s[i] <= right and z[i] < -0.75:
            boundaries.append(i)     # boundary after paragraph i
    return boundaries

# ---------- pack into chunks ----------
def pack_chunks(paras: List[str], boundaries: List[int], target_tokens=400, overlap_ratio=0.1) -> List[dict]:
    boundary_set = set(boundaries)
    i = 0
    chunks = []
    last_chunk_end = -1

    while i < len(paras):
        tok = 0
        start = i
        # Grow until target, but prefer to end at a boundary if close.
        while i < len(paras) and (tok + approx_tokens(paras[i])) <= target_tokens:
            tok += approx_tokens(paras[i])
            # If we reached or surpassed ~85% of target and current i is a boundary, stop here
            near_target = tok >= int(0.85 * target_tokens)
            if near_target and i in boundary_set:
                i += 1
                break
            i += 1
        # If we didn't hit a boundary, but we overshot or ran out, we end here.
        end = i

        text = "\n\n".join(paras[start:end]).strip()
        if text:
            chunks.append({
                "start_para": start,
                "end_para": end,   # exclusive
                "tokens_est": approx_tokens(text),
                "text": text,
            })

        # Overlap by a fraction of the chunk (by paragraphs), but don’t cut through code blocks.
        if end >= len(paras): break
        span = max(1, end - start)
        overlap_paras = max(0, int(math.floor(span * overlap_ratio)))
        # Ensure overlap boundary does not split a code block
        back = end - overlap_paras
        while back > start and is_code_block(paras[back]):
            back -= 1
        i = max(back, end - 1)  # keep some overlap; never move backwards past start

    return chunks

# ---------- main ----------
def semantic_chunk(text: str, target_tokens=400, overlap=0.10, model_name=MODEL_NAME) -> List[dict]:
    paras = split_paragraphs(text)
    if not paras:
        return []
    model = SentenceTransformer(model_name)
    embs = embed_paragraphs(model, paras)
    bounds = similarity_dips(embs)
    chunks = pack_chunks(paras, bounds, target_tokens=target_tokens, overlap_ratio=overlap)
    # Add simple section titles from preceding heading-like paragraphs (optional)
    heading_re = re.compile(r"^\s{0,3}(#{1,6}\s+.+|[A-Z][A-Za-z0-9 .:/-]{2,})\s*$")
    for c in chunks:
        title = None
        for j in range(c["start_para"], -1, -1):
            if heading_re.match(paras[j]) and not is_code_block(paras[j]) and len(paras[j]) < 180:
                title = paras[j].strip()
                break
        c["title"] = title
    return chunks

if __name__ == "__main__":
    txt = sys.stdin.read()
    chunks = semantic_chunk(txt, target_tokens=400, overlap=0.12)
    for ch in chunks:
        print(json.dumps(ch, ensure_ascii=False))
