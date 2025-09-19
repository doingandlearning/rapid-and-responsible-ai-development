<section data-markdown data-separator-notes="^Note:">
  <textarea data-template>
# AI Ethics & Governance for RAG @ Edinburgh
**Practical guardrails for a live vector search/chat system**

<!-- Note:
- Aim: decisions & actions, not theory.
- Session length: 90 minutes. Keep pace tight.
- Emphasise Edinburgh context (students, staff, sensitive data). -->
  </textarea>
</section>

<section data-markdown data-separator-notes="^Note:">
  <textarea data-template>
## Outcomes & Agenda 
- <span class="fragment">Spot key risks in **your** pipeline</span>
- <span class="fragment">Use a **3-step** risk/incident flow</span>
- <span class="fragment">Leave with **roles + 3 metrics + 2 docs**</span>



<!-- Note:
- Keep slides moving; timebox group work.
- Capture only actionable items (owner + next step). -->
  </textarea>
</section>

<section data-markdown data-separator-notes="^Note:">
  <textarea data-template>
## Warm-up: Pair Share 
- <span class="fragment">One positive AI experience at Edinburgh</span>
- <span class="fragment">One concerning AI experience</span>
- <span class="fragment">What made the good one good?</span>

<!-- Note:
- 2 mins think, 3 mins pairs.
- Harvest 2–3 themes (trust, clarity, speed, fairness). -->
  </textarea>
</section>

<section data-markdown data-separator-notes="^Note:">
  <textarea data-template>
## Our System 
Ingest → chunk → embed → search → cite

**Where can it go wrong?**
- <span class="fragment">Data: gaps, skew, sensitive content</span>
- <span class="fragment">Ranking: weights, recency/department boosts</span>
- <span class="fragment">UX: missing sources, unclear confidence</span>
- <span class="fragment">Logging: PII retention, access controls</span>
<!-- 
Note:
- Anchor discussion in their RAG pipeline.
- Set up for scenarios. -->
  </textarea>
</section>

<section data-markdown data-separator-notes="^Note:">
  <textarea data-template>
## Scenario 1: Bias in Results 
**Query:** “leadership opportunities” → male-skewed results

In trios, list:
- <span class="fragment">Causes (data, ranking, UX)</span>
- <span class="fragment">Impacts (who/what, short vs long term)</span>
- <span class="fragment">Quick mitigations (do tomorrow)</span>

<!-- Note:
- 5 min work, 3 min prep one sticky per trio.
- Encourage *specific* mitigations (e.g. coverage caps, curated boost). -->
  </textarea>
</section>

<section data-markdown data-separator-notes="^Note:">
  <textarea data-template>
## Debrief: Scenario 1 
Share **1 cause + 1 impact + 1 fix** per trio

**Wall of 5 fixes**:
- <span class="fragment">Content coverage checks per department</span>
- <span class="fragment">Diversity-aware rerank (ensure alt perspectives)</span>
- <span class="fragment">Explain “why ranked” in UI</span>
- <span class="fragment">Add support/help docs into top-K pool</span>
- <span class="fragment">Audit set: leadership queries by cohort</span>

<!-- Note:
- Keep to 5; assign tentative owners if possible. -->
  </textarea>
</section>

<section data-markdown data-separator-notes="^Note:">
  <textarea data-template>
## Minimal Risk Framework
**Classify** → **Decide** → **Record**

- **High**: rights/opportunities/sensitive data → human review
- **Medium**: influences choices → monthly audit
- **Low**: informational → monitor

**Record** (1-pager):
- purpose, data, risks, mitigations, owner, review date

<!-- Note:
- This is the core governance “muscle memory”.
- Keep it lightweight; bias towards writing it down. -->
  </textarea>
</section>

<section data-markdown data-separator-notes="^Note:">
  <textarea data-template>
