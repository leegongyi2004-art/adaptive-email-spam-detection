# PASTE-READY FIXES FOR YOUR SUBMISSION DOCUMENT

Everything below is final text. Copy each block into Word at the place named.
Nothing here touches figure/table caption numbering — you said you are handling that yourself.

Order of work (fastest first):

1. FIX 1 — heading prefixes (30 seconds)
2. FIX 2 — find/replace the stale numbers (2 minutes)
3. FIX 3 — Table 4.2 (1 minute)
4. FIX 4 — paste the missing Section 2.1 (biggest, about 5 minutes)
5. FIX 5 — paste the missing 6.5 and 7.2 and the corrected 6.2.3 / 6.2.4 / 7.1
6. FIX 6 — optional: replace 5.3 and 5.4 with the current versions

---

## FIX 1 — Stray chapter prefixes on three headings

Delete the prefix so the headings read exactly:

| Currently in your document | Change to |
|---|---|
| Chapter 6 6.2 Testing Setup and Result | 6.2 Testing Setup and Result |
| Chapter 7 7.1 Conclusion | 7.1 Conclusion |
| Chapter 8 7.2 Recommendation | 7.3 Recommendation |

Note the last one becomes **7.3**, not 7.2, because 7.2 is the Limitations section you are
adding in FIX 5e.

---

## FIX 2 — Stale numbers (Word: Ctrl+H, Find and Replace)

| Find | Replace with | Where it appears |
|---|---|---|
| 16 milliseconds | 13 milliseconds | Section 5.1, Section 6.2.5, Section 7.1 |
| 16 ms | 13 ms | Table 6.1, Table 6.6 |
| 41 ms | 33 ms | Table 6.1 |
| 11 milliseconds | 13 milliseconds | Section 6.2.3 |

Then fix the adaptation claim by hand. Anywhere the document says recall rose from
**20% to 85%**, that is wrong. The measured result is that recall was **maintained at 95%**
while ROC-AUC rose from 0.810 to 0.945. Corrected wording is in FIX 5b.

Correct values, for reference:

| Quantity | Correct value |
|---|---|
| Corpus after de-duplication | 81,152 emails |
| Held-out test split | 20,288 emails |
| Accuracy / Precision / Recall / F1 | 0.992 / 0.991 / 0.992 / 0.992 |
| ROC-AUC | 1.000 |
| Confusion matrix | TP 10,399; FN 80; TN 9,719; FP 90 |
| False-positive rate | 0.9% |
| Latency | p50 13 ms; p95 33 ms |
| LLM-phishing catch | 92% at low threshold; 84% at 0.55 |
| Adaptation | ROC-AUC 0.810 to 0.945; recall 95% to 95% |

---

## FIX 3 — Table 4.2 must list THIRTEEN signals

Your version has 12 because "Exclamation count" was merged into "Urgency markers".
Replace the whole of Section 4.3 with this block.


## 4.3 Data and Feature Design

The thirteen structural metadata signals are defined in Table 4.2.

**Table 4.2 — The thirteen structural metadata signals.**

| Signal | Meaning / rationale |
|---|---|
| Subject length | Phishing often uses unusually short or long subjects. |
| Body length | Length of the body in characters. |
| Number of links | Count of URLs in the body. |
| Distinct link domains | Number of different domains linked; many distinct domains suggest bulk campaigns. |
| Number of attachments | Count of attached files. |
| Sender has a domain | Whether the sender address contained a usable domain. |
| Sender–link domain mismatch | The sender's domain was absent from the body's link domains — a classic phishing signal. |
| Reply-To present | Whether a Reply-To header was present (a possible redirect of replies). |
| SPF authentication result | Whether a sender-policy-framework pass was indicated in the authentication headers. |
| DKIM signature present | Whether a DomainKeys-Identified-Mail signature header was present. |
| Capitals ratio in subject | Fraction of upper-case letters in the subject line. |
| Exclamation count | Number of exclamation marks in the subject and body. |
| Urgency term count | Number of urgent or verification-related terms (eleven-term list) found in the subject and body. |

