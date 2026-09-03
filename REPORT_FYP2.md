<!--
================================================================================
UTAR FYP2 REPORT — MASTER DRAFT (Markdown)
Project: Adaptive Email Spam Detection using AI and Content–Metadata Fusion
Student: Lee Gong Yi | Supervisor: Dr Abdulrahman Aminu Ghali
Degree: Bachelor of Information Technology (Honours) Communications and Networking
Faculty: Faculty of Information and Communication Technology (Kampar Campus), UTAR

HOW TO TURN THIS INTO THE SUBMITTED DOCUMENT
1. Copy the text into the official FYP2 Word template (from the UTAR FYP portal).
   Formatting rules (from the FYP2 Information Booklet v26 Oct 2025):
   - Times New Roman 12 pt, 1.5 line spacing, black, British English.
   - Third person and past tense throughout (already written this way).
   - Margins: left 1 in (front cover 1.2 in), right 1 in, top/bottom 1 in.
   - Header (left): degree + faculty; footer (right): page number.
   - Front matter numbered i, ii, iii... (title page = i but number not printed).
   - Chapters and references numbered 1, 2, 3...; appendices A-1, B-1...
   - Each chapter begins on a new page; subsections no deeper than 3 levels.
2. Search for every [FILL IN] and complete it (student ID, dates, screenshots).
3. Every [FIGURE x.y: ...] block is a placeholder — insert the diagram/screenshot
   there and keep the caption text. Every [TABLE x.y ...] with [ ] cells is filled
   by running the indicated command on YOUR data/reviewed_mail.csv.
4. Remove these HTML comment notes before submission.
5. Turnitin: upload ONLY title page, abstract, chapters 1–7 and references.
   Remove cover, declaration, acknowledgements, ToC, lists, and appendices for the
   similarity check; keep the full file for final submission.
Target length: 8,000–20,000 words. This draft is within that range once figures and
tables are inserted.
================================================================================
-->

# FRONT COVER
<!-- Use Appendix A of the booklet. Content is identical to the title page.
     Times New Roman 12; no UTAR logo; left margin 1.2 in; do not alter layout. -->

ADAPTIVE EMAIL SPAM DETECTION USING AI AND CONTENT–METADATA FUSION

LEE GONG YI

[FILL IN: Student ID]

A PROJECT REPORT SUBMITTED TO
UNIVERSITI TUNKU ABDUL RAHMAN
IN PARTIAL FULFILMENT OF THE REQUIREMENTS FOR THE DEGREE OF
BACHELOR OF INFORMATION TECHNOLOGY (HONOURS)
COMMUNICATIONS AND NETWORKING

FACULTY OF INFORMATION AND COMMUNICATION TECHNOLOGY
(KAMPAR CAMPUS)

[FILL IN: Month YEAR — e.g. SEPTEMBER 2026]

---

# TITLE PAGE
<!-- One page; same content as front cover (booklet Appendix B). -->

ADAPTIVE EMAIL SPAM DETECTION USING AI AND CONTENT–METADATA FUSION

By
LEE GONG YI

A PROJECT REPORT SUBMITTED TO
UNIVERSITI TUNKU ABDUL RAHMAN
IN PARTIAL FULFILMENT OF THE REQUIREMENTS FOR THE DEGREE OF
BACHELOR OF INFORMATION TECHNOLOGY (HONOURS)
COMMUNICATIONS AND NETWORKING

FACULTY OF INFORMATION AND COMMUNICATION TECHNOLOGY
(KAMPAR CAMPUS)

[FILL IN: Month YEAR]

---

# COPYRIGHT STATEMENT
<!-- One page; use the exact faculty wording from Appendix B and highlight-replace
     the name/year. Remove yellow highlighting before submission. -->

© [FILL IN: YEAR] LEE GONG YI. ALL RIGHTS RESERVED.

This Final Year Project report is submitted in partial fulfilment of the
requirements for the degree of Bachelor of Information Technology (Honours)
Communications and Networking at Universiti Tunku Abdul Rahman (UTAR).

This Final Year Project report represents the work of the author, except where
due acknowledgment has been made in the text. No part of this Final Year Project
report may be reproduced, stored, or transmitted in any form or by any means,
whether electronic, mechanical, photocopying, recording, or otherwise, without
the prior written permission of the author or UTAR, in accordance with UTAR's
Intellectual Property Policy.

---

# ACKNOWLEDGEMENTS
<!-- One page. Replace/extend as appropriate; third or first person is acceptable on
     this page. A suggestion consistent with Project I: -->

The author would like to express sincere gratitude to the project supervisor,
Dr Abdulrahman Aminu Ghali, for the guidance, constructive feedback and continuous
support throughout the development of this project. The opportunity to work on a
cybersecurity and artificial-intelligence project has been an enriching experience
and a meaningful step towards professional aspirations in the field.

The author also wishes to thank the Faculty of Information and Communication
Technology for the resources provided, and family and friends for their
encouragement throughout the duration of the study.

---

# ABSTRACT

Email remained a primary vector for phishing, business-email-compromise and malware
delivery, while generative language models had lowered the effort required to write
polished, convincing fraudulent messages. Rule-based and keyword filters were brittle
against such evolving, fluent attacks. This project developed an adaptive email spam
detection system that fused two complementary views of a message — its textual content
and its structural metadata — within a machine-learning pipeline, and that improved over
time through reviewed-feedback retraining.

Raw emails were parsed to extract word and character term-frequency–inverse-document-
frequency (TF-IDF) content features together with twelve structural metadata signals,
including URL and attachment counts, sender-to-link domain mismatch, reply-to presence,
sender-policy-framework and DomainKeys-Identified-Mail indicators, and casing and urgency-
term statistics. The streams were fused into a single feature space and classified by a
class-balanced logistic regression model, with multinomial Naïve Bayes and a linear support
vector machine evaluated for comparison. A FastAPI service, a browser review console, a
mailbox watcher with quarantine, and a feedback-driven retraining loop were implemented,
together with an optional deep-learning DistilBERT branch documented for graphics-
processing-unit deployment.

The fused model was trained on 81,152 de-duplicated public emails and achieved 99.2%
accuracy with precision 0.991, recall 0.992 and receiver-operating-characteristic area
under the curve of 1.000 on a held-out test split, at a median latency of approximately
16 milliseconds per email on a commodity central processing unit. On 4,986 phishing emails
generated by three large language models — none of which the model was trained on — the
detector flagged 92%, demonstrating strong generalisation to AI-assisted phishing. After
one adaptive retraining cycle on reviewed modern-threat examples, detection ranking on
held-out AI-style email improved from area under the curve 0.81 to 0.945 while overall
accuracy was maintained. The system detected phishing intent rather than AI authorship, and
its signals and operating threshold were fully explainable and adjustable.

**Area of Study:** Cybersecurity, Artificial Intelligence.
**Keywords:** Spam Detection, Phishing, Content–Metadata Fusion, Adaptive Systems, Machine
Learning.

---

# TABLE OF CONTENTS
<!-- Generated automatically in Word (References > Table of Contents). Skeleton:
TITLE PAGE / COPYRIGHT / ACKNOWLEDGEMENTS / ABSTRACT / TABLE OF CONTENTS /
LIST OF FIGURES / LIST OF TABLES / LIST OF ABBREVIATIONS
CHAPTER 1 INTRODUCTION
  1.1 Problem Statement and Motivation
  1.2 Objectives
  1.3 Project Scope
  1.4 Contributions
  1.5 Report Organisation
CHAPTER 2 LITERATURE REVIEW
  2.1 Review of the Technologies
    2.1.1 Hardware Platform
    2.1.2 Firmware / Operating System
    2.1.3 Database
    2.1.4 Programming Language and Libraries
    2.1.5 Algorithms
    2.1.6 Summary of the Technologies Review
  2.2 Review of Existing Systems and Applications
    2.2.1 Rule- and Keyword-Based Filters
    2.2.2 Content-Based Statistical Classifiers
    2.2.3 Metadata and Reputation-Based Systems
    2.2.4 Hybrid and Fusion Systems
    2.2.5 Deep-Learning and Commercial Systems
    2.2.6 Summary of the Existing Systems
CHAPTER 3 SYSTEM METHODOLOGY / APPROACH
  3.1 System Design Diagram
    3.1.1 System Architecture Diagram
    3.1.2 Use Case Diagram and Description
    3.1.3 Activity Diagram
CHAPTER 4 SYSTEM DESIGN
  4.1 System Block Diagram
  4.2 System Components Specifications
  4.3 Data and Feature Design
  4.4 System Components Interaction Operations
CHAPTER 5 SYSTEM IMPLEMENTATION
  5.1 Hardware Setup
  5.2 Software Setup
  5.3 Setting and Configuration
  5.4 System Operation (with Screenshots)
  5.5 Implementation Issues and Challenges
  5.6 Concluding Remark
CHAPTER 6 SYSTEM EVALUATION AND DISCUSSION
  6.1 System Testing and Performance Metrics
  6.2 Testing Setup and Result
  6.3 Project Challenges
  6.4 Objectives Evaluation
  6.5 Concluding Remark
CHAPTER 7 CONCLUSION AND RECOMMENDATION
  7.1 Conclusion
  7.2 Recommendation
