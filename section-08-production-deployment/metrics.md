### **Accuracy**

* **What it is:**
  The percentage of predictions that are *exactly correct*.
* **Where it’s used:**
  Classification tasks (e.g. “is this spam?” → correct/incorrect).
* **Limitations:**
  Doesn’t capture “partial correctness” in text generation (e.g. if most of an answer is right but one fact is wrong).

---

### **Perplexity**

* **What it is:**
  A measure of how well a probability model predicts text.
  Mathematically, it’s the **exponential of the average negative log-likelihood** of the true sequence.
* **Interpretation:**
  Lower perplexity = the model finds the sequence *less surprising* → better language modeling.
* **Where it’s used:**
  Evaluating how fluently a model predicts text sequences.
* **Analogy:**
  If you’re reading a book in your native language, your “perplexity” is low because you can easily predict the next word. In an unfamiliar language, your “perplexity” is high.

---

### **BLEU (Bilingual Evaluation Understudy)**

* **What it is:**
  An automatic metric for comparing a machine-generated text to one or more reference texts.
* **How it works:**
  Looks at **n-gram overlap** (short word sequences like “student support”).
* **Typical use case:**
  Machine translation quality.
* **Scale:**
  0 to 1 (or 0 to 100). Higher is better.
* **Limitation:**
  Penalises creative paraphrasing — if the wording is different but still correct, BLEU may score it low.

---

### **ROUGE (Recall-Oriented Understudy for Gisting Evaluation)**

* **What it is:**
  A family of metrics for text summarisation and generation.
* **How it works:**
  Measures **overlap** between system output and reference summaries:

  * **ROUGE-N:** n-gram recall.
  * **ROUGE-L:** longest common subsequence.
* **Focus:**
  Recall-oriented → how much of the reference text was captured.
* **Limitation:**
  Doesn’t measure factual accuracy or fluency, only overlap.

---

📌 **Quick Comparison Table**

| Metric     | Measures                        | Typical Use Case     | Limitation                         |
| ---------- | ------------------------------- | -------------------- | ---------------------------------- |
| Accuracy   | % exactly correct predictions   | Classification tasks | Too rigid for free-form text       |
| Perplexity | Surprise/unexpectedness in text | Language modelling   | Doesn’t measure meaning or utility |
| BLEU       | n-gram precision vs references  | Machine translation  | Penalises paraphrasing             |
| ROUGE      | n-gram recall vs references     | Summarisation        | Ignores factuality & fluency       |