The subject and body were concatenated into a single content string so that both parts were
represented in the text features. For plain-text inputs without headers (such as the body-only
external sets), the parser treated the whole input as the body and set the header-derived
signals to neutral values, preserving the feature-vector structure. Once trained, the model was
saved to a single file so that the service and the mailbox watcher loaded an identical
predictor. Keeping the metadata to thirteen signals deliberately avoided a large, fragile
handcrafted rule
set: unlike a keyword blocklist, each signal contributed a numeric feature whose weight was
learned by the classifier rather than maintained by hand, satisfying the objective of an
adaptive, learning-based system rather than a static rule engine.

---

## FIX 4 — Chapter 2 is missing all of Section 2.1

Your Chapter 2 jumps straight to 2.2, but your own 2.3 Summary refers back to the technologies
review. Paste this block immediately after the Chapter 2 heading, before 2.2.


## 2.1 Review of the Technologies

### 2.1.1 Hardware Platform

The project was deliberately designed to run on commodity hardware. Development and evaluation
were performed on a consumer laptop running Windows 11, powered by an Intel-class central
processing unit with integrated Intel UHD graphics and no discrete graphics processing unit.
This constraint was treated as a design requirement: a detector that ran comfortably on a
central processing unit could be deployed widely, embedded in mail automation, and reproduced
by other researchers without specialist infrastructure.

### 2.1.2 Firmware / Operating System

All core components were written in Python and were developed and tested on Windows 11. No
special firmware was required, and no hardware programming was involved. The operating system
served only as the host for the Python runtime, the virtual environment and the local file
storage used for email and model artefacts.

### 2.1.3 Database

No database server was deployed. Emails, labels and reviewed feedback were stored as
comma-separated-value files, and the trained model was serialised to disk with Joblib. This
choice followed the lightweight, script-based design of the system, kept
the system portable and easy to back up, and avoided the operational overhead of a database for
a dataset processed in batch. The comma-separated-value format also allowed the public corpora
to be merged and de-duplicated with simple, auditable scripts.

### 2.1.4 Programming Language and Libraries

Python (3.11+) was used as the primary programming language for all pipeline stages. The
principal library was scikit-learn for feature extraction and classification — including
TF-IDF vectorisation, dictionary vectorisation of metadata, feature union, standardisation,
logistic regression, multinomial Naïve Bayes and the linear support-vector classifier — and
Joblib for model persistence [15]. The service layer used FastAPI with Uvicorn as the
application server and Pydantic for request validation. Standard-library modules (`email`, `re`,
`csv`, `pathlib`) handled message parsing, regular-expression extraction and file handling.

### 2.1.5 Algorithms

Five algorithmic families were relevant. **Term frequency–inverse document frequency**
weighted terms by how often they appeared in a message and how rare they were across the
corpus; word unigrams and bigrams captured phrasing, while character n-grams of length three
to five tolerated obfuscation such as spaced or misspelled words. **Multinomial Naïve Bayes**
applied Bayes' theorem with a conditional-independence assumption to provide a fast generative
baseline; it remained a competitive, efficient method for text classification and had been
shown to reach high accuracy when paired with sound preprocessing [3], [8]. **Logistic
regression** modelled the log-odds of spam as a linear function of the features passed through
a sigmoid, producing a probability estimate and interpretable coefficients. **Linear
support vector machines** found a maximum-margin separating hyperplane and provided a strong
discriminative baseline for high-dimensional text. **Standardisation** was applied to metadata
features so that raw lengths could not dominate the normalised text features.

Comprehensive reviews of machine learning for spam filtering confirmed that learned models
consistently outperformed manually engineered rule systems, and that hybrid combinations of
feature sources were among the most robust approaches [4], [5]. Recent comparative studies across
many classical classifiers further showed that models such as random forests and support vector
machines reached the high-nineties in accuracy on public phishing and spam corpora [6], [7].
The choice of logistic regression as the deployed classifier reflected three practical
requirements: it produced a genuine probability that could be compared against an adjustable
threshold, it accepted balanced class weighting to compensate for the ham/spam ratio, and its
linear coefficients allowed the contribution of each feature to be inspected, supporting the
explainability requirement. Naïve Bayes and the linear support vector machine were retained as
comparators because together they spanned the generative-to-discriminative spectrum, with Naïve
Bayes a generative baseline and the support vector machine a maximum-margin discriminative one.