REFERENCES
APPENDICES
-->

# LIST OF FIGURES
<!-- In Word: Insert Table of Figures. Skeleton: -->

- Figure 3.1 System architecture of the adaptive fusion spam-detection framework.
- Figure 3.2 Use-case diagram for the reviewer/administrator actor.
- Figure 3.3 Activity diagram for scoring, review and adaptive retraining.
- Figure 4.1 System block diagram (ingestion, features, fusion, action, adaptation).
- Figure 5.1 Software and virtual-environment setup.
- Figure 5.2 Browser check-and-review console showing a phishing verdict and signal chips.
- Figure 5.3 Example `/predict` JSON response.
- Figure 5.4 Mailbox watch run quarantining a flagged message.
- Figure 6.1 Confusion matrix of the fused model on the held-out test split (n = 20,288).
- Figure 6.2 ROC curve and threshold sweep for the fused model.
- Figure 6.3 Catch rate versus decision threshold on the LLM-phishing set.
- Figure 6.4 ROC curves before and after one adaptive retraining cycle.
- Appendix A Poster.

# LIST OF TABLES
- Table 2.1 Comparison of detection paradigms.
- Table 3.1 Use-case descriptions.
- Table 3.2 Integrated public corpus and class distribution.
- Table 4.1 Component modules and responsibilities.
- Table 4.2 The twelve structural metadata signals.
- Table 5.1 Development hardware and software.
- Table 5.2 Model and feature hyper-parameters.
- Table 6.1 Held-out performance of the deployed fused model.
- Table 6.2 Classifier and feature-group comparison (Objective 3).
- Table 6.3 Detection of genuine LLM-generated phishing (n = 4,986).
- Table 6.4 Before/after adaptive retraining on held-out modern-threat email.
- Table 6.5 Comparison with commercial mail filters (vendor-reported context).
- Table 6.6 Comparison with published models on comparable public corpora.
- Table 6.7 Objectives evaluation summary.

# LIST OF SYMBOLS
<!-- The report uses few symbols; include those below (or omit this list if unused). -->
- ŷ — predicted class / predicted spam probability output.
- σ(·) — logistic (sigmoid) function.
- w, b — logistic-regression weight vector and bias term.
- TP, FP, TN, FN — true positive, false positive, true negative, false negative.
- C — logistic-regression regularisation strength parameter.

# LIST OF ABBREVIATIONS
- API — Application Programming Interface
- AUC — Area Under the Curve
- BEC — Business Email Compromise
- BERT — Bidirectional Encoder Representations from Transformers
- CPU — Central Processing Unit
- CSV — Comma-Separated Values
- DKIM — DomainKeys Identified Mail
- FPR — False-Positive Rate
- GPU — Graphics Processing Unit
- HTML — HyperText Markup Language
- IDE — Integrated Development Environment
- LR — Logistic Regression
- ML — Machine Learning
- NB — Naïve Bayes
- NLP — Natural Language Processing
- ROC — Receiver Operating Characteristic
- REST — Representational State Transfer
- SPF — Sender Policy Framework
- SVM — Support Vector Machine
- TF-IDF — Term Frequency–Inverse Document Frequency
- TLD — Top-Level Domain
- URL — Uniform Resource Locator

---
---

# CHAPTER 1: INTRODUCTION

## 1.1 Problem Statement and Motivation

Electronic mail remained one of the most widely used communication channels in
organisations and, at the same time, one of the most exploited. Cybersecurity had become a
pressing global concern as internet adoption, cloud services, e-commerce and remote work
expanded the exposure of individuals and organisations to cyber risk; industry estimates
projected annual cybercrime damages reaching into the trillions of United States dollars,
with ransomware, phishing, data breaches and identity theft among the principal causes [1].
Among the available attack vectors, email continued to be favoured because it was ubiquitous,
trusted and inexpensive to abuse. Unsolicited or fraudulent messages, broadly termed spam,
had for many years accounted for a substantial fraction of global email traffic, ranging from
nuisance advertisements to sophisticated phishing campaigns designed to steal credentials,
financial data or to distribute malware [2], [3].

Early spam messages were comparatively simple and could be blocked by keyword filters or
blacklists. Attackers, however, evolved their techniques continuously. Modern campaigns used
obfuscation such as inserted characters, misleading links and disguised headers, while
phishing — the subset of spam that deceived recipients into revealing sensitive information —
grew particularly dangerous and featured prominently in reported data breaches [3]. Two more
recent trends made the problem materially harder. First, business-email-compromise (BEC)
attacks used calm, professional, grammatically correct language and frequently contained no
malicious link or attachment at all, so they evaded signatures designed for obvious,
keyword-laden spam. Second, large language models allowed attackers to generate fluent,
personalised, typo-free fraudulent messages at scale, removing the historical language barrier
that had made many phishing emails easy for a human reader to recognise.

A further, persistent issue was concept drift: the characteristics of spam evolved over time,
so a model trained once on older data gradually failed to recognise new tactics unless it was
updated. Static rule lists and statically trained models therefore degraded in production.
False positives — legitimate email wrongly marked as spam — were especially costly, because
they interrupted business communication and damaged trust in the filter; false negatives, on
the other hand, allowed malicious mail to reach the user. Conventional defences had
complementary weaknesses. Pure content models examined what a message said but ignored how it
was constructed; pure rule or reputation systems used structural indicators but could be
bypassed by well-written text; and systems that were never updated could not follow evolving
campaigns.

The motivation for this project was therefore to build a detector that (a) fused content and
metadata so that fluent wording and structural anomalies were judged together, (b) remained
fast and interpretable enough to run locally on ordinary hardware without dependence on
external cloud services, and (c) adapted to new threats through a reviewed retraining loop
rather than through manual editing of rules. The project carried forward the proposal
established in Project I — an adaptive content–metadata fusion spam-detection framework — and
implemented and evaluated it as a complete, deployable system.

Project I had established the feasibility of the approach on a smaller integrated corpus and
confirmed that content and metadata each carried complementary signal. Project II moved from a
preliminary baseline to a finished, deployable system: it scaled the pipeline to a larger and
more varied public corpus, hardened the implementation against malformed real-world input,
added a service and quarantine layer, built the reviewed retraining loop end to end, and tested
generalisation against genuinely AI-generated phishing. The relationship between the two
phases was therefore one of realisation and validation rather than redirection: the same four
objectives defined in the proposal drove the implementation, and the results reported in
Chapter 6 measured the extent to which each was met.

## 1.2 Objectives

The aim of this project was to design and implement an adaptive spam detection system that
leveraged content–metadata fusion for enhanced email security. To achieve this aim, the
project was guided by four specific objectives, carried forward unchanged from Project I:

1. To extract and process content-based features (body text, subject lines and embedded URLs)
   and metadata features (sender information and header attributes) from raw email datasets.
2. To design a content–metadata fusion framework that combined textual and structural data
   into a unified machine-learning pipeline.
3. To train and evaluate artificial-intelligence-based classification models — namely Naïve
   Bayes, logistic regression and support vector machines — on the fused feature set.
4. To implement an adaptive retraining mechanism that updated the model with newly reviewed
   samples, so that detection accuracy was maintained as spam patterns evolved over time.

## 1.3 Project Scope

The system was scoped to English-language email, processed and trained locally with no
dependency on external cloud application programming interfaces and no use of private employee
or customer email. This local-first scope was a privacy and reproducibility decision: because
no message content left the host, the detector could be evaluated and deployed without exposing
mail to a third-party service, and every reported figure could be reproduced from public data.
All data used for training and testing were public corpora or synthetic data generated for
controlled experiments. The core detector was a classical machine-learning model
over content and metadata; a deep-learning transformer branch (DistilBERT) was designed and
provided as an optional, graphics-processing-unit-deployed enhancement, with a ready-to-run
notebook for free cloud execution.

The system produced a spam probability, a binary label and an explanation of the structural
signals observed in a message, and it supported a configurable action (report or quarantine)
rather than destructive deletion. It was delivered as a set of standalone, modular Python
scripts together with a representational-state-transfer service, a browser review console and
a mailbox watcher. The classifier identified malicious intent; it did not attempt to determine
whether a message had been authored by an artificial intelligence, a task that independent
evaluations had shown to be unreliable. Instant-messaging and social-media content were outside
the scope.

## 1.4 Contributions

The project made the following contributions:

1. A working content–metadata fusion detector that combined word and character TF-IDF content
   features with twelve structural metadata signals in a single, standardised feature space.
2. A structured comparison of multinomial Naïve Bayes, logistic regression and a linear support
   vector machine on both content-only and fused features, quantifying the contribution of the
   feature groups.
3. A complete adaptive loop — a review console, a feedback store and a scheduled retraining
   path — demonstrated empirically to improve detection on previously unseen threat types.
4. A deployable service layer comprising a REST application programming interface, a browser
   review page, a mailbox watcher with quarantine, and a documented integration route for mail
   automation.
5. An empirical evaluation that included detection of genuine large-language-model-generated
   phishing, reported with explicit validity controls and without unsupported claims of
   superiority over commercial filters.

## 1.5 Report Organisation

