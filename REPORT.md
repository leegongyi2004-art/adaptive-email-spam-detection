# [SUPERSEDED] Use REPORT_FYP2.md for the UTAR FYP2 report.
This is an earlier generic draft kept only for reference; all official content lives in REPORT_FYP2.md.

# Adaptive Email Spam Detection using AI and Content–Metadata Fusion

> **FYP2 report draft.** Copy the chapters into your faculty's template, add your
> name/ID/supervisor on the cover page, and replace any `[…]` placeholders. Every
> number below comes from commands you actually ran, so you can defend them in the viva.

## Abstract

Email remains a primary channel for phishing and social-engineering attacks, and
large language models (LLMs) have lowered the effort needed to write polished,
convincing fraudulent messages. This project builds a local, open-source **adaptive
email spam detector** that fuses two complementary views of a message: its **text
content** (word and character patterns) and its **structural metadata** (links,
sender/link domain mismatch, reply-to headers, SPF/DKIM, urgency signals). A
class-balanced logistic-regression classifier is trained on 81,152 reviewed public
emails and achieves **99.2% accuracy** (F1 0.992, ROC-AUC 1.000) on a held-out test
split, scoring each message in roughly **11–16 ms on a CPU**. On a separate set of
modern, AI-style phishing and business-email-compromise (BEC) messages, one cycle of
the system's **adaptive retraining on reviewed feedback** raised detection ranking
(ROC-AUC) from 0.81 to 0.945 and increased phishing recall at a near-zero false-positive
operating point from 20% to 85%. The system is served through a REST API with a
review/feedback console and can be integrated with a live mailbox through automation.
The detector identifies **phishing intent**, not AI authorship; claims about AI-generated
mail are framed accordingly.

---

## Chapter 1 — Introduction

### 1.1 Background
Email filters are a long-standing security control, but attacks continue to evolve.
Two trends motivate this project: (1) phishing and business-email-compromise (BEC)
attacks increasingly use calm, professional language with few classic "spam" signals;
and (2) generative AI lets attackers produce fluent, personalised, typo-free fraudulent
messages at scale. A detector that relies only on a fixed keyword list or only on
message text is therefore brittle.

### 1.2 Problem statement
A practical detector should (a) combine what a message *says* (content) with how it is
*structured* (metadata), (b) remain fast and explainable enough to run on ordinary
hardware, and (c) **adapt** as new campaigns appear, rather than being rewritten by hand.

### 1.3 Objectives
1. Build a content–metadata fusion spam/phishing classifier using machine learning.
2. Train and evaluate it on a large, labelled public email corpus.
3. Measure detection of modern, AI-assisted-style phishing and link-less BEC mail.
4. Implement an **adaptive loop**: human-reviewed corrections are used to retrain the
   model, and show that accuracy on new threats improves.
5. Deploy the model as a service (REST API + review console) and document integration
   with a live mailbox.

### 1.4 Scope
- English-language email; local/offline operation; no private/employee data is used.
- The core model is classical machine learning (TF-IDF + logistic regression). A
  deep-learning transformer branch (DistilBERT) is designed and provided as an optional
  GPU upgrade path.
- The model classifies **phishing/spam intent**. It does not claim to detect whether a
  message was written by an AI (see §5.3).

### 1.5 Report structure
Chapter 2 reviews related work; Chapter 3 describes the data, features, model and
adaptive design; Chapter 4 presents results; Chapter 5 concludes and lists future work.

---

## Chapter 2 — Literature Review

- **Spam detection approaches.** Early filters used hand-written rules (SpamAssassin);
  modern systems use statistical and machine-learning classifiers over text features.
  Linear models over TF-IDF features remain a strong, fast, explainable baseline and are
  widely used in production mail pipelines.
- **Content vs metadata.** Text models capture wording; structural signals (sender/link
  domain mismatch, reply-to, SPF/DKIM, attachments) capture attacks that use innocuous
  language. Fusing the two is more robust than either alone.
- **Deep learning.** Transformer models such as DistilBERT/BERT model context and
  paraphrase. Published multi-dataset studies report BERT-family accuracy around
  99% on the same public corpora used here (e.g. ~99.7% F1 on CEAS-08 with DistilBERT),
  at higher compute cost. This project positions the transformer as an optional branch.