### 2.1.6 Summary of the Technologies Review

A Python and scikit-learn stack provided a fast, explainable and reproducible detector on
commodity central-processing-unit hardware, with comma-separated-value storage and Joblib
persistence keeping the system portable and free of any special hardware dependency.

---

## FIX 5 — Missing and corrected results / conclusion sections

### 5a. Replace Section 6.2.3 (fixes the 11 ms figure)


### 6.2.3 Detection of Genuine LLM-Generated Phishing

The detector was tested on 4,986 phishing emails generated by GPT-4.1, DeepSeek 3.2 and
LLaMA 3.3 — an external set the model was never trained on. The baseline detector caught 92%
(4,565/4,986) at a low-threshold operating point and 84% at the default 0.55 threshold, at
roughly 13 milliseconds per email. Table 6.3 summarises the result.

**Table 6.3 — Detection of genuine LLM-generated phishing (n = 4,986).**

| Operating threshold | Emails caught | Catch rate |
|---|---|---|
| Low threshold (favour recall) | 4,565 / 4,986 | **92%** |
| Default 0.55 | ≈ 4,188 / 4,986 | 84% |

The catch rate fell as the threshold rose, showing that the model was systematically less
confident on large-language-model-written mail than on classic phishing — evidence that
AI-assisted messages were harder, and a direct motivation for the adaptive retraining
mechanism. The result was consistent with recent research in which a conventionally trained
detector still caught the large majority of AI-generated phishing [12]. The decline of catch
rate with the decision threshold is plotted in Figure 6.3.

[FIGURE 6.3: Catch rate versus decision threshold on the LLM-phishing set.]

### 5b. Replace Section 6.2.4 (fixes the "20% to 85%" claim)


### 6.2.4 Adaptive Improvement (Objective 4)

After retraining on a disjoint, reviewed batch of modern AI-style and
business-email-compromise emails, detection ranking on a held-out modern-threat set improved
from ROC-AUC 0.81 to 0.945, a 16.7% relative improvement in ranking quality, while phishing recall at the default 0.55
threshold was maintained at 95% and main-corpus accuracy was maintained at 0.991. Table 6.4
summarises the change; in a controlled before/after demonstration on a held-out new campaign,
the number of campaign messages caught rose from 0 out of 6 before retraining to 5 out of 6 after
a single reviewed retraining cycle.

**Table 6.4 — Before/after one adaptive retraining cycle on held-out modern-threat email.**

| Measure | Before retraining | After retraining |
|---|---|---|
| ROC-AUC (modern set) | 0.81 | **0.945** |
| Phishing recall at threshold 0.55 | 95% | **95%** |
| Main-corpus accuracy | 0.991 | 0.991 (maintained) |
| Demo campaign caught (held-out set) | 0 / 6 | 5 / 6 |

The improvement was greatest for threat types actually represented in the reviewed feedback;
this scope was reported honestly rather than claiming universal adaptation. The same before/after
comparison was also applied to a second, independent held-out set, on which the baseline detector
was already close to its ceiling at ROC-AUC 0.965 and 100% recall. After the same retraining
cycle, recall on that set remained at 100% while ROC-AUC moved slightly to 0.951. Adaptation
therefore did not improve a set on which there was effectively no headroom to gain, and the
small change in ranking quality is within the variation expected from refitting on a marginally
different training sample. This outcome is reported because it delimits the claim: reviewed
feedback improves detection for threat families the baseline handles poorly, and neither
improves nor materially harms performance where the baseline is already near-perfect. The retraining
cycle was run as a scheduled batch step, and the retrained model was evaluated on the held-out
data before further use, confirming that main-corpus accuracy was maintained while the target
threat ranking improved. Retraining in controlled batches rather than continuously distinguished
the system from both a static model and an uncontrolled online-learning loop. The improvement
in ranking is visualised by the two ROC curves, before and after retraining, in Figure 6.4.

[FIGURE 6.4: ROC curves before and after one adaptive retraining cycle.]

### 5c. Add Section 6.5 Concluding Remark (missing entirely) at the end of Chapter 6