Chapter 2 reviews the technologies and existing systems relevant to email spam detection.
Chapter 3 presents the system methodology, including the architecture, use cases and activity
flow. Chapter 4 details the system design at a level sufficient to rebuild the system. Chapter 5
describes the hardware and software setup, configuration, operation and implementation
challenges. Chapter 6 reports the evaluation setup, results, discussion and an
objective-by-objective assessment. Chapter 7 concludes the report and recommends future work.
References and appendices follow.

---

# CHAPTER 2: LITERATURE REVIEW

This chapter first reviews the technologies used in the project (hardware, operating system,
data storage, programming language and algorithms) and then reviews existing spam-detection
systems and approaches, summarising their strengths and weaknesses to position the proposed
system.

## 2.1 Review of the Technologies

### 2.1.1 Hardware Platform

The project was deliberately designed to run on commodity hardware. Development and evaluation
were performed on a consumer laptop running Windows 11, powered by an Intel-class central
processing unit with integrated Intel UHD graphics and no discrete graphics processing unit.
This constraint was treated as a design requirement rather than a limitation: a detector that
ran comfortably on a central processing unit could be deployed widely, embedded in mail
automation, and reproduced by other researchers without specialist infrastructure. The optional
deep-learning branch was engineered so that its heavier training workload could be offloaded to
a free cloud graphics processing unit, while inference of the deployed classical model remained
on the central processing unit.

### 2.1.2 Firmware / Operating System

All core components were written in cross-platform Python and were developed and tested on
Windows 11; the same code was also executed successfully in a Linux-based environment. No
special firmware was required, and no hardware programming was involved. The operating system
served only as the host for the Python runtime, the virtual environment and the local file
storage used for email and model artefacts.

### 2.1.3 Database

No database server was deployed. Emails, labels and reviewed feedback were stored as
comma-separated-value files, and the trained model was serialised to disk with Joblib. This
choice was consistent with the lightweight, script-based approach proposed in Project I, kept
the system portable and easy to back up, and avoided the operational overhead of a database for
a dataset that was processed in batch. The comma-separated-value format also allowed the public
corpora to be merged and de-duplicated with simple, auditable scripts.

### 2.1.4 Programming Language and Libraries

Python (3.11+) was used as the primary programming language for all pipeline stages. The
principal libraries were scikit-learn for feature extraction and classification — including
TF-IDF vectorisation, dictionary vectorisation of metadata, feature union, standardisation,
logistic regression, multinomial Naïve Bayes and the linear support-vector classifier — and
Joblib for model persistence. The service layer used FastAPI with Uvicorn as the application
server and Pydantic for request validation. The optional transformer branch used the Hugging
Face Transformers library, PyTorch and the Datasets library, isolated in a separate requirements
file so that the core system remained lightweight. Standard-library modules (`email`, `re`,
`csv`, `pathlib`) handled message parsing, regular-expression extraction and file handling.

### 2.1.5 Algorithms

Five algorithmic families were relevant. **Term frequency–inverse document frequency** weighted
terms by how often they appeared in a message and how rare they were across the corpus; word
unigrams and bigrams captured phrasing, while character n-grams of length three to five
tolerated obfuscation such as spaced or misspelled words. **Multinomial Naïve Bayes** applied
Bayes' theorem with a conditional-independence assumption to provide a fast generative baseline;
it remained a competitive, efficient method for text classification and had been shown to reach
high accuracy when paired with sound preprocessing [4], [16]. **Logistic regression** modelled
the log-odds of spam as a linear function of the features passed through a sigmoid, producing a
calibrated-style probability and interpretable coefficients. **Linear support vector machines**
found a maximum-margin separating hyperplane and provided a strong discriminative baseline for
high-dimensional text. **Standardisation** was applied to metadata features so that raw lengths
could not dominate the normalised text features. Finally, **transformer-based deep learning**
(DistilBERT, a distilled version of the bidirectional encoder representations from transformers
family) modelled context and paraphrase at substantially higher computational cost [10], [19].
Comprehensive reviews of machine learning for spam filtering confirmed that learned models
consistently outperformed manually engineered rule systems, and that hybrid combinations of
feature sources were among the most robust approaches [11], [20], [25]. Recent comparative
studies across many classifiers further showed that both classical models (random forest,
support vector machines) and deep models reached the high-nineties in accuracy on public
phishing and spam corpora, with the gap between them narrowing on well-prepared data [20],
[26]. Naïve Bayes in particular remained a competitive baseline not only for text but also for
related security-classification tasks, where its simplicity and speed were valued [29]. The choice of logistic
regression as the deployed classifier reflected three practical requirements of this project:
it produced a genuine probability that could be compared against an adjustable threshold, it
accepted balanced class weighting to compensate for the ham/spam ratio, and its linear
coefficients allowed the contribution of each feature to be inspected, supporting the
explainability requirement. Naïve Bayes and the linear support vector machine were retained as
comparators because together they spanned the generative-to-discriminative spectrum that was
evaluated during Project I.

### 2.1.6 Summary of the Technologies Review

A Python and scikit-learn stack provided a fast, explainable and reproducible detector on
commodity central-processing-unit hardware, with comma-separated-value storage and Joblib
persistence keeping the system portable. The documented transformer path offered a route to
semantic deep learning when a graphics processing unit was available, without burdening the
deployed system.

## 2.2 Review of Existing Systems and Applications

### 2.2.1 Rule- and Keyword-Based Filters (Existing System A)

The earliest and still widespread approach filtered mail using manually maintained rules,
keyword lists, blacklists and blocklists. Such systems were simple and fully explainable, but
they were brittle: they required constant manual updating, were easily evaded by rewording or
obfuscation, and could not generalise to novel campaigns. Their weakness in the face of fluent,
link-less business-email-compromise messages was a primary motivation for learned models.

### 2.2.2 Content-Based Statistical Classifiers (Existing System B)

Statistical content filters learned the distribution of words in spam versus legitimate mail.
The seminal Bayesian approach of Sahami et al. estimated the probability of a message being junk
from its terms [4]; later work combined TF-IDF representation with classifiers such as Naïve
Bayes and support vector machines and reported high accuracy on public corpora [5], [16].
Content methods were computationally efficient and effective for well-defined spam vocabulary,
but they examined only what a message said and were vulnerable to fluent rewording; they ignored
message structure entirely.

### 2.2.3 Metadata and Reputation-Based Systems (Existing System C)

A second family exploited structural information: sender domain and reputation, received-header
routing, presence of sender-policy-framework and DomainKeys-Identified-Mail authentication,
reply-to mismatches and link analysis. These signals caught structural anomalies that content
models missed. In the preliminary ablation conducted during Project I, a metadata-only configuration reached
approximately 93.2% accuracy with an F1 score of 83.6% — meaningful, but well below
content-based methods — confirming that metadata was valuable but insufficient on its own and
had to be combined with content.
Reputation systems were also evaded by well-formed, link-less business-email-compromise mail
sent from plausibly configured accounts.

### 2.2.4 Hybrid and Fusion Systems (Existing System D)

Hybrid approaches combined content and structural features and were repeatedly reported to be
more robust than either source alone. Studies using content- and header-based features with
machine-learning classifiers demonstrated improved reliability, and hierarchical and attention-
based fusion mechanisms had been proposed to weight complementary feature streams adaptively [9],
[18]. The Project I preliminary ablation similarly found that the content-plus-metadata fusion
configuration delivered the most balanced precision–recall trade-off and the best coverage of
spam, even though a strong text-only support-vector-machine baseline was hard to beat with simple
concatenation — a finding that motivated the richer word-plus-character content representation and
the standardised metadata used in Project II.

### 2.2.5 Deep-Learning and Commercial Systems

Deep-learning models based on word embeddings, recurrent architectures and bidirectional
transformer encoders achieved strong accuracy on public corpora and captured semantic
relationships that bag-of-words models could not [6], [7], [10], [19]. Their drawbacks were
computational cost, reduced direct explainability and a dependence on graphics processing units.
Commercial filters such as Gmail used proprietary, continuously updated artificial-intelligence
pipelines and reported blocking the vast majority of unwanted mail; because their models were
private, they could not be benchmarked offline, and any comparison required an authorised,
controlled black-box test on a disposable account. Most relevant to the present threat
landscape, recent research showed that large-language-model-generated phishing could evade an
institutional filter at high rates, while a conventional machine-learning detector trained on
ordinary phishing data still detected the large majority of those AI-generated emails [17];
public cross-model large-language-model phishing corpora and business-email-compromise datasets
had also become available for evaluation [21], [22].

### 2.2.6 Summary of the Existing Systems

Table 2.1 summarises the paradigms. The literature indicated that no single source was
sufficient: rules were brittle, content models ignored structure, metadata alone was weak, deep
learning was costly and less explainable, and commercial systems were not reproducible. The
project therefore adopted an explainable fusion of rich content and standardised metadata,
added an adaptive retraining loop to address concept drift, and evaluated the resulting system
explicitly against AI-assisted phishing.

**Table 2.1 — Comparison of detection paradigms.**

