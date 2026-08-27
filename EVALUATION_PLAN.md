# Model selection and defensible evaluation plan

## Decision

Use a **two-stage local ensemble**, not an AI-authorship detector as the spam decision:

1. **Current fusion baseline** — word/character TF-IDF plus header and structural metadata, logistic regression.
2. **Transformer content branch** — fine-tune `distilbert-base-uncased` on the same reviewed email corpus for `ham`, `spam`, and (where available) `phishing` labels.
3. **Fusion / policy layer** — combine transformer probability, baseline probability, authentication, URL/domain, attachment, and reputation signals. Block only on a tuned risk threshold; route ambiguous mail to quarantine/review.

A transformer is valuable for semantic social-engineering language; the metadata branch covers signals that body-only models cannot see. A downloaded community phishing checkpoint may be useful as a *baseline*, but it must not be treated as production-ready until its licence, class definition, data provenance, and performance on the held-out organization-specific test set are verified.

## Important claim boundary

Do **not** write “Gmail cannot prevent AI-generated emails” or “our model detects AI authorship, therefore it detects spam.” Gmail says it uses AI-enhanced filtering and blocks more than 99.9% of spam, phishing and malware; its actual model, telemetry, and decisions are not available for a reproducible head-to-head benchmark. [Google Safety Center](https://safety.google/intl/en_us/products/gmail/)

AI authorship is not a reliable proxy for malicious intent: legitimate messages may be AI-assisted, and a scammer can paraphrase generated text. NIST’s text challenge explicitly evaluates how generators can make text hard for discriminators to distinguish, so an authorship score must be experimental/diagnostic only, never a blocking rule. [NIST GenAI Text Challenge](https://ai-challenges.nist.gov/text-2026)

**Defensible report wording:** “On our time-separated, organization-specific evaluation set containing realistic AI-assisted phishing variants, the proposed fusion system achieved X recall at Y false-positive rate. Gmail placement was observed on the consented test mailbox subset; it is not a measurement of Gmail’s overall protection.”

## Candidate model configuration

| Component | Recommended setting | Why it is a parameter |
|---|---|---|
| Base encoder | `distilbert-base-uncased` | small English encoder (~66M parameters); use a multilingual encoder only if the corpus requires it |
| Input | `Subject: ...\nBody: ...` | preserves high-signal subject wording |
| `max_length` | 256 tokens initially; evaluate 512 | latency/coverage trade-off; report truncation rate |
| labels | `ham=0`, `spam=1`; optional separate `phishing=2` | labels must match the intervention policy |
| learning rate | `2e-5` | starting point; tune only on validation data |
| epochs | 3–5 | use early stopping on validation PR-AUC |
| batch size | 16 GPU / 4–8 CPU | hardware-dependent; use gradient accumulation if needed |
| weight decay | 0.01 | regularization |
| warm-up ratio | 0.1 | optimizer stability |
| decision threshold | selected on validation set | do not assume 0.50; choose by false-positive budget |
| baseline threshold | 0.55 (starting value) | existing model setting; validate it |
| final fusion | logistic-regression meta-model trained only on out-of-fold branch scores + metadata | avoids hand-waving and reduces leakage |

Freeze all final settings before touching the held-out test set. Record package versions, hardware, random seed, model hash, tokenization parameters, data period, and class counts.

## Evaluation protocol

### Dataset split

- Remove duplicates and near-duplicates **before** splitting.
- Split chronologically: older reviewed mail for training/validation, newest mail for test. This tests drift realistically.
- Keep campaigns, threads, sender domains, and template variants in one split where possible, preventing leakage.
- Maintain a test stratum with consented, controlled AI-assisted phishing/spear-phishing variants and a separate stratum of legitimate AI-assisted mail.
- Never send harmful links or credentials. Use inert URLs such as `https://example.invalid/` and isolated test inboxes.

### Compare three systems

1. TF-IDF + metadata baseline (already in this repository).
2. Transformer body/subject classifier.
3. Fusion model (the proposed system).

The controlled Gmail observation is a fourth *environmental observation*, not an equivalent competitor: deliver only benign, authorized test emails to isolated test accounts and record inbox/spam placement. Do not infer that a message was “missed” without checking delivery status and policies.

### Report metrics

Spam datasets are often imbalanced, so accuracy alone is inadequate. Report all metrics with 95% bootstrap confidence intervals:

- phishing/spam recall (security catch rate);
- precision and false-positive rate (legitimate mail wrongly blocked);
- PR-AUC and ROC-AUC;
- F1 only as a secondary summary;
- recall at a fixed false-positive rate, e.g. 0.1% or the organization’s approved budget;
- p50/p95 end-to-end latency, CPU/GPU, model size, and throughput (emails/second);
- calibration: Brier score and reliability plot.

Break results down by language, message length, new/known sender, authentication state, AI-assisted malicious variant, and legitimate AI-assisted mail. Publish errors and limitations, not only the best number.

## AI-assisted-email experiment

The actual security hypothesis is: **“Can semantic and structural features recognize malicious intent when grammar and fluency are high?”**

Create controlled variants from known phishing templates using several generators and prompts, then have a reviewer verify that the malicious request and technical indicators remain. Include human-written phishing and legitimate AI-assisted operational emails. Label the task by **maliciousness**, separately recording `authorship_source` as human / AI-assisted / unknown. Evaluate whether recall holds across source; do not train and test on paraphrases of the same template.

## Success criteria to set before training

Choose values with the project supervisor or security owner, for example:

- Fusion recall is higher than either branch at the pre-declared 0.1% false-positive threshold.
- Fusion p95 local inference latency remains below the deployment budget.
- Performance does not materially fall for the AI-assisted malicious test stratum.
- Legitimate AI-assisted mail does not have a materially higher false-positive rate than human-authored legitimate mail.

If any criterion fails, report the limitation rather than changing the evaluation set after seeing results.