## 6.5 Concluding Remark

All four objectives were met with a fast, explainable and adaptive system. The fused detector
matched strong published results on the public corpus, generalised to previously unseen
AI-generated phishing, and improved measurably on new threat types after a single reviewed
retraining cycle, while keeping false positives low and every decision interpretable.

### 5d. Replace Section 7.1 Conclusion (fixes 16 ms)


## 7.1 Conclusion

An adaptive email spam detection system using artificial intelligence and content–metadata
fusion was designed, implemented and evaluated. The system fused word and character TF-IDF
content features with thirteen standardised structural metadata signals in a class-balanced
logistic-regression model, with Naïve Bayes and a linear support vector machine evaluated for
comparison. On a held-out split of 81,152 public emails it achieved 99.2% accuracy with
precision 0.991, recall 0.992 and ROC-AUC of 1.000, at a median latency of approximately 13
milliseconds per email on a commodity central processing unit and a false-positive rate of about
0.9%. It flagged 92% of previously unseen phishing emails generated by three large language
models, demonstrating that a conventionally trained fusion detector generalises strongly to
AI-assisted phishing without any AI-specific training. After a single reviewed retraining
cycle it improved from ROC-AUC 0.81 to 0.945 on held-out modern-threat email while preserving
main-corpus accuracy, evidencing an effective and practical adaptation mechanism. The system
was delivered as a local, open-source service with a browser review console, mailbox
quarantine and feedback-driven retraining, satisfying all four stated objectives.

### 5e. Add Section 7.2 (missing entirely), between 7.1 and the Recommendation section


## 7.2 Limitations of the Adaptation Mechanism

Two properties of the adaptation loop constrain how quickly and how safely the deployed model
can change, and both were deliberate design decisions rather than oversights.

The first is that retraining is a batch operation and cannot be performed on a single new
message. Term weighting in the proposed system is corpus-dependent: as Equation (3.2) shows, the
inverse document frequency of a term is computed from the total number of documents and the
number of documents containing that term, so introducing one additional message changes the
weight of every term in the vocabulary. The vectoriser and the classifier must therefore be
refitted together over the whole corpus, which takes several minutes on the 81,152-message
dataset. Training on the corrected message alone is not a valid alternative: the resulting model
would represent only that single example and would discard everything learned from the remaining
corpus, an effect known as catastrophic forgetting. Retraining is consequently performed as a
scheduled maintenance action on the corpus together with the accumulated corrections, rather than
after every individual review.

An incremental alternative exists. A stochastic-gradient classifier combined with feature hashing
supports partial fitting, and would allow the model to be updated in milliseconds for each
reviewed message. It was not adopted here for two reasons. Such a model forgoes the calibrated
probability estimates that the present system relies on for its adjustable decision threshold and
for the explanation of individual verdicts, and, more importantly, it removes the human
checkpoint between a reviewer's correction and a change in the deployed model. That checkpoint is
a security control. Adaptive filters are a documented target for label-flipping poisoning
attacks, in which an adversary submits deliberately mislabelled messages so that the decision
boundary shifts in their favour over time. In the proposed system a correction cannot alter the
deployed model until a reviewer explicitly requests retraining, and the candidate model is then
accepted only if it does not reduce ranking quality on the held-out split; a batch of corrupted
corrections is therefore rejected automatically rather than silently degrading detection.

The second limitation is that the validation gate protects against a poor batch of corrections
but does not provide model versioning. Once a candidate model has been accepted and deployed,
there is no automated mechanism to revert to a previous version, and a reviewer correction
recorded in error can be changed or withdrawn only before the next retraining cycle is run.

---

## FIX 6 — Optional: Sections 5.3 and 5.4

Section 5.3 has been rewritten in the departmental exemplar style: a short lead-in paragraph
naming what is being configured, then four numbered, step-by-step configuration procedures
(environment, detector, mail account, detection service, filtering and review). It now includes
a Detection Service Configuration subsection with a new Table 5.5 listing the service endpoints,
which pushes the old "Command-line operations" table to Table 5.6. Replace your whole Section 5.3
with the block below, and renumber that later table to 5.6.