| Approach | Strengths | Weaknesses |
|---|---|---|
| Rules / keywords | Simple; fully explainable | Brittle; easily evaded; needs manual upkeep |
| Content (TF-IDF + NB/SVM) | Fast; learns wording; strong on classic spam | Ignores structure; vulnerable to fluent rewording |
| Metadata / reputation | Catches structural anomalies | Weak alone (~93% in preliminary work); evaded by link-less BEC |
| Hybrid fusion | Robust; balanced precision–recall | More features to manage; fusion design matters |
| Deep learning (BERT family) | Context and paraphrase aware | Costly; needs GPU; less directly explainable |
| Commercial filter | Very high reported block rate | Proprietary; cannot be benchmarked offline |
| This project (fusion + adaptation) | Robust, fast, explainable; updates from feedback | Semantic edge cases; GPU branch optional |

## 2.3 Limitations of Previous Studies

Three limitations motivated the design. First, many published results were reported on random
splits of single corpora where the positive and negative classes came from stylistically distinct
sources, which could overstate real-world generalisation; the present project therefore
supplemented held-out results with disjoint external and AI-generated test sets and stated the
validity threat explicitly. Second, few systems fused rich metadata with content in an
explainable, locally deployable form; the present project standardised and exposed every
metadata signal and its contribution. Third, few systems demonstrated adaptation to new threat
types or to large-language-model-generated phishing with honest framing; the present project
implemented a reviewed retraining loop and reported both its gains and its scope.

## 2.4 Proposed Solution

The proposed solution was a local, open-source adaptive detector that fused word and character
TF-IDF content features with twelve standardised structural metadata signals under a
class-balanced logistic-regression classifier, with Naïve Bayes and a linear support vector
machine evaluated for comparison. The detector was wrapped in a service with a browser review
console, a mailbox watcher with quarantine and a feedback-driven retraining loop, and was
accompanied by an optional DistilBERT branch for graphics-processing-unit deployment.

---

# CHAPTER 3: SYSTEM METHODOLOGY / APPROACH

This chapter describes the methodology as a development-based project, presenting the system
architecture, the use cases and the activity flow. The work followed a supervised, data-driven
machine-learning pipeline with an explicit adaptation stage, and each stage was implemented as an
independent Python module so that it could be retrained or replaced without rebuilding the whole
system.

## 3.1 System Design Diagram

### 3.1.1 System Architecture Diagram

The pipeline proceeded from incoming email to action and feedback. Three parallel feature
streams — word content, character content and structural metadata — were extracted, fused and
standardised, then passed to the classifier. The resulting probability was compared against a
configurable threshold to produce a label and an explanation; decisions and corrections flowed
through a review queue into the feedback store, which fed scheduled retraining.

[FIGURE 3.1: System architecture of the adaptive fusion spam-detection framework. Show seven
stages left-to-right — Data Input, Email Parsing, parallel Feature Extraction (word TF-IDF,
char TF-IDF, metadata), Feature Fusion + Standardisation, Classification, Decision/Action
(report or quarantine plus signal explanation), and Review/Feedback → Scheduled Retrain →
Redeploy, with the retrain output arrowed back to the Classification stage.]

```
        incoming email (.eml / API JSON / watched mailbox folder)
                              |
                      email parsing (RFC 5322)
                              |
        +---------------------+----------------------+
        |              feature extraction            |
        |  word TF-IDF   char TF-IDF   12 metadata    |
        +---------------------+----------------------+
                              |
            FeatureUnion fusion  ->  StandardScaler
                              |
          class-balanced Logistic Regression (deployed)
        (Naive Bayes / Linear SVM evaluated alongside)
                              |
          spam probability + fired structural signals
                              |
            threshold -> label / quarantine
                              |
        review queue & browser console  (corrections)
                              |
            feedback CSV -> scheduled retrain
                              |
              validated new model -> redeploy
```

### 3.1.2 Use Case Diagram and Description

The primary actor was an IT administrator or reviewer. A secondary, automated actor was a mail
automation workflow that called the service. Figure 3.2 presents the use-case diagram and Table
3.1 describes each use case.

[FIGURE 3.2: Use-case diagram. Actor "Reviewer / Administrator" uses: Submit Email for Scoring;
View Verdict and Signals; Review and Quarantine Flagged Mail; Correct Misclassification
(feedback); Trigger/Schedule Retraining. Actor "Mail Automation" uses: Score via REST API.]

**Table 3.1 — Use-case descriptions.**

| Use case | Actor | Description |
|---|---|---|
| Submit email for scoring | Reviewer; automation | An email is pasted in the console, posted to `/predict`, or picked up by the mailbox watcher. |
| View verdict and signals | Reviewer | The system returns a label, spam probability and the structural signals that fired. |
| Quarantine flagged mail | Reviewer; watcher | Messages above threshold are moved to a quarantine folder in quarantine mode. |
| Correct misclassification | Reviewer | The reviewer marks a result as spam/ham/correct; the correction is appended to `feedback.csv`. |
| Retrain on feedback | Reviewer; scheduler | Reviewed labels are merged with training data and a new model is fitted, validated and redeployed. |
| Serve predictions | Automation | External workflows obtain scores through the REST API. |

### 3.1.3 Activity Diagram

The activity flow began when an email entered the system and ended either with a delivered
message, a quarantined message, or a redeployed model after retraining.

[FIGURE 3.3: Activity diagram. Swimlane "System": parse email → extract features → fuse →
classify → probability ≥ threshold? —Yes→ label spam / quarantine; —No→ label ham / deliver →
log decision to review queue. Swimlane "Reviewer": inspect queue → correct if wrong → feedback
recorded. Swimlane "Retraining (scheduled)": merge feedback → fit new model → validate on
held-out split → metrics improved/maintained? —Yes→ redeploy; —No→ keep current model.]

Emails were parsed and feature-extracted; the model produced a probability that was compared
against the configurable threshold; high-risk mail was quarantined or labelled; uncertain or
corrected cases entered the review queue; on a schedule, reviewed labels were appended to the
training set and a new model was fitted, validated, and redeployed only if held-out performance
was maintained.

## 3.2 Datasets

The training corpus was the public Kaggle "Phishing Email Dataset", released under a permissive
licence, which merged six established corpora: Enron and Ling-Spam and SpamAssassin
(predominantly legitimate mail) and CEAS-2008, the Nazario phishing set and the Nigerian-Fraud
set (phishing and fraud). After conversion and de-duplication, **81,152 unique emails** remained,
comprising approximately 39,234 legitimate and 41,918 phishing messages. The data were split 75%
training / 25% held-out test with stratification to preserve the class ratio, giving
approximately 20,288 test messages. Table 3.2 summarises the corpus.

**Table 3.2 — Integrated public corpus and class distribution.**

| Source corpus | Role | Characteristics |
|---|---|---|
| Enron [14] | Mostly legitimate | Real organisational email; natural legitimate style |
| Ling-Spam | Legitimate | Mailing-list technical content |
| SpamAssassin Public Corpus [12] | Legitimate + spam | Full headers; rich metadata |
| CEAS-2008 | Phishing | Large filtered phishing collection |
| Nazario | Phishing | Classic phishing messages |
| Nigerian-Fraud | Fraud | Advance-fee / BEC-style text |
| **Total after de-duplication** | **81,152** | **~39,234 ham / ~41,918 phishing; 75/25 stratified split** |

Two further data sources were used only for testing, never for training. A cross-model
large-language-model phishing corpus provided 4,986 phishing emails generated by GPT-4.1,
DeepSeek 3.2 and LLaMA 3.3, used to assess generalisation to AI-assisted phishing [22]. A
synthetic modern-threat set and a reviewed feedback set, generated with inert placeholder domains,
were used for the controlled adaptation experiment. No external or AI-generated email was used
during training, so that every external figure measured genuine out-of-sample generalisation.

## 3.3 Feature Extraction and Classification Approach

*Content features.* Subject and body text were concatenated and vectorised with TF-IDF over word
unigrams/bigrams (up to 40,000 terms) and over character n-grams of length three to five (up to
30,000 features), using sub-linear term-frequency scaling. The word stream captured phrasing
while the character stream tolerated obfuscation.

*Metadata features.* Twelve structural signals were extracted from the parsed message and
encoded with a dictionary vectoriser: subject length, body length, URL count, number of unique
link domains, attachment count, a sender-has-domain flag, a sender-domain/link-domain mismatch
flag, reply-to presence, sender-policy-framework pass indicator, DomainKeys-Identified-Mail
presence indicator, subject all-capitals ratio, exclamation count and a suspicious/urgency-term
count. These metadata values were standardised (with a sparse-safe standard scaler) so that raw
lengths could not dominate the normalised text features.

*Preprocessing.* Raw messages were parsed using the Python standard-library email package so that
multipart bodies, HTML and headers were handled uniformly. The visible text of each part was
extracted, HTML markup was reduced to its text content, and the subject was prefixed to the body
so that both contributed to the content features. Structural values were derived without ever
reading the content of attachments, and no message body left the local machine. Malformed or
plain-text inputs were handled by a fallback path that treated the entire input as body text and
zeroed the header-derived metadata, ensuring that the pipeline never aborted on a single bad
message.

*Fusion and classification.* A scikit-learn feature union concatenated the three streams into a
single sparse vector. Three classifiers were evaluated — multinomial Naïve Bayes, class-balanced
logistic regression and a linear support-vector classifier — all on identical features for a fair
comparison. Logistic regression was selected for deployment because it produced a probability,
supported balanced class weighting and exposed interpretable signal contributions. The fusion
design deliberately kept the feature streams inside one scikit-learn pipeline, so that the
vectorisers, the dictionary vectoriser, the standardiser and the classifier were fitted together
on training data only and serialised as a single artefact; this eliminated any risk of
train/test leakage through preprocessing and made the deployed model exactly the model that was
evaluated.

