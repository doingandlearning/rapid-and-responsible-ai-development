# From RNNs to Transformers: A Curated Reading Path

This handout will help you deepen your understanding of how transformer models evolved from earlier sequence models like RNNs and LSTMs, why they were a breakthrough, and how they continue to develop.

---

## 1. Sequence Models: RNNs & LSTMs
**Goal:** Understand how we first handled sequences.

- 📖 [Understanding LSTM Networks – Chris Olah](https://colah.github.io/posts/2015-08-Understanding-LSTMs/)  
- 📖 *Deep Learning* (Goodfellow et al.) – Chapter 10 covers RNNs and LSTMs.  

**Takeaway:** RNNs introduced temporal memory but struggled with long-range context and training stability.

---

## 2. The Limits of RNNs
**Goal:** Recognise why we needed something better.

- 📖 [Stanford CS224n Lecture Notes (2019)](http://web.stanford.edu/class/cs224n/) – see sequence models section.  

**Takeaway:** RNNs/LSTMs are sequential, slow to train, and still weak at long dependencies.

---

## 3. Attention Mechanisms
**Goal:** Discover the breakthrough idea before transformers.

- 📄 [Neural Machine Translation by Jointly Learning to Align and Translate (Bahdanau et al., 2014)](https://arxiv.org/abs/1409.0473)  
- 📖 [The Illustrated Attention Mechanism – Lilian Weng](https://lilianweng.github.io/posts/2018-06-24-attention/)  

**Takeaway:** Attention allows models to selectively focus on relevant parts of the sequence.

---

## 4. Transformers: The Breakthrough
**Goal:** Learn how attention replaced recurrence.

- 📄 [Attention Is All You Need (Vaswani et al., 2017)](https://arxiv.org/abs/1706.03762)  
- 📖 [The Illustrated Transformer – Jay Alammar](http://jalammar.github.io/illustrated-transformer/)  
- 💻 [The Annotated Transformer (Harvard NLP)](http://nlp.seas.harvard.edu/annotated-transformer/)  

**Takeaway:** Transformers use self-attention and parallelism to handle long-range dependencies efficiently.

---

## 5. Interactive Simulation
**Goal:** Explore how transformers work step by step.

- 🕹️ [Transformer Visualisation – Harvard NLP](http://nlp.seas.harvard.edu/annotated-transformer/) (interactive elements)  
- 🕹️ [The Transformer from Scratch – Peter Bloem](http://peterbloem.nl/blog/transformers)  
- 🕹️ [Attention Playground – Distill.pub](https://distill.pub/2016/augmented-rnns/#attention)  

**Takeaway:** These tools let you see attention weights and token interactions in real time.

---

## 6. Transformer Variants
**Goal:** See how the architecture evolved for different use cases.

- 📄 [BERT: Pre-training of Deep Bidirectional Transformers (Devlin et al., 2018)](https://arxiv.org/abs/1810.04805)  
- 📄 [Language Models are Unsupervised Multitask Learners (GPT-2 paper, Radford et al.)](https://cdn.openai.com/better-language-models/language_models_are_unsupervised_multitask_learners.pdf)  
- 📖 [The Illustrated BERT, ELMo, and co. – Jay Alammar](http://jalammar.github.io/illustrated-bert/)  

**Takeaway:** Same building blocks (attention + feed-forward layers), but adapted:  
- Encoder-only (BERT) → understanding  
- Decoder-only (GPT) → generation  
- Encoder-decoder (T5/BART) → flexible seq2seq

---

## 7. Scaling & Efficiency
**Goal:** Understand why modern models (GPT-4, LLaMA, etc.) are possible.

- 📄 [Scaling Laws for Neural Language Models (Kaplan et al., 2020)](https://arxiv.org/abs/2001.08361)  
- 📖 [Efficient Transformers – HuggingFace Blog](https://huggingface.co/blog/efficient-transformers)  

**Takeaway:** Performance improves predictably with more data/parameters — but efficiency tricks are essential.

---

## 8. Hands-On Practice
**Goal:** Move from reading to experimenting.

- 💻 [HuggingFace Transformers Course](https://huggingface.co/course/chapter1)  
- 💻 [Papers with Code – Transformers Collection](https://paperswithcode.com/method/transformer)  

**Takeaway:** Build, fine-tune, and experiment with real transformer models.

---

## Key Takeaways
- RNNs introduced memory → LSTMs improved it → but both struggled with long-range dependencies.  
- Attention let models “look anywhere” in the sequence → a paradigm shift.  
- Transformers unlocked parallelism and scale → foundation for today’s LLMs.  
- Modern progress = scaling + efficiency + variants (BERT, GPT, T5, etc.).  
- You learn best by combining **theory + visualisation + code**.

---