Section 5.4 in your document has only three figures. The current version has five numbered
subsections, one per figure, each with an explicit "Figure 5.x shows..." elaboration, which is
what the marking guidance on diagrams asks for.

### 6a. Section 5.3


## 5.3 Setting and Configuration

In this section, we outline the critical setup and configuration steps required to enable the
key functionalities of the system, namely local classification, live mailbox retrieval and
reviewer-driven retraining. These configurations ensure that the machine can run the detector
in an isolated Python environment, that the trained model is available to every component, and
that the connector is able to authenticate to a mail account over the Internet Message Access
Protocol (IMAP) and act on new messages safely. No paid service, cloud classification interface
or third-party scanning key is required: all classification is performed locally by the trained
model, and the only credential involved is the mail-account application password used to read
the mailbox. Below are the steps for configuring the Python environment, the detector itself,
the mail account used for live filtering, the local detection service interface, and the
filtering and review behaviour of the running system.

### 5.3.1 Python Environment Configuration

1. **Install Python:** download Python 3.13 for Windows from python.org and, during
   installation, tick "Add python.exe to PATH" so that the interpreter can be invoked from any
   terminal.
2. **Obtain the project files:** place the project folder on the local disk and open a terminal
   in that folder.
3. **Create the virtual environment:** run `python -m venv .venv` so that the project libraries
   are isolated from the system-wide Python installation.
4. **Activate the environment:** run `.venv\Scripts\activate`. The terminal prompt is then
   prefixed with `(.venv)`, confirming that the environment is active.
5. **Install the required libraries:** run `pip install -r requirements.txt`, which installs
   scikit-learn, FastAPI, Uvicorn, NumPy, SciPy, Matplotlib and Joblib together with their
   dependencies.
6. **Verify the installation:** run `pip list` and confirm that the packages listed in Table 5.2
   are present with the stated versions, as shown in Figure 5.1.

No configuration file, environment variable or administrator privilege is required for this
stage.

### 5.3.2 Detector Configuration

1. **Prepare the corpus:** run `python -m spam_detection.prepare_dataset` to merge the six
   public source files, de-duplicate them on normalised message content and write the reviewed
   dataset to `data/reviewed_mail.csv` (81,152 messages).
2. **Train the fusion model:** run `python -m spam_detection.train` to fit the word and
   character TF-IDF vectorisers, the metadata vectoriser and the class-balanced logistic
   regression on the training split.
3. **Confirm the saved model:** check that `models/email_spam_detector.joblib` has been created.
   This single file contains the vectorisers, the scaler and the classifier, so the service and
   the mailbox connector always load an identical predictor.
4. **Set the decision threshold:** the deployed threshold defaults to 0.55. It may be re-tuned
   per deployment using the threshold sweep produced during evaluation; lowering the threshold
   increases recall at the cost of more false positives, which is useful when catch rate on
   AI-style mail is prioritised.
5. **Review the hyper-parameters:** the classifier and feature settings are fixed at training
   time and are listed in Table 5.3.

**Table 5.3 — Model and feature hyper-parameters.**

| Component | Setting |
|---|---|
| Word TF-IDF | n-grams 1–2; max 40,000 features; sub-linear TF |
| Character TF-IDF | `char_wb`; n-grams 3–5; max 30,000 features; sub-linear TF |
| Metadata vectoriser | `DictVectorizer` (sparse) |
| Metadata scaling | `StandardScaler(with_mean=False)` |
| Classifier | `LogisticRegression(class_weight="balanced", C=1.5, max_iter=1000)` |
| Decision threshold | 0.55 default; sweep-tunable |
| Random state | Fixed seed for reproducibility |

In plain terms, the word and character TF-IDF rows controlled how the email text was turned into
numbers: single words and two-word pairs, and three-to-five-character fragments, were counted up
to a fixed vocabulary size, with very frequent words dampened. The dictionary vectoriser turned
the thirteen metadata signals into numerical features, and the standard scaler rescaled those
signals so that a raw value such as body length could not outweigh the word features. The
classifier used class-balanced weighting so that the spam and legitimate classes were treated
fairly even if one was more common, with a regularisation strength of C = 1.5. The decision
threshold of 0.55 meant an email was flagged as spam only when the model's spam probability
exceeded 0.55. A fixed random seed ensured that the same training run could be reproduced
exactly.