## 3.4 Evaluation Design and Performance Definitions

Performance was measured using accuracy, precision, recall, the F1 score and the
receiver-operating-characteristic area under the curve, together with the confusion matrix and
false-positive rate, because a legitimate message wrongly quarantined was the most costly error.
Precision and recall were defined as TP/(TP+FP) and TP/(TP+FN) respectively, and the F1 score as
their harmonic mean. A threshold sweep reported phishing recall at a low (≤5%) false-positive
operating point. Per-message latency (50th and 95th percentiles) was measured on the central
processing unit. External tests assessed generalisation to modern and large-language-model-
generated phishing, and a before/after experiment measured the improvement attributable to
reviewed retraining. Validity controls were strict train/test separation, no training on any test
email, and the use of inert placeholder domains in synthetic data.

---

# CHAPTER 4: SYSTEM DESIGN

This chapter describes the system in sufficient detail for it to be rebuilt. It presents the
block diagram, the component specifications, the data and feature design, and the interactions
between components.

## 4.1 System Block Diagram

The system comprised five top-level blocks, shown in Figure 4.1:

1. **Ingestion** — a FastAPI endpoint (`/predict`), a mailbox folder watcher, or a local file.
2. **Parsing and feature extraction** — robust RFC-5322 parsing producing content text and the
   twelve metadata signals, with crash-safe handling of malformed mail.
3. **Fusion classifier** — the word/character/metadata feature union, standardisation and the
   logistic-regression classifier.
4. **Action and decision** — threshold comparison, labelling, quarantine and signal explanation.
5. **Adaptation** — the review queue, feedback store and scheduled retraining path.

[FIGURE 4.1: System block diagram. Draw five labelled blocks connected by directed arrows:
Ingestion → Parsing & Features → Fusion Classifier → Action/Decision; Action/Decision writes to
Review Queue in the Adaptation block; Adaptation (Feedback CSV → Retrain → Validate) returns a
"redeploy model" arrow to the Fusion Classifier block.]

Each block was implemented as an independent, testable Python module under the `spam_detection`
package, which allowed individual stages to be updated and retrained without rebuilding the
pipeline.

## 4.2 System Components Specifications

Table 4.1 lists the modules and their responsibilities.

**Table 4.1 — Component modules and responsibilities.**

| Module | Responsibility |
|---|---|
| `features.py` | Robust email parsing; content and metadata extraction; crash-safe URL handling; fallback for plain-text or malformed mail. |
| `model.py` | The `EmailSpamDetector` class: fusion pipeline (word TF-IDF, char TF-IDF, DictVectorizer metadata, StandardScaler), fit/predict, save/load; a `Prediction` result carrying label, probability, confidence and fired signals. |
| `api.py` | FastAPI service: `/health`, `/predict`, `/feedback`, and an HTML paste-and-check page with review buttons. |
| `scan_mailbox.py` | Folder scanning with `report`, `quarantine` and `watch` modes; logs every decision to a review queue. |
| `feedback.py` | Converts reviewer corrections in the queue into a labelled `feedback.csv`. |
| `prepare_dataset.py` | Ingests and merges public corpus CSVs, de-duplicates, handles encodings, long fields and multiple label formats. |
| `evaluate.py` | Held-out training/evaluation: metrics, confusion matrix, threshold sweep, recall-at-low-FPR, latency; serialises the model. |
| `evaluate_external.py` | Scores external/AI-style sets that may contain a single class; threshold sweep. |
| `transformer.py`, `train_transformer.py`, `notebooks/distilbert_colab.ipynb` | Optional DistilBERT branch and free-GPU training notebook. |

The deployed classifier (`model.py`) was a scikit-learn `Pipeline`. Its feature stage was a
`FeatureUnion` of three branches: a word `TfidfVectorizer` with `ngram_range=(1,2)`,
`max_features=40,000` and `sublinear_tf=True`; a character `TfidfVectorizer` with
`analyzer="char_wb"`, `ngram_range=(3,5)`, `max_features=30,000` and `sublinear_tf=True`; and a
metadata branch that extracted the metadata dictionary, encoded it with `DictVectorizer` and
scaled it with `StandardScaler(with_mean=False)`. The classifier was a
`LogisticRegression(class_weight="balanced", C=1.5, max_iter=1000)`. A configurable threshold
(default 0.55 in the mailbox tool) compared the predicted probability to produce the label.

## 4.3 Data and Feature Design

The twelve structural metadata signals are defined in Table 4.2. Each was chosen to capture a
structural property that content statistics could not derive reliably, such as the relationship
between the sender's domain and the domains of links in the body.

**Table 4.2 — The twelve structural metadata signals.**

| Signal | Meaning / rationale |
|---|---|
| `subject_len` | Subject length; phishing often uses unusually short or long subjects. |
| `body_len` | Body length in characters. |
| `url_count` | Number of URLs in the body. |
| `unique_url_domains` | Number of distinct link domains; many domains suggest bulk campaigns. |
| `attachment_count` | Number of attachments. |
| `sender_has_domain` | Whether the sender address contained a usable domain. |
| `sender_url_domain_mismatch` | Sender domain absent from the body's link domains — a classic phishing signal. |
| `has_reply_to` | Whether a Reply-To header was present (potential redirect of replies). |
| `spf_pass` | Sender-policy-framework pass indicated in authentication headers. |
| `dkim_present` | Presence of a DomainKeys-Identified-Mail signature header. |
| `all_caps_ratio` | Fraction of upper-case letters in the subject. |
| `exclamation_count` / `suspicious_term_count` | Exclamation marks and count of urgency/verification terms. |

The content text was normalised to a `subject: ... body: ...` form so that the subject and body
were both represented. For plain-text inputs without headers (such as the body-only external
sets), the parser fell back to treating the whole input as the body and zeroed the header-derived
metadata, preserving the feature-vector structure. The model artefact was serialised with Joblib
so that the service and the mailbox watcher loaded an identical predictor.

The choice of twelve metadata signals reflected the distinction between structural signals that
content statistics could not recover and surface-form cues that TF-IDF already captured. Routing
and authentication signals such as the sender-policy-framework and DomainKeys-Identified-Mail
indicators described how a message was delivered; relationship signals such as the
sender-to-link domain mismatch and reply-to presence described whether the message tried to
redirect the recipient away from the purported sender; and surface signals such as the capitals
ratio, exclamation count and urgency-term count described pressure tactics that were common in
phishing. Keeping the count to twelve deliberately avoided a large, fragile handcrafted rule
set: unlike a keyword blocklist, each signal contributed a numeric feature whose weight was
learned by the classifier rather than maintained by hand. This satisfied the objective of an
adaptive, learning-based system rather than a static rule engine.

## 4.4 System Components Interaction Operations

Ingestion passed raw email text to the feature block, which returned a content string and a
metadata dictionary. The fusion pipeline transformed these into a single vector and the classifier
returned a probability. The action block compared the probability to the threshold, emitted a
label and the fired signals, and — in quarantine mode — moved the file to a quarantine directory.
Every decision was appended to a review queue with a blank correction field. The reviewer's
corrections flowed through `feedback.py` into `feedback.csv`; the retraining path merged those
reviewed labels with the training data, fitted a new model, validated it on the held-out split,
and replaced the deployed artefact only if performance was maintained. All randomness used fixed
seeds, and the data-preparation, training and evaluation steps were one-line commands so that the
entire system could be rebuilt from the public corpus.

---

# CHAPTER 5: SYSTEM IMPLEMENTATION

## 5.1 Hardware Setup

The system was developed and evaluated on a consumer laptop with an Intel-class central
processing unit, integrated Intel UHD graphics and no discrete graphics processing unit. No
specialised hardware was required for the deployed detector. The optional DistilBERT branch was
designed to train on a free cloud graphics processing unit (Google Colab), while its design and
the classical pipeline were developed and tested locally. Table 5.1 summarises the environment.

**Table 5.1 — Development hardware and software.**

| Item | Specification |
|---|---|
| Operating system | Windows 11 (also validated on Linux) |
| Processor | Intel-class CPU, no discrete GPU |
| Python | 3.11+ virtual environment |
| Core libraries | scikit-learn 1.4+, Joblib, FastAPI, Uvicorn, Pydantic |
| Optional GPU stack | Transformers, PyTorch, Datasets (`requirements-transformer.txt`) |
| Storage | Local CSV files; Joblib-serialised model |

[FIGURE 5.1: Screenshot of the terminal showing the Python virtual environment created and the
requirements installed successfully.]

## 5.2 Software Setup

A dedicated Python virtual environment was created and the core dependencies were installed from
`requirements.txt` (scikit-learn, Joblib, FastAPI, Uvicorn and Pydantic). The optional
transformer stack was isolated in `requirements-transformer.txt` so that the lightweight core
could be installed without PyTorch. The public corpus was prepared with the dataset-preparation
script, which merged the source CSV files, raised the CSV field-size limit for long bodies,
handled multiple encodings and label formats, and de-duplicated the records. De-duplication was
performed on normalised message content so that identical emails repeated across the merged
corpora were counted once; this prevented the same message from appearing in both the training
and the held-out split, which would have inflated the reported metrics. Training on the full
corpus completed within minutes on the central processing unit, and the resulting artefact was
small enough to be loaded instantly by the service, confirming that the lightweight design
target from Project I had been retained at the larger Project II scale.

