# FYP2 Poster — content to lay out

A4 portrait, three columns. Build it in PowerPoint (set slide size to A4), Canva or Word,
then export as JPEG or TIFF. Keep the title large enough to read from about a metre away.

Suggested sizes: title 32–36 pt, section headings 18–20 pt, body 12–14 pt, figure captions 10 pt.

---

## TITLE BLOCK (across the top, full width)

**Adaptive Email Spam Detection Using Artificial Intelligence and Content–Metadata Fusion**

Lee Gong Yi · Supervisor: Dr Abdulrahman
Bachelor of Information Technology (Honours) Communications and Networking
Faculty of Information and Communication Technology, UTAR Kampar Campus

---

## COLUMN 1

### Introduction

Phishing remains the most common entry point for cyber intrusion, and large language models now
let attackers write fluent, error-free phishing mail at scale. Classic filters look only at what a
message says, so a well-written phishing email that avoids known trigger words passes through.

**Problem:** content-only filters miss fluent phishing; metadata-only filters miss well-formed
messages sent from correctly configured accounts; commercial filters cannot be reproduced or
audited.

### Objectives

1. Build a spam detector combining message content with structural metadata.
2. Compare classical machine-learning models and select the strongest fused configuration.
3. Evaluate against modern threats including AI-generated phishing.
4. Implement and measure a reviewed-feedback adaptation loop.

### Dataset

| Source | Emails |
|---|---|
| Merged public corpus (Enron, Ling, CEAS-2008, Nazario, Nigerian-Fraud, SpamAssassin) | 82,500 |
| After de-duplication | **81,152** |
| Held-out test split (25%) | 20,288 |
| AI-generated phishing (test only) | 4,986 |

---

## COLUMN 2

### Method

*Insert the system architecture diagram here — Figure 3.1 from the report.*

Every message is parsed as RFC 5322 and turned into two parallel feature streams:

- **Content:** word TF-IDF (1–2 grams) + character TF-IDF (3–5 grams)
- **Metadata:** 13 structural signals — URL count, sender/URL domain mismatch, reply-to
  presence, SPF, DKIM, all-caps ratio, exclamation count, suspicious terms, and others

The two streams are joined by a feature union and classified by logistic regression with
class-balanced weighting at a decision threshold of 0.55.

### Adaptation loop

Scored message → review queue → reviewer confirms or corrects → retraining on the corpus plus
corrections → candidate deployed **only if** held-out ranking quality does not drop.

*Insert a small flow diagram or the review console screenshot here.*

---

## COLUMN 3

### Results

| Metric | Value |
|---|---|
| Accuracy | **99.2%** |
| Precision / Recall / F1 | 0.991 / 0.992 / 0.992 |
| ROC-AUC | 1.000 |
| False-positive rate | 0.9% |
| Latency (CPU) | 13 ms median |

*Insert the confusion matrix — Figure 6.1.*

**Unseen AI-generated phishing:** 92% caught (4,565 of 4,986) — the model was never trained on
AI-written mail.

**Adaptation:** ROC-AUC improved from 0.810 to 0.945 after one reviewed retraining cycle, with
main-corpus accuracy maintained.

### Discussion

Fusion outperformed content alone: metadata signals such as sender/URL domain mismatch catch
structurally suspicious mail that reads perfectly. Character n-grams resist obfuscation that
defeats word-level features. The whole system runs on an ordinary CPU laptop with no cloud
service, so no email leaves the machine.

### Conclusion

A classical, explainable, locally deployable detector reaches 99.2% accuracy and generalises to
AI-generated phishing it never saw in training, while a human-gated feedback loop lets it adapt
to new campaigns without exposing the model to poisoned labels.

---

## Figures to include (pick three or four)

1. System architecture — Figure 3.1
2. Confusion matrix — Figure 6.1
3. Threshold sweep — Figure 6.2
4. Adaptation before/after — Figure 6.4
5. Review console screenshot — Figure 5.6