### 5.3.3 Mail-Account Configuration for Live Filtering

To filter real incoming mail rather than pasted samples, the detector connects to a mail account
over IMAP, the same protocol ordinary mail clients use to read mail. A dedicated test account
was used throughout, so that no third party's private correspondence was processed.

1. **Create a dedicated test mail account:** register an account used only for this project, so
   that no personal or third-party mail is read by the system.
2. **Enable two-step verification:** in the account security settings, turn on two-step
   verification. This is a prerequisite for issuing an application password.
3. **Generate an application password:** in the same security settings, create a sixteen-
   character application password for the connector and copy it. The ordinary login password is
   never used and is never stored by the system.
4. **Supply the credentials as environment variables:** set them in the terminal rather than
   editing any source file, so that no password is written into the code or into this report:

```
$env:IMAP_USER = "the test address"
$env:IMAP_PASS = "the sixteen-character application password"
```

5. **List the available mailbox folders:** run
   `python -m spam_detection.imap_watch --list-folders` to confirm that the connection and the
   credentials are accepted and to obtain the exact folder names used by the provider.
6. **Run a read-only check first:** the connector defaults to `report` mode, in which messages
   are scored and logged but nothing is moved or deleted:
   `python -m spam_detection.imap_watch --action report`
7. **Select the folder to monitor, if required:** the connector reads INBOX by default; another
   folder may be chosen with, for example,
   `python -m spam_detection.imap_watch --source-folder "[Gmail]/Spam" --action report`
8. **Enable automatic filtering:** once the read-only check succeeds, start continuous
   monitoring with quarantine enabled:
   `python -m spam_detection.imap_watch --action quarantine --watch`

### 5.3.4 Detection Service Configuration

The detector is exposed as a local representational-state-transfer (REST) service built with
FastAPI and served by Uvicorn. The service is what the review console, the mailbox watchers and
any external automation talk to, so it must be started and verified before live filtering is
attempted. It listens only on the local machine and requires no account, no key and no internet
connection.

1. **Activate the environment:** open a terminal in the project folder and run
   `.venv\Scripts\activate`.
2. **Confirm the model is present:** check that `models/email_spam_detector.joblib` exists. The
   service loads this file once at start-up; if it is missing, the service still starts but
   every prediction request is refused.
3. **Start the service:** run `uvicorn spam_detection.api:app --reload`. Uvicorn binds to
   `http://127.0.0.1:8000` by default and prints `Application startup complete` when ready.
4. **Change the port if 8000 is occupied:** restart with an explicit port, for example
   `uvicorn spam_detection.api:app --port 8001`.
5. **Verify that the service is healthy:** open `http://localhost:8000/health` in a browser. A
   response of `{"status": "ready"}` confirms that the model loaded successfully; a response of
   `model_not_loaded` indicates that step 2 was not satisfied.
6. **Open the review console:** browse to `http://localhost:8000`. The console is served by the
   same process, so no separate front-end installation is required.
7. **Test a single prediction:** paste a raw email into the console and submit it, or send a
   request directly to the `/predict` endpoint, and confirm that a label, a spam probability and
   the contributing metadata signals are returned.
8. **Leave the service running:** the mailbox watchers and the retraining control depend on it,
   so the terminal window is kept open for the duration of a filtering session.

The endpoints the service exposes are listed in Table 5.5.

**Table 5.5 — Detection-service endpoints.**

| Endpoint | Method | Purpose |
|---|---|---|
| `/` | GET | Serves the browser review console |
| `/health` | GET | Reports whether the model loaded and how many feedback rows exist |
| `/predict` | POST | Scores one raw email and returns the label, spam probability and metadata signals |
| `/feedback` | POST | Records a reviewer's correct label for a submitted email |
| `/queue` | GET | Returns the messages scanned by the mailbox watchers that still await review |
| `/queue/{row}/message` | GET | Returns the stored copy of one queued message for preview |
| `/queue/feedback` | POST | Records or replaces the reviewer's verdict for a queued message |
| `/queue/{row}/undo` | POST | Withdraws a verdict recorded in error |
| `/retrain` | POST | Trains a candidate model on the corpus plus accumulated corrections and deploys it only if it does not reduce ranking quality |