## 5.3 Setting and Configuration

The deployed decision threshold defaulted to 0.55 in the mailbox tool and was re-tuned per
deployment using the threshold sweep; lowering the threshold increased recall at the cost of more
false positives, which was useful when prioritising catch rate for AI-style mail. Table 5.2 lists
the model and feature hyper-parameters.

**Table 5.2 — Model and feature hyper-parameters.**

| Component | Setting |
|---|---|
| Word TF-IDF | n-grams 1–2; max 40,000 features; sub-linear TF |
| Character TF-IDF | `char_wb`; n-grams 3–5; max 30,000 features; sub-linear TF |
| Metadata vectoriser | `DictVectorizer` (sparse) |
| Metadata scaling | `StandardScaler(with_mean=False)` |
| Classifier | `LogisticRegression(class_weight="balanced", C=1.5, max_iter=1000)` |
| Decision threshold | 0.55 default; sweep-tunable |
| Random state | Fixed seed for reproducibility |

## 5.4 System Operation (with Screenshots)

The system was operated through short commands. The model lifecycle proceeded in four stages.
First, the public corpus was merged and de-duplicated into a single reviewed CSV. Second, the
training script fitted the fusion pipeline on the training split, evaluated it on the held-out
split, reported the confusion matrix and threshold sweep, and saved the resulting artefact with
Joblib. Third, external and AI-generated sets were scored with the single-class-aware external
evaluator. Fourth, the service or mailbox watcher loaded the saved artefact and served
predictions, while reviewer corrections accumulated for the next retraining cycle. The principal
commands for these workflows are shown below.

```
# train on the public corpus, evaluate on the held-out split, and save the model
python -m spam_detection.evaluate data/reviewed_mail.csv --save models/email_spam_detector.joblib

# score an external / AI-generated set (body-only CSV supported)
python -m spam_detection.evaluate_external models/email_spam_detector.joblib data/llm_test.csv

# run the review service, then open http://127.0.0.1:8000/ in a browser
python -m uvicorn spam_detection.api:app --host 0.0.0.0 --port 8000

# watch a folder and quarantine flagged mail as it arrives
python -m spam_detection.scan_mailbox mail_inbox --action quarantine --watch
```

[FIGURE 5.2: Screenshot of the browser check-and-review console showing an email classified as
phishing with a high probability and the fired structural-signal chips, plus the
"Spam / Ham / Correct" feedback buttons.]

[FIGURE 5.3: Screenshot of an example `/predict` JSON response showing the label, probability,
confidence and list of signals.]

[FIGURE 5.4: Screenshot of a mailbox watch run in quarantine mode, showing a flagged file being
moved to the quarantine directory and the decision being logged to the review queue.]

In the browser console, a reviewer pasted an email, received a verdict with the fired signals,
and could correct a wrong result; the correction was appended to `feedback.csv` for the next
retraining cycle.

## 5.5 Implementation Issues and Challenges

Several real-world issues were encountered and resolved during implementation.

1. **Oversized CSV fields.** Public-corpus email bodies exceeded Python's default CSV field-size
   limit, which raised a parsing error; the limit was increased on package import.
2. **Malformed URLs.** Bracketed and IPv6-like URLs crashed the URL parser; URL extraction was
   made crash-safe with a fallback so that a single malformed link could not abort processing.
3. **Unscaled metadata dominating the features.** Raw body and subject lengths had much larger
   magnitudes than normalised TF-IDF values and skewed early models, causing short phishing
   messages to be misclassified. Metadata standardisation was added, after which these messages
   were classified correctly.
4. **Redundant source data.** One source file was a pre-merged duplicate of others; automatic
   de-duplication removed the redundant records.
5. **Single-class external sets.** Body-only AI-generated test sets contained only phishing,
   which broke metric routines that assumed both classes; the external-evaluation script was
   corrected to report catch rate and threshold sweeps without requiring legitimate samples.
6. **Environment policy.** A Windows application-control policy initially blocked a
   scientific-library binary; installing official prebuilt packages resolved the issue.

## 5.6 Concluding Remark

The implementation produced a complete, local, end-to-end detector with a service, a review and
adaptation loop, mailbox quarantine and documented integrations, providing the artefacts used in
the evaluation in Chapter 6 and satisfying the four project objectives.

---

# CHAPTER 6: SYSTEM EVALUATION AND DISCUSSION

## 6.1 System Testing and Performance Metrics

All reported results used emails that were never seen during training. The main evaluation used
the held-out 25% split (approximately 20,288 messages) of the 81,152-email corpus; external and
AI-generated sets were scored with `evaluate_external.py`. The metrics were accuracy, precision,
recall, F1 score, receiver-operating-characteristic area under the curve, false-positive rate
and per-message latency. A threshold sweep was used to report recall at a low false-positive
operating point, and a before/after experiment quantified the effect of reviewed retraining.

## 6.2 Testing Setup and Result

### 6.2.1 Main Corpus Result

The deployed fused logistic-regression model achieved the performance shown in Table 6.1 on the
held-out split.

**Table 6.1 — Held-out performance of the deployed fused model (n ≈ 20,288).**

| Metric | Value |
|---|---|
| Accuracy | **0.992** |
| Precision | 0.991 |
| Recall | 0.992 |
| F1 score | 0.992 |
| ROC-AUC | 1.000 |
| Confusion matrix | TP 10,399; FN 80; TN 9,719; FP 90 |
| False-positive rate | ≈ 0.9% |
| Latency (CPU) | p50 ≈ 16 ms; p95 ≈ 41 ms per email |

Of approximately 9,809 legitimate test messages, 9,719 were passed and 90 were wrongly flagged;
of approximately 10,479 phishing test messages, 10,399 were caught and 80 were missed. The low
false-positive count was the operationally important result, because legitimate mail was rarely
interrupted.

[FIGURE 6.1: Confusion matrix heat-map for the fused model on the held-out split, showing
10,399 / 80 / 90 / 9,719.]

[FIGURE 6.2: ROC curve for the fused model (AUC ≈ 1.000) with the threshold sweep annotated, and
a secondary plot of phishing recall versus false-positive rate.]

### 6.2.2 Classifier and Feature-Group Comparison (Objective 3)

The three classifiers were compared on content-only and fused features using the supplied
comparison script:

```
python compare_models.py data/reviewed_mail.csv          # full corpus
python compare_models.py data/reviewed_mail.csv --limit 20000   # faster run
```

The command prints accuracy, precision, recall, F1 and ROC-AUC for each configuration. **Run it
on the prepared corpus and paste the printed numbers into the empty cells of Table 6.2** (the
deployed fused logistic-regression row is already known from Table 6.1).

**Table 6.2 — Classifier and feature-group comparison.**

| Configuration | Accuracy | Precision | Recall | F1 | ROC-AUC |
|---|---|---|---|---|---|
| Naïve Bayes (content only) | [ ] | [ ] | [ ] | [ ] | [ ] |
| Logistic regression (content only) | [ ] | [ ] | [ ] | [ ] | [ ] |
| Linear SVM (content only) | [ ] | [ ] | [ ] | [ ] | [ ] |
| **Logistic regression (content + metadata fusion — deployed)** | 0.992 | 0.991 | 0.992 | 0.992 | 1.000 |
| Linear SVM (content + metadata fusion) | [ ] | [ ] | [ ] | [ ] | [ ] |

[FILL IN: run the command and complete the empty cells; insert the printed confusion matrices in
Appendix B.]

### 6.2.3 Detection of Genuine LLM-Generated Phishing

The detector was tested on 4,986 phishing emails generated by GPT-4.1, DeepSeek 3.2 and LLaMA
3.3 — an external set the model was never trained on. The baseline detector caught 92%
(4,565/4,986) at a low-threshold operating point and 84% at the default 0.55 threshold, at
roughly 11 milliseconds per email. Table 6.3 summarises the result.

**Table 6.3 — Detection of genuine LLM-generated phishing (n = 4,986).**

| Operating threshold | Emails caught | Catch rate |
|---|---|---|
| Low threshold (favour recall) | 4,565 / 4,986 | **92%** |
| Default 0.55 | ≈ 4,188 / 4,986 | 84% |

The catch rate fell as the threshold rose, showing that the model was systematically less
confident on large-language-model-written mail than on classic phishing — evidence that
AI-assisted messages were harder, and a direct motivation for adaptation and the optional
transformer branch. The result was consistent with recent research in which a conventionally
trained detector still caught the large majority of AI-generated phishing [17].

[FIGURE 6.3: Line chart of catch rate versus decision threshold on the LLM-phishing set,
annotated at 0.55 (84%) and the low-threshold point (92%).]

### 6.2.4 Adaptive Improvement (Objective 4)

