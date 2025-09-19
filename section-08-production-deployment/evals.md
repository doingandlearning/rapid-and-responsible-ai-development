# 📏 Guide to Evaluating LLM/RAG Workflows

## 1. Why Evals Matter

A RAG pipeline that “seems to work” in demos can fail badly in production:

* **Hallucinations** (LLM makes up facts).
* **Irrelevant retrievals** (wrong chunks).
* **Bias / fairness issues**.
* **Latency** that breaks user expectations.

Evaluations give you **ground truth checks** and **continuous monitoring** so you can iterate systematically.

---

## 2. Levels of Evaluation

### A) Retrieval Evaluation

* **Goal:** Do we retrieve the right documents/chunks?
* **Metrics:**

  * **Recall\@k** – proportion of relevant docs found within top-k results.
  * **Precision\@k** – proportion of retrieved docs that are relevant.
  * **MRR (Mean Reciprocal Rank)** – how far down the list the first relevant result is.
* **Manual setup:** Label a set of queries with expected docs → compare retrieval outputs.
* **Automated trick:** If docs have structured metadata, use it as weak supervision (“all fee queries should surface finance docs”).

---

### B) Generation Evaluation

* **Goal:** Is the answer useful, accurate, and well-grounded?
* **Metrics:**

  * **Faithfulness / Groundedness** – % of claims that are directly supported by retrieved docs.
  * **Answer relevance** – does it address the query intent?
  * **Citation quality** – are correct sources cited?
* **Methods:**

  * LLM-as-judge – use a stronger model to rate outputs against guidelines.
  * Human annotation – gold standard but expensive.
  * QA pairs – compare generated answers with reference answers.

---

### C) System/Operational Evaluation

* **Latency** – average time to retrieve + generate.
* **Cost per query** – embedding + completion costs.
* **Robustness** – measure under noisy input (typos, paraphrasing).
* **Bias/Fairness** – differential performance across groups (e.g. domestic vs international students).

---

## 3. SaaS / Platform Options

Several tools provide evaluation dashboards & pipelines:

* **[TruLens](https://www.trulens.org/)**

  * Open-source + hosted options.
  * Provides “faithfulness, relevance, coherence” scores.
  * Easy integration with LangChain, LlamaIndex.

* **[Ragas](https://docs.ragas.io/)**

  * Purpose-built for RAG evaluation.
  * Focus on retrieval metrics + generation groundedness.
  * Integrates with HuggingFace + LangChain.

* **[LangSmith (LangChain)](https://www.langchain.com/langsmith)**

  * SaaS for tracing + evaluation.
  * Supports datasets, run tracking, LLM-as-judge evals.

* **[Arize Phoenix](https://phoenix.arize.com/)**

  * Observability for LLM apps.
  * Emphasis on tracing + dataset evaluation.

* **Others:** Weights & Biases LLMOps, PromptLayer, Humanloop, Helicone (for logging + basic evals).

---

## 4. Building Your Own Lightweight Evals

### Step 1: Collect Eval Dataset

* 50–200 **representative queries**.
* Label expected answers or at least expected sources.
* Include “hard” cases: ambiguous, multi-hop, edge scenarios.

### Step 2: Run Retrieval Checks

* Store for each query:

  * Retrieved docs/chunks.
  * Which ground-truth docs appear in top-k.
* Calculate Recall\@k, Precision\@k, MRR.

### Step 3: Run Generation Checks

* For each query:

  * Prompt an LLM judge (e.g. GPT-4 or Claude) with:

    > “Given the retrieved documents and the generated answer, rate:
    >
    > 1. Faithfulness (0–5), 2. Relevance (0–5), 3. Citation quality (0–5).”
* Aggregate scores across dataset.

### Step 4: Monitor in Production

* Log queries + answers + retrieved sources.
* Periodically sample and run them through the eval pipeline.
* Track latency, cost, and failure modes (empty retrieval, API errors).

---

## 5. Example: Minimal Eval Script (Python)

```python
import openai
from sklearn.metrics import precision_score, recall_score

# retrieval eval
def eval_retrieval(ground_truth, retrieved):
    gt_set, ret_set = set(ground_truth), set(retrieved)
    precision = len(gt_set & ret_set) / len(ret_set) if ret_set else 0
    recall = len(gt_set & ret_set) / len(gt_set) if gt_set else 0
    return precision, recall

# generation eval (LLM-as-judge)
def eval_generation(answer, context, question):
    prompt = f"""
    Question: {question}
    Answer: {answer}
    Retrieved Context: {context}

    Rate on 0–5 scale:
    1. Faithfulness (answer supported by context)
    2. Relevance (answer addresses question)
    3. Citation quality
    Respond as JSON with keys faithfulness, relevance, citation.
    """
    res = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return res.choices[0].message["content"]
```

---

## 6. Practical Tips

* Start with **small eval sets** (50 queries) → scale later.
* Always include **edge cases** (negation queries, typos, multilingual).
* Combine **automated LLM-as-judge** with **spot-check human reviews**.
* Track **trends over time** (regression tests when you retrain or re-index).
* Don’t over-optimise one metric; balance faithfulness, recall, latency, cost.

---

✅ With this approach you can either:

* Use **SaaS eval platforms** (faster, richer dashboards).
* Or build your own **lean eval pipeline** using JSON datasets, a judge LLM, and simple metrics.