## Transparency Users Notice
- <span class="fragment">Show **sources + confidence**</span>
- <span class="fragment">One-line “why ranked” (similarity/recency/dept match)</span>
- <span class="fragment">“Report bias” link → incident flow</span>

<!-- Note:
- The simplest UI changes often yield the biggest trust gains.
- Encourage shipping this in the capstone UI. -->
  </textarea>
</section>

<section data-markdown data-separator-notes="^Note:">
  <textarea data-template>
## GDPR Essentials (for this system)
- <span class="fragment">Lawful basis: **Public Task** (most cases)</span>
- <span class="fragment">Data minimisation: don’t log PII by default</span>
- <span class="fragment">Retention: TTL on chat logs/embeddings</span>
- <span class="fragment">DPIA triggers: High-risk class, new data types/groups</span>

<!-- Note:
- Keep it crisp; defer deep legal debate.
- Point to DPO for edge cases. -->
  </textarea>
</section>

<section data-markdown data-separator-notes="^Note:">
  <textarea data-template>
## Scenario 2: Incident Simulation (7 min build)
**Complaint:** “International fees results hide scholarship info; unfair to applicants.”

Roles (5 groups):
- Student • Advisor • IT • DPO • Comms

Task:
- First **3 actions** + **1-sentence** external statement

<!-- Note:
- 5 min group work, 2 min internal prep.
- Keep them concrete; no platitudes. -->
  </textarea>
</section>

<section data-markdown data-separator-notes="^Note:">
  <textarea data-template>
## Debrief: Incident Flow (Contain → Diagnose → Fix → Communicate)
- <span class="fragment">Contain: disable biased boost; add banner</span>
- <span class="fragment">Diagnose: sample queries by cohort; inspect weights</span>
- <span class="fragment">Fix: adjust ranking; add fairness tests to audit set</span>
- <span class="fragment">Communicate: status page, timeline, contact</span>

<!-- Note:
- Map each role’s “first 3 actions” into this sequence.
- Capture one line per step on board. -->
  </textarea>
</section>

<section data-markdown data-separator-notes="^Note:">
  <textarea data-template>
## Metrics That Matter (pick 3)
Choose one per row:
- **Fairness**: dept coverage parity • campus balance • top-3 includes support doc
- **Transparency**: % with sources • % with explanation shown
- **Safety/Privacy**: PII leakage rate • % queries auto-redacted

Set **target + owner + review cadence**

<!-- Note:
- Force choices; avoid “measure everything”.
- Suggest monthly 30-min review. -->
  </textarea>
</section>

<section data-markdown data-separator-notes="^Note:">
  <textarea data-template>
## Roles & Lightweight Governance
- <span class="fragment">**Owner (IT product):** uptime, roadmap, changes</span>
- <span class="fragment">**DPO:** DPIA, logging/retention, DSARs</span>
- <span class="fragment">**Academic rep:** content coverage checks</span>
- <span class="fragment">**Ethics triage (2 people):** approve **High** changes</span>
- <span class="fragment">**Cadence:** 30-min monthly review</span>

<!-- Note:
- Names optional now; ensure the roles exist by next sprint. -->
  </textarea>
</section>

<section data-markdown data-separator-notes="^Note:">
  <textarea data-template>
## Two Docs Only (start here)
- **Model Card (1 page):** purpose, data, limits, metrics, change log
- **Risk Log (sheet):** feature, class (H/M/L), decision, mitigations, owner, review

<!-- Note:
- Provide templates after session (repo or handout).
- Encourage adding to capstone deliverables. -->
  </textarea>
</section>

<section data-markdown data-separator-notes="^Note:">
  <textarea data-template>
## Commitments 
Write down:
- <span class="fragment">1 policy/process change</span>
- <span class="fragment">1 metric you’ll track</span>
- <span class="fragment">1 content gap to fix</span>

Pair share (2 min)

<!-- Note:
- Ask for 2 volunteers to share one commitment each.
- Park questions for the next break. -->
  </textarea>
</section>