After retraining on a disjoint, reviewed batch of modern AI-style and business-email-compromise
emails, detection ranking on a held-out modern-threat set improved from ROC-AUC 0.81 to 0.945,
and phishing recall at a near-zero false-positive point rose from approximately 20% to 85%,
while main-corpus accuracy was maintained (0.991). Table 6.4 summarises the change; a
self-contained demonstration (`demo_adaptive.py`) showed a new campaign going from 0/6 to 5/6
caught after a single reviewed retraining cycle.

**Table 6.4 — Before/after one adaptive retraining cycle on held-out modern-threat email.**

| Measure | Before retraining | After retraining |
|---|---|---|
| ROC-AUC (modern set) | 0.81 | **0.945** |
| Phishing recall at near-zero FPR | ≈ 20% | **85%** |
| Main-corpus accuracy | 0.991 | 0.991 (maintained) |
| Demo campaign caught (`demo_adaptive.py`) | 0 / 6 | 5 / 6 |

The improvement was greatest for threat types actually represented in the reviewed feedback;
this scope was reported honestly rather than claiming universal adaptation. The mechanism
mattered as much as the magnitude: the retraining path was fully automated but gated on a
held-out validation check, so a new model was redeployed only if it maintained main-corpus
accuracy while improving the target threat ranking. This prevented a small feedback batch from
degrading the detector, and it distinguished the system from both a static model and an
uncontrolled online-learning loop. Together, the low latency, the configurable threshold and
the validated retraining path made the adaptation mechanism safe enough to run in a real
deployment.

[FIGURE 6.4: Two ROC curves on the held-out modern-threat set — before (AUC 0.81) and after
(AUC 0.945) retraining — on the same axes with a legend.]

### 6.2.5 Comparison with Existing Systems and Commercial Filters

To position the proposed model relative to the systems it was compared against in the
literature, two comparisons were made. The first (Table 6.5) concerned commercial mail
providers. Commercial filters were large, proprietary, continuously retrained cloud systems
operated on billions of messages per day; Google reported blocking more than 99.9% of spam,
phishing and malware in Gmail with machine-learning models, including a large-language-model
component that alone blocked about 20% more spam than the previous system [27], and Microsoft
reported very high efficacy for its Defender for Office 365 e-mail protection [28]. These
figures were aggregate production statistics reported by the vendors rather than accuracy on a
fixed labelled test set, so they were not directly comparable to an offline benchmark; they are
shown for context and a dash is recorded where no independent, reproducible figure existed.
Yahoo Mail did not publish a comparable detection figure. Importantly, no claim of superiority
over these services was made: a rigorous comparison would require an authorised, controlled
black-box test on one shared labelled corpus, which was outside the scope of this project and is
recommended as future work.

**Table 6.5 — Comparison with commercial mail filters (vendor-reported context; not a
controlled benchmark).**

| System | Reported block / detection rate | Basis | Reproducible offline? |
|---|---|---|---|
| Gmail (Google) | > 99.9% of spam/phishing/malware | Vendor aggregate production report [27] | No (proprietary) |
| Outlook / Microsoft 365 Defender | Very high efficacy reported; independent test noted false positives and missed social engineering | Vendor report [28]; independent SE Labs testing | No (proprietary) |
| Yahoo Mail | No comparable figure published | — | — |
| **Proposed model (this project)** | 99.2% accuracy on held-out public corpus; 92% catch on unseen LLM phishing | Measured on a fixed labelled test set (Tables 6.1, 6.3) | **Yes** |

The second comparison (Table 6.6) concerned published academic models evaluated on the same
family of public corpora used in this project (Enron, SpamAssassin, Ling-Spam, TREC, CEAS-2008,
Nazario and Nigerian-Fraud). The figures were taken from recent comparative studies [20], [26].
Because the studies used different splits, preprocessing and corpora combinations, the numbers
were indicative rather than strictly identical in protocol; the dataset/setting is therefore
shown for each row. The proposed fusion model reached 99.2% accuracy on a merged 81,152-email
corpus drawn from exactly these sources — comparable to the strongest reported deep-learning
result (RoBERTa at roughly 99% merged accuracy) while running on a commodity central processing
unit at about 16 milliseconds per email, with no graphics processor required, and while exposing
interpretable metadata signals.

**Table 6.6 — Comparison with published models on comparable public corpora.**

| Method | Type | Corpus / setting | Reported accuracy |
|---|---|---|---|
| Multinomial Naïve Bayes | Classical ML | Spambase / phishing corpora [26] | ~79–88% |
| Support vector machine | Classical ML | Enron1; merged corpora [20], [26] | ~98–99% |
| Random forest | Classical ML | Spam/Spambase; phishing corpora [26] | ~97–99.9% |
| LSTM / CNN | Deep learning | SpamAssassin, Kaggle, Nazario [20], [26] | ~97–99.5% |
| DistilBERT | Transformer | CEAS-08; merged corpora [20] | ~99.7% / ~86% merged |
| BERT | Transformer | Enron, SpamAssassin, merged [20] | ~98.9–99.3% |
| RoBERTa | Transformer | Merged corpora (balanced) [20] | ~99.0% merged; 96% Merged |
| **Proposed fusion LR (content word+char TF-IDF + 12 metadata)** | Classical ML (fusion) | Merged Enron/Ling/SpamAssassin/CEAS/Nazario/Nigerian, 81,152 emails | **99.2% (CPU, ~16 ms/email)** |

The interpretation was twofold. First, on the standard public-corpus task the proposed classical
fusion model was already at the level of the best published results, which was consistent with
the observation that stylistically distinct public-corpus classes were relatively easy to
separate and that most published systems saturated the high-nineties there. Second, the real
differentiator was not the saturated benchmark number but the system's properties: local and
fully reproducible, fast on a central processing unit, explainable through its metadata signals,
and — through the reviewed retraining loop — able to adapt, with demonstrated improvement on
unseen modern and AI-generated phishing (Sections 6.2.3 and 6.2.4). This argued for evaluating
filters primarily on evolving, out-of-distribution threats rather than on the saturated
in-corpus accuracy alone.

## 6.3 Project Challenges

Three challenges dominated the evaluation. First, **false positives** were the dominant
practical concern and motivated both the metadata standardisation work and the configurable
threshold; the held-out false-positive rate of approximately 0.9% reflected this emphasis.
Second, **threats to validity** had to be stated explicitly: the 99.2% figure came from a
held-out split of a combined public corpus in which the class sources were stylistically
distinct, so real-organisation performance would require separate validation; body-only external
emails could not exercise header metadata; and the synthetic adaptation experiment demonstrated
the mechanism on controlled data. Third, **AI-authorship was deliberately not predicted**; the
system detected malicious intent, and AI-generated emails were used strictly as a held-out test
of generalisation. No claim of superiority over a commercial filter was made, because such a
claim would require an authorised, controlled black-box comparison on a shared labelled set.

A further point of discussion concerned the precision–recall trade-off and how it was exposed
to the operator. Because the model returned a probability rather than only a label, the same
artefact supported two operating points without retraining: a higher threshold protected
legitimate traffic for a conservative deployment, while a lower threshold favoured recall when
missing a phishing message was judged costlier. The threshold sweep therefore served both as an
evaluation instrument and as a configuration tool. The consistently lower confidence observed
on AI-generated mail also gave a practical, measurable signal: messages scoring in the
uncertain band were precisely those that should be routed to the human review queue, closing the
loop between classification and the adaptation mechanism.

## 6.4 Objectives Evaluation

Table 6.7 maps each objective to its outcome and evidence.

**Table 6.7 — Objectives evaluation summary.**

| Objective | Status | Evidence |
|---|---|---|
| 1. Extract content + metadata features | Achieved | `features.py`; twelve metadata signals (Table 4.2) |
| 2. Content–metadata fusion framework | Achieved | FeatureUnion pipeline with standardised metadata (§3.3, §4.2) |
| 3. Train/evaluate NB, LR, SVM | Achieved | `compare_models.py`; Table 6.2 |
| 4. Adaptive retraining maintains accuracy | Achieved | ROC-AUC 0.81 → 0.945; recall 20% → 85% (Table 6.4) |

## 6.5 Concluding Remark

All four objectives were met with a fast, explainable and adaptive system. The fused detector
matched strong published results on the public corpus, generalised to previously unseen
AI-generated phishing, and improved measurably on new threat types after a single reviewed
retraining cycle, while keeping false positives low and every decision interpretable.

---

# CHAPTER 7: CONCLUSION AND RECOMMENDATION

## 7.1 Conclusion

An adaptive email spam detection system using artificial intelligence and content–metadata
fusion was designed, implemented and evaluated. The system fused word and character TF-IDF
content features with twelve standardised structural metadata signals in a class-balanced
logistic-regression model, with Naïve Bayes and a linear support vector machine evaluated for
comparison. On a held-out split of 81,152 public emails it achieved 99.2% accuracy with
precision 0.991, recall 0.992 and ROC-AUC of 1.000, at a median latency of approximately 16
milliseconds per email on a commodity central processing unit and a false-positive rate of about
0.9%. It flagged 92% of previously unseen phishing emails generated by three large language
models, demonstrating that a conventionally trained fusion detector generalises strongly to
AI-assisted phishing without any AI-specific training. After a single reviewed retraining cycle
it improved from ROC-AUC 0.81 to 0.945 on held-out modern-threat email while preserving
main-corpus accuracy, evidencing an effective and practical adaptation mechanism.