- **AI-generated phishing is a real, measured threat.** A 2025 study used LLMs to
  generate phishing that evaded a campus network's existing filters (~99% evasion), and
  then showed that a machine-learning detector trained on an ordinary phishing dataset
  detected ~99.9% of those LLM-generated emails (Phish-Master, *Applied Sciences*, 2025,
  https://www.mdpi.com/2076-3417/15/22/12203). This supports this project's approach:
  a well-trained fusion model can generalise to AI-assisted phishing without needing a
  special "AI detector".
- **Business Email Compromise (BEC).** Link-less scams that impersonate executives or
  finance staff are among the hardest cases because they contain no malicious URL.
  Public BEC data is scarce; the BEC-2 dataset (279 LLM-generated BEC emails) is the
  first public corpus of its kind (Springer, 2025,
  https://link.springer.com/article/10.1007/s11416-024-00544-y).
- **Commercial filters (e.g. Gmail).** Google states its AI-enhanced filtering blocks
  more than 99.9% of spam/phishing/malware (Google Safety Center,
  https://safety.google/intl/en_us/products/gmail/). Commercial models are proprietary
  and continuously updated, so they cannot be benchmarked offline; any comparison must
  be a controlled, authorised black-box test (see §4.6), not an overall claim of
  superiority.
- **AI-authorship detection is unreliable.** Evaluations of AI-text detectors show high
  error rates (e.g. the NIST Generative AI Text Challenge,
  https://ai-challenges.nist.gov/text-2026). This project therefore detects malicious
  *intent*, not AI authorship.

---

## Chapter 3 — Methodology

### 3.1 System architecture
```
                 incoming email (.eml / API / mailbox watcher)
                                      │
                    ┌─────────────────┴─────────────────┐
                    │        feature extraction          │
                    │  content: word + char TF-IDF       │
                    │  metadata: 12 structural signals   │
                    └─────────────────┬─────────────────┘
                                      │
                    class-balanced logistic regression
                                      │
                         spam probability + signals
                                      │
                 label / quarantine (action) ──► review queue
                                      │
              human corrections (feedback console / CSV)
                                      │
                    scheduled retrain (adaptation) ──► redeploy
```

### 3.2 Datasets
- **Training corpus:** the public "Phishing Email Dataset" (Kaggle; CC BY-SA 4.0), which
  merges six established corpora: **Enron, Ling-Spam, SpamAssassin** (mostly legitimate)
  and **CEAS-2008, Nazario, Nigerian-Fraud** (phishing/fraud). After de-duplication:
  **81,152 unique emails = 39,234 legitimate + 41,918 spam/phishing.**
- **Split:** 75% train / 25% held-out test (stratified). The test quarter is never used
  for training or threshold selection.
- **External test sets (never trained on for the headline number):**
  - a synthetic **modern-threat** set of AI-style phishing, link-less BEC and adversarial
    legitimate mail (`modern_test.csv`, 30 emails), with a separate, disjoint reviewed
    batch (`modern_feedback.csv`) used only for adaptation;
  - the University of Twente phishing-validation set (2,000 rows / 100 unique templates),
    used as a small secondary sanity check.

### 3.3 Features
- **Content:** word unigrams/bigrams and character n-grams (3–5) via TF-IDF, which also
  tolerates obfuscation such as spaced-out words.
- **Metadata (12 signals):** URL count, unique link domains, attachment count,
  sender-has-domain, **sender-domain vs link-domain mismatch**, reply-to present,
  SPF pass, DKIM present, subject/body length, ALL-CAPS ratio, exclamation count, and a
  count of urgency/verification terms.
- Metadata features are standardised so raw lengths do not dominate the text features.

### 3.4 Model
A scikit-learn `FeatureUnion` fuses the content and metadata branches into a
**class-balanced logistic regression** (`class_weight="balanced"`, `C=1.5`). It outputs a
calibrated-style spam probability; a threshold (default 0.55) converts it to a label.
The model is explainable (each decision reports which metadata signals fired) and trains
in minutes on a CPU.

### 3.5 Adaptive loop (the "adaptive" part)
The system does **not** learn unsupervised (which would let attackers poison it). It
adapts the way large providers do: reviewed labels drive scheduled retraining.
1. The model scores mail; uncertain/quarantined/missed messages are collected in a review
   queue with the predicted label.
2. A reviewer marks mistakes (spam/ham) — equivalent to "Report spam"/"Not spam".
3. Corrections are appended to a feedback dataset.
4. A scheduled retrain refits on the original corpus **plus** the reviewed batch, and the
   new model is redeployed.
A live demonstration (`demo_adaptive.py`) shows a brand-new scam campaign going from
0/6 caught to 5/6 caught after one reviewed retraining cycle, with legitimate mail
unaffected.

### 3.6 Deployment and integration
- A **FastAPI** service exposes `POST /predict` (label, probability, signals) and a
  browser review console with "Correct / Actually spam / Actually legitimate" buttons that
  write the feedback dataset.
- A **mailbox watcher** scans a folder of `.eml` files (as a mail server would deliver),
  logs predictions, and can quarantine spam.
- Integration with a live Gmail/IMAP mailbox is documented with the open-source
  automation tool **n8n** (new-mail trigger → call `/predict` → label/quarantine), in
  `INTEGRATION_n8n.md`.

### 3.7 Evaluation metrics and design
- Accuracy, precision, recall, F1 and ROC-AUC on the held-out split.
- **Confusion matrix / false-positive rate**, because in email filtering a legitimate
  message wrongly sent to spam is the most costly error.
- **Threshold sweep and recall at a low false-positive rate (≤5%)**, which is the
  operationally meaningful operating point (the default 0.55 threshold is not assumed
  optimal for every mail distribution).
- Per-message latency (p50/p95) on CPU.
- External generalisation tests on modern/AI-style and BEC mail, plus an before/after
  adaptation comparison on the same held-out set.

---

## Chapter 4 — Results and Evaluation

### 4.1 Main held-out results (81k corpus)
Trained on 60,864 emails, tested on 20,288 unseen emails (51.7% spam):

| Metric | Value |
|---|---|
| Accuracy | **0.992** |
| Precision | 0.991 |
| Recall | 0.992 |
| F1 | 0.992 |
| ROC-AUC | 1.000 |
| Latency | p50 16.4 ms / p95 41.3 ms per email (CPU) |

Confusion matrix: **10,399** phishing caught, **80** missed; **9,719** legitimate
passed, **90** wrongly flagged (false-positive rate ≈ **0.9%**).

These agree with published results on the same public corpora (BERT-family systems
report ~99%), confirming the implementation is sound.

### 4.2 Detection of modern, AI-style phishing and BEC
On the held-out modern-threat set (polished, typo-free phishing, link-less BEC, and
adversarial legitimate mail), the original model ranked threats well but was miscalibrated
for that distribution at the default threshold — illustrating why the operating threshold
is tuned per deployment.

A separate 12-email qualitative demo (`test_ai_phishing.py`) had the trained model flag
**6/6 modern AI-style phishing** emails (including a no-link CEO wire-fraud BEC), with one
legitimate parcel-delivery email flagged — a false alarm used to motivate both the
metadata/threshold handling and the optional transformer.

### 4.2b Detection of genuine LLM-generated phishing
To test generalisation to real AI-written mail, the baseline model (trained **only** on the
conventional 81k corpus) was scored on **4,986 phishing emails generated by GPT-4.1,
DeepSeek 3.2 and LLaMA 3.3** (the public cross-model LLM-phishing corpus, Zenodo
[https://zenodo.org/records/20250116](https://zenodo.org/records/20250116)) — none of which
it had seen in training. At a low-threshold operating point it caught **92% (4,565/4,986)**,
and 84% at the default 0.55 threshold, at ~11 ms/email. This shows a conventional
content–metadata model **generalises strongly to AI-assisted phishing without any
AI-specific training**, consistent with published work (Phish-Master reported ~99.9%).
The catch rate falls as the decision threshold is raised (26% at 0.98), indicating the model
is systematically *less confident* on LLM-written mail than on classic phishing — evidence
that AI-assisted messages are harder for a text classifier and a motivation for adaptive
retraining and the transformer branch. (This set is phishing-only, so it measures recall;
false-positive rate is assessed on the legitimate-containing sets above.)

### 4.3 Adaptive improvement (before vs after reviewed retraining)
Model v2 was retrained on the original corpus **plus 404 reviewed modern examples**
(disjoint from the test set). Tested on the same held-out modern set:

| Metric on modern threat set | v1 (baseline) | v2 (after adaptation) |
|---|---|---|
| ROC-AUC | 0.81 | **0.945** |
| Phishing recall at ≤5% false positives | 20% (4/20) | **85% (17/20)** |
| False positives at that operating point | high | **0/10 legitimate** |
| Main-corpus accuracy (regression check) | 0.992 | **0.991** (unchanged) |

**Interpretation:** one adaptive cycle substantially improved detection of the new,
AI-style/BEC campaigns represented in the reviewed feedback while preserving normal-mail
accuracy — the system measurably *adapts* from reviewed feedback. On the independent,
genuine-LLM corpus (§4.2b) the same synthetic-feedback model performed comparably to the
baseline (~92% vs ~92%), which is expected: adaptation most improves the threat types
actually present in the reviewed batch. In production, reviewed examples of the real new
campaign are folded into the next retraining cycle; the system improves on threats it has
received labelled feedback for, rather than by unsupervised guessing. (The synthetic sets
are an illustrative, controlled benchmark; the 81k result in §4.1 and the LLM recall in
§4.2b are the primary figures.)

### 4.4 Speed
The model scores an email in ~11–16 ms median on a modest CPU (tens of emails/second),
comfortably real-time for a mail pipeline. No GPU is required for the baseline.

### 4.5 Threats to validity (state these — they strengthen the report)
- The 99.2% figure is from a held-out split of a combined public corpus; phishing and
  legitimate mail come from stylistically different sources, so real-organisation results
  may differ and should be measured before deployment.
- Body-only external emails cannot exercise header metadata (sender/SPF); real incoming
  mail includes headers and is expected to score better.
- The synthetic modern sets demonstrate behaviour in a controlled way; they are not a
  census of all real AI-generated mail.

### 4.6 Comparison with commercial filters (Gmail)
Gmail's model is proprietary and cannot be benchmarked offline; Google reports blocking
>99.9% of spam/phishing/malware. A fair comparison would be a **controlled, authorised
  black-box test**: run the same fixed labelled set (including AI-style/BEC samples)
  through both this model and a disposable test Gmail account, and compare confusion
  matrices. This should be done only with supervisor approval and is framed as a test on
  a controlled subset — **not** a claim that this system is overall better than Gmail.
  This project's demonstrated advantages are transparency (visible signals), local/offline
  operation, low latency, and an explicit, controllable adaptation loop.

---

## Chapter 5 — Conclusion and Future Work

### 5.1 Conclusion
The project delivers a complete, working **adaptive email spam detector using AI and
content–metadata fusion**. It reaches 99.2% accuracy on a large public benchmark, runs in
milliseconds on a CPU, flags modern AI-assisted-style phishing and link-less BEC, and
measurably improves on new threats after a single reviewed retraining cycle — while
keeping false positives low and reporting the signals behind each decision.

### 5.2 Future work
1. **Deep-learning branch:** fine-tune DistilBERT on a GPU (a ready-to-run Google Colab
   notebook is provided) and fuse its semantic score with the metadata-aware baseline,
   which should further reduce false alarms on adversarial-but-legitimate mail.
2. **Live deployment:** connect the API to a real mailbox via n8n / a mail-transfer agent,
   with quarantine and a reviewer dashboard.
3. **Controlled Gmail comparison** on a disposable account (with approval).
4. **Closed-loop adaptation on real AI phishing:** periodically retrain on reviewed
   genuine-LLM phishing (the correct feedback for that threat), which the split-feedback
   experiment shows lifts detection beyond the ~92% out-of-the-box figure.
5. Periodic scheduled retraining and drift monitoring as the production adaptation loop.

### 5.3 Important limitation on "AI-generated" claims
The system detects **phishing/spam intent**, including in fluent, AI-assisted-style
messages. It does **not** identify whether an email was authored by an AI; independent
evaluations show AI-text detection is unreliable. The correct claim is that the model
catches fraudulent mail regardless of how it was written.

---

## References (examples — format to your faculty's style)
1. Phishing Email Dataset (Enron/Ling/SpamAssassin/CEAS/Nazario/Nigerian-Fraud), Kaggle, CC BY-SA 4.0.
2. Phish-Master: Leveraging Large Language Models for Advanced Phishing Email Generation and Detection, *Applied Sciences* 15(22):12203, 2025. https://www.mdpi.com/2076-3417/15/22/12203
3. In-Depth Analysis of Phishing Email Detection: ML vs DL across datasets, *Applied Sciences* 15(6):3396, 2025. https://www.mdpi.com/2076-3417/15/6/3396
4. Building a Business Email Compromise research dataset with LLMs (BEC-2), *Journal of Cyber Security*, 2025. https://link.springer.com/article/10.1007/s11416-024-00544-y
5. Google Safety Center — Gmail security. https://safety.google/intl/en_us/products/gmail/
6. NIST Generative AI Text Challenge (AI-text detection reliability). https://ai-challenges.nist.gov/text-2026
7. University of Twente Phishing Validation Emails dataset, Zenodo, 2024. https://zenodo.org/records/13474746
8. Cross-model evaluation of phishing detectors against LLM-generated emails (5,000 human + 4,986 GPT-4.1/DeepSeek 3.2/LLaMA 3.3 phishing), Zenodo, 2026. https://zenodo.org/records/20250116
9. scikit-learn (Pedregosa et al.), FastAPI, and DistilBERT (Sanh et al., 2019) documentation.