As shown in Table 5.5, the service separates scoring from learning: the prediction endpoints are
read-only with respect to the model, and the deployed model can change only through an explicit
call to the retraining endpoint. This is the configuration-level expression of the human
checkpoint discussed in Section 7.2.

### 5.3.5 Filtering and Review Configuration

1. **Choose the action mode:** use `report` while validating the filter and `quarantine` once it
   is trusted to move mail. Flagged messages are copied into the quarantine folder and are never
   deleted.
2. **Set the polling interval:** pass `--poll-seconds` to control how often the mailbox is
   checked; the default is ten seconds.
3. **Choose where copies are stored:** pass `--save-dir` so that a copy of each scored message is
   written to disk, allowing the reviewer to open the original message from the console.
4. **Review and correct verdicts:** confirm or correct each queued message. Only the most recent
   verdict for a message is retained, and corrections accumulate in the feedback store without
   altering the deployed model.
5. **Trigger retraining when required:** use the retraining control in the console, which calls
   the `/retrain` endpoint listed in Table 5.5. Retraining is a planned batch operation initiated
   by the reviewer; no automatic timer is used, so no change reaches the deployed model without
   human authorisation. The candidate model replaces the deployed model only if it does not
   reduce ranking quality on the held-out split.

The resulting operational settings are summarised in Table 5.4. The server host and port are
inferred automatically from the address domain for common providers, so in normal use only the
account credentials must be supplied.

**Table 5.4 — Mailbox connection and filtering configuration.**

| Setting | Value | Purpose |
|---|---|---|
| Protocol | IMAP over SSL/TLS (port 993) | Encrypted retrieval of new mail |
| Server host | Inferred from the address domain | Avoids manual server entry for common providers |
| Authentication | Sixteen-character application password, supplied as an environment variable | Avoids storing a password in code or configuration files |
| Source folder | `--source-folder` (default INBOX) | Selects which mailbox folder is monitored |
| Action mode | `report` (read-only) or `quarantine` | Read-only scoring for testing; quarantine for live filtering |
| Quarantine folder | `Spam_Quarantine` | Flagged mail is copied there, never deleted |
| Poll interval | `--poll-seconds` (default 10 seconds) | Frequency at which the folder is checked for new mail |
| Saved-message directory | `--save-dir` | Stores a copy of each scored message so it can be previewed during review |
| Processed-message state file | `imap_seen_<folder>.txt` | Prevents a message from being scored twice |
| Review queue | `review_queue.csv` | Records every decision so a reviewer can correct mistakes |
| Decision threshold | 0.55 | Probability above which a message is treated as spam |

As shown in Table 5.4, the configuration was deliberately conservative: flagged mail is copied
into a quarantine folder rather than deleted, the read-only mode allows the filter to be
validated before it is allowed to move anything, and every decision is logged so that reviewer
corrections can be fed back into the next retraining cycle described in Section 3.4.

### 6b. Sections 5.4.1 to 5.4.5


### 5.4.1 Checking an Email in the Review Console

The review console was the manual entry point to the detector. A reviewer pasted the complete
source of an email into the console and submitted it for scoring. The console returned the
predicted label, the spam probability, a confidence value and the list of structural signals that
fired for that message, so that the verdict could be interpreted rather than merely accepted.
Figure 5.2 shows the console after a phishing message was submitted.

[FIGURE 5.2: Browser check-and-review console showing a phishing verdict and fired signals.]

Figure 5.2 shows the console classifying a credential-harvesting message as spam. The probability
bar reports the score assigned by the model, and the signal chips beneath it name the structural
evidence that contributed to the decision, including the mismatch between the sender domain and
the domain of the embedded link and the presence of a reply-to address different from the sender.

### 5.4.2 Service Prediction Response

The same detector was exposed as a local service so that other software could obtain a verdict
programmatically rather than through the browser. A client submitted the raw email to the
prediction endpoint and received a structured response. Figure 5.3 shows a response returned by
the service.

[FIGURE 5.3: Example service prediction response (label, probability and signals).]