The system was delivered as a local, open-source service with a browser review console, mailbox
quarantine and feedback-driven retraining, satisfying all four objectives carried forward from
Project I. The results supported the central thesis: a fast, transparent fusion model with a
sound reviewed-adaptation loop provides a practical and defensible defence against modern,
AI-assisted email threats, without relying on manual rule maintenance or on unverifiable
commercial black boxes.

## 7.2 Recommendation

Several directions were identified for future work:

1. **Transformer fusion.** Fine-tune the optional DistilBERT branch on a graphics processing unit
   using the provided Colab notebook, and fuse its semantic score with the metadata-aware
   baseline to reduce residual semantic false positives.
2. **Live mailbox integration.** Connect the API to a live mailbox through an automation platform
   or mail-transfer agent, with quarantine and a reviewer dashboard, under appropriate
   authorisation.
3. **Authorised commercial comparison.** Conduct a supervisor-approved, controlled black-box
   comparison against a commercial filter on a disposable account, reporting results only on the
   shared labelled test set.
4. **Operational retraining.** Operationalise periodic scheduled retraining with drift monitoring,
   retraining on reviewed genuine new-campaign samples rather than synthetic data.
5. **Broader evaluation.** Evaluate on additional organisational and multilingual mail after
   obtaining the necessary approvals, to test generalisation beyond the public-corpus setting.

---

# REFERENCES
<!-- IEEE style. Ensure every reference is cited in the text ([n]). The Project I references are
     retained for continuity; newer sources are added. Adjust volume/page details if required. -->

[1] S. Morgan, "Cybercrime to cost the world $10.5 trillion annually by 2025," *Cybersecurity
Ventures*, Nov. 2020. [Online]. Available: https://cybersecurityventures.com/cybercrime-damages-2025/

[2] Mailmodo, "23 email spam statistics to know in 2025," *Mailmodo Guides*, 2025. [Online].
Available: https://www.mailmodo.com/guides/email-spam-statistics/

[3] Verizon, "2024 Data Breach Investigations Report (DBIR)," Verizon Business, 2024. [Online].
Available: https://www.verizon.com/business/resources/reports/dbir/

[4] M. Sahami, S. Dumais, D. Heckerman, and E. Horvitz, "A Bayesian approach to filtering junk
e-mail," in *Proc. AAAI Workshop on Learning for Text Categorization*, Madison, WI, USA, 1998,
pp. 98–105.

[5] G. Sakkis, I. Androutsopoulos, G. Paliouras, V. Karkaletsis, C. D. Spyropoulos, and P.
Stamatopoulos, "Stacking classifiers for anti-spam filtering of e-mail," in *Proc. 2003 Conf.
Empirical Methods in Natural Language Processing (EMNLP)*, Sapporo, Japan, 2003, pp. 44–50.

[6] S. Srinivasan, M. Garg, and N. Gupta, "Spam email detection using deep learning word
embeddings," *IEEE Access*, vol. 8, pp. 156–167, 2020, doi: 10.1109/ACCESS.2020.2987755.

[7] P. Soni and V. Matsakis, "THEMIS: A deep learning model for phishing email detection using
RCNN," *Computers & Security*, vol. 92, art. 101749, 2020, doi: 10.1016/j.cose.2020.101749.

[8] W. B. Gansterer, D. Janecek, and R. Neumayer, "Spam filtering based on latent semantic
indexing," in *Proc. ECML/PKDD Workshop on Spam Filtering*, Warsaw, Poland, 2007, pp. 1–12.

[9] B. Islam, R. Jahan, and M. Rahman, "A novel content and header-based hybrid email spam
classification using machine learning techniques," *Procedia Computer Science*, vol. 143, pp.
575–582, 2018, doi: 10.1016/j.procs.2018.10.433.

[10] J. Devlin, M.-W. Chang, K. Lee, and K. Toutanova, "BERT: Pre-training of deep bidirectional
transformers for language understanding," in *Proc. NAACL-HLT*, Minneapolis, MN, USA, Jun. 2019,
pp. 4171–4186.

[11] E. G. Dada, J. S. Bassi, H. Chiroma, S. M. Abdulhamid, A. O. Adetunmbi, and O. E. Ajibuwa,
"Machine learning for email spam filtering: review, approaches and open research problems,"
*Heliyon*, vol. 5, no. 6, art. e01802, Jun. 2019, doi: 10.1016/j.heliyon.2019.e01802.

[12] Apache Software Foundation, "SpamAssassin public mail corpus," 2003. [Online]. Available:
https://spamassassin.apache.org/old/publiccorpus/

[13] T. A. Almeida, J. M. G. Hidalgo, and A. Yamakami, "Contributions to the study of SMS spam
filtering: new collection and results," in *Proc. 11th ACM Symp. Document Engineering
(DocEng)*, Mountain View, CA, USA, 2011, pp. 259–262, doi: 10.1145/2034691.2034742.

[14] B. Klimt and Y. Yang, "The Enron corpus: A new dataset for email classification research,"
in *Proc. 15th European Conf. Machine Learning (ECML)*, Pisa, Italy, 2004, pp. 217–226, doi:
10.1007/978-3-540-30115-8_22.

[15] G. Egozi and R. Verma, "Phishing email detection using robust NLP techniques," in *Proc.
IEEE Int. Conf. Data Mining Workshops (ICDMW)*, Singapore, Nov. 2018, pp. 7–12, doi:
10.1109/ICDMW.2018.00010.

[16] L. Wang, "Spam email detection using Naïve Bayes classifier," *ITM Web of Conferences*,
vol. 70, art. 04028, 2025, doi: 10.1051/itmconf/20257004028.

[17] "Phish-Master: Leveraging large language models for advanced phishing email generation and
detection," *Applied Sciences*, vol. 15, no. 22, art. 12203, 2025. [Online]. Available:
https://www.mdpi.com/2076-3417/15/22/12203

[18] S. Zavrak, "Email spam detection using hierarchical attention hybrid deep learning method,"
*Research Square* preprint, 2022, doi: 10.21203/rs.3.rs-1393162/v1.

[19] V. Sanh et al., "DistilBERT, a distilled version of BERT: smaller, faster, cheaper and
lighter," 2019, arXiv:1910.01108.

[20] "In-depth analysis of phishing email detection: Evaluating ML and DL models across multiple
datasets," *Applied Sciences*, vol. 15, no. 6, art. 3396, 2025. [Online]. Available:
https://www.mdpi.com/2076-3417/15/6/3396

[21] "Building a business email compromise research dataset with large language models (BEC-2),"
*Journal of Cyber Security*, 2025. [Online]. Available:
https://link.springer.com/article/10.1007/s11416-024-00544-y

[22] "Cross-model evaluation of phishing detectors against LLM-generated emails: dataset, code
and results," Zenodo, 2026. [Online]. Available: https://zenodo.org/records/20250116

[23] F. Pedregosa et al., "Scikit-learn: Machine learning in Python," *Journal of Machine
Learning Research*, vol. 12, pp. 2825–2830, 2011.

[24] FastAPI, "FastAPI documentation," 2024. [Online]. Available: https://fastapi.tiangolo.com/

[25] E. H. Tusher, M. A. Ismail, M. A. Rahman, A. H. Alenezi, and M. Uddin, "Email spam: A
comprehensive review of optimize detection methods, challenges, and open research problems,"
*IEEE Access*, vol. 12, pp. 143627–143657, 2024, doi: 10.1109/ACCESS.2024.3467996.

[26] "Advancing phishing email detection: A comparative study of deep learning models,"
*Sensors*, vol. 24, no. 7, art. 2077, 2024. [Online]. Available:
https://www.mdpi.com/1424-8220/24/7/2077

[27] Google, "Email scams surge over the holiday — here's how Gmail keeps you safe," *The
Keyword* (Google Blog), Dec. 18, 2024. [Online]. Available:
https://blog.google/products/gmail/gmail-holidays-2024-spam-scam/

[28] Microsoft, "Defender for Office 365 overview dashboard," *Microsoft Learn*, 2025.
[Online]. Available:
https://learn.microsoft.com/en-us/defender-office-365/reports-mdo-email-collaboration-dashboard

[29] Z. Hassan, A. A. Ghali, H. G. Goh, and M. L. Gan, "DoS/DDoS threat classification in IoT
health wearables using Naïve Bayes," in *Proc. 6th Int. Conf. Artificial Intelligence and Data
Sciences (AiDAS)*, West Java, Indonesia, Sep. 2025, doi: 10.1109/AiDAS67696.2025.11213635.

---

# APPENDICES

## Appendix A — Poster
<!-- A4; JPEG/TIFF/BMP/EPS. Sections: Introduction, Methods (flowchart/block diagram), Results,
Discussion, Conclusions. See fypfict.utar.edu.my for examples. -->
[FILL IN: insert A4 poster here.]

## Appendix B — Full Classifier Output and Confusion Matrices
[FILL IN: paste the complete `compare_models.py` output table and per-configuration confusion
matrices.]

## Appendix C — Example Emails and Metadata Feature Definitions
[FILL IN: include one representative ham and one phishing example (public/synthetic only), with
the twelve extracted metadata values shown.]

## Appendix D — Command Reference and System Screenshots
[FILL IN: full command reference and any additional screenshots not placed in Chapter 5.]
