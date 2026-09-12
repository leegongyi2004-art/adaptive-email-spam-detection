# FYP2 Submission Checklist

Work top to bottom. Everything here is assembly — no new writing or experiments are required.
The report text itself is complete and its numbers are verified.

---

## 1. Front matter — fill in the blanks (about 20 minutes)

Open `REPORT_FYP2.docx` and search for `[FILL IN`. There are fifteen markers.

| Where | What to enter |
|---|---|
| Cover page | Your student ID |
| Cover page | Month and year of submission |
| Title page | Month and year of submission |
| Copyright page | Year |
| Declaration form | Signed FM-IAD-004 declaration |
| Turnitin form | Signed originality declaration |
| Approval form | Supervisor-signed approval |
| Table 5.1 | Laptop model, processor, RAM, storage, operating system |

Also confirm the **registered project title** matches the cover exactly. If the officially
registered title differs, the cover, title page, declaration and abstract heading must all be
changed to match it.

---

## 2. Figures — capture these screenshots

Each command below produces the screen you need. Insert each image at its `[FIGURE x.y: ...]`
marker and put the caption **below** the image.

| Figure | Command to run | What to capture |
|---|---|---|
| 5.1 | `.venv\Scripts\activate` then `pip list` | Terminal showing the activated environment and installed packages |
| 5.2 | `python -m uvicorn spam_detection.api:app --port 8000` then paste a phishing email | Browser console showing the SPAM verdict, probability bar and signal chips |
| 5.3 | Same server, use the console or a client on `/predict` | The JSON response with label, probability, confidence and signals |
| 5.4 | `python -m spam_detection.scan_mailbox mail_inbox --action quarantine` | Terminal showing messages scored and one moved to quarantine |
| 5.5 | Already captured — your IMAP run | Terminal showing 27.4% / 97.6% / 98.7% / 99.8% |
| 5.6 | Open `http://localhost:8000` and scroll to Review inbox | The queued messages with confirm/correct buttons and the retrain button |

Figures 1.1 to 4.1 are already generated in `reports/figures/`.
Figures 6.1 to 6.4 are produced by `python reports/make_result_figures.py`.

**Formatting rules for every figure:** caption below, numbered per chapter, axes labelled with
units, at most two or three curves per graph, legend present, and each figure referred to *and*
explained in the text. The report text already does the referring and explaining.

---

## 3. Appendices

| Appendix | Content | How to produce it |
|---|---|---|
| A | Poster | Your poster, A4 or A3 |
| B | Classifier output | Paste `verify_all.txt` — the verification run |
| C | Example emails | One legitimate and one phishing email with their thirteen metadata values |
| D | Weekly logs | Six signed progress report forms |
| E | Turnitin | The originality report — **start this today** |
| F | Checklist | The completed FM-IAD-005 submission form |

For Appendix C, the thirteen metadata values are: subject length, body length, URL count,
unique URL domains, attachment count, sender has domain, sender/URL domain mismatch, reply-to
present, SPF pass, DKIM present, all-caps ratio, exclamation count, suspicious term count.

---

## 4. Verification — already complete

The following were measured against the real corpus and match the report:

```
corpus rows      81,152        held-out rows  20,288
accuracy 0.992   precision 0.991   recall 0.992   F1 0.992
ROC-AUC 1.000    false-positive rate 0.009
confusion matrix TN=9,719  FP=90  FN=80  TP=10,399
latency          p50 13 ms   p95 33 ms
AI phishing      4,565/4,986 = 92% at threshold 0.30; 84% at 0.55
adaptation       ROC-AUC 0.810 to 0.945
```

Keep `verify_all.txt`. It is the evidence that every number in Chapter 6 is reproducible.

To re-run at any time:

```
python examples\verify_report_numbers.py > verify_all.txt
```

---

## 5. Before you submit

- [ ] All fifteen `[FILL IN` markers replaced
- [ ] All twenty-one figures inserted with captions below
- [ ] Every figure referred to in the text (already written)
- [ ] Header on every chapter page, page numbers in the footer
- [ ] Roman numerals for front matter, Arabic from Chapter 1
- [ ] Reference list checked against the citations used
- [ ] `python reports/check_abbreviations.py` run and the list updated
- [ ] Turnitin submitted: title page, abstract, Chapters 1 to 7 and references only —
      no cover, declaration, acknowledgements, contents, lists or appendices
- [ ] Supervisor has signed the six weekly logs and the approval form

---

## What is deliberately not being done

These were considered and ruled out; none is required to pass.

- Adding more training data — the corpus is saturated at 99.2% and matches the published
  benchmark on the same data
- Training on AI-generated email — it would destroy the generalisation result, which is the
  most valuable finding in the report
- Adding new datasets such as the human/LLM 2x2 set — useful as future work only
- Regenerating the base corpus — it reproduces exactly at 81,152 and must not be rebuilt
- Building an automatic retraining loop — the human checkpoint is a security control and is
  justified in Section 7.2