Figure 5.3 shows the response for a single message, containing the predicted label, the spam
probability, the confidence value and the named structural signals. Returning the signals
alongside the verdict allowed a calling system to log why a message was flagged, which was a
requirement for the review and appeal process described in Section 4.4.

### 5.4.3 Mailbox Watch and Quarantine

The mailbox watcher applied the detector to a folder of stored messages rather than to a single
pasted email. Each message file was parsed, scored and recorded in the review queue; in
quarantine mode a flagged message was moved into a separate quarantine folder while legitimate
mail was left untouched. Figure 5.4 shows a watch run in progress.

[FIGURE 5.4: Mailbox watch run quarantining a flagged message.]

Figure 5.4 shows the watcher processing a folder containing both legitimate and phishing
messages. Each line reports the verdict and the probability for one message, and the flagged
messages are reported as moved to the quarantine folder. Nothing was deleted at any point: the
quarantine folder retained every flagged message so that a false positive could be recovered.

### 5.4.4 Live Mailbox Filtering over IMAP

To confirm that the connector operated outside a controlled local folder, it was run against a
live mailbox hosted by a commercial provider. A disposable account was created for the purpose,
application-specific credentials were issued for it, and four test messages were sent to it: one
ordinary message and three phishing messages of the credential-harvesting, fraudulent invoice
and account-suspension types. The connector authenticated over an encrypted IMAP connection on
port 993, retrieved each message in its complete RFC 5322 form and scored it with the same saved
model used throughout Chapter 6, with no change to the classifier, its features or its decision
threshold.

An unanticipated but instructive observation arose during this run. The provider applied its own
filter before delivery and placed all four test messages, including the legitimate one, in its
spam folder, so that none of them reached the inbox. The connector was therefore directed at that
folder instead, which had the useful effect of turning the exercise into an independent second
opinion on messages the provider had already judged. Figure 5.5 records the result.

[FIGURE 5.5: Live IMAP run scoring four messages retrieved from a commercial mailbox, showing
three phishing messages flagged and one legitimate message released.]

Figure 5.5 shows that the three phishing messages were assigned spam probabilities of 97.6%,
98.7% and 99.8% and were flagged, whereas the legitimate message received 27.4% and was correctly
released. The proposed detector therefore agreed with the provider on the three phishing messages
and disagreed on the one legitimate message, which the provider had filtered and the detector had
not. This single observation is a demonstration of deployment, not a measurement of comparative
accuracy, and no general claim about the relative performance of the two systems is drawn from
it; the quantitative results in Chapter 6 rest entirely on the held-out corpus and the external
test sets. It does, however, confirm that the detector operates correctly on live network mail.

### 5.4.5 Reviewer Feedback and Retraining

Every message scored by either watcher was written to the review queue, and the console presented
those messages to a reviewer for confirmation or correction. For each message the reviewer either
confirmed the verdict or recorded the correct label; a verdict entered by mistake could be
changed simply by selecting a different one, and only the most recent verdict for a message was
retained. Corrections accumulated in the feedback store and did not alter the deployed model
until retraining was explicitly requested. Figure 5.6 shows the review inbox.

[FIGURE 5.6: Review inbox showing scored messages with confirm and correct controls, and the
retraining control.]

Figure 5.6 shows the queued messages with their verdicts and probabilities, the controls used to
confirm or correct each one, and the control that starts a retraining cycle. When retraining was
requested, a candidate model was trained on the historical corpus together with the accumulated
corrections and was compared with the deployed model on the held-out split; the candidate
replaced the deployed model only if it did not reduce ranking quality. This validation gate is
discussed further in Section 7.2.

---

## After pasting

1. Re-run the figure generator so Figures 6.2, 6.3 and 6.4 match the corrected numbers:
   `python reports\make_result_figures.py` — then check `reports/figures/fig6_4.png` no longer
   reads "20% to 85%".
2. Capture Figure 5.6 (review inbox with confirm / correct / retrain controls).
3. Update the List of Figures: there are now 23 figures, with Figure 5.6 added.
4. Update the Table of Contents (right-click, Update Field, Update entire table).
5. Remove all yellow highlighting from the Copyright Statement and the Abstract.
