"""Build the FYP2 viva slide deck.

Produces reports/slides/fyp2_viva.pptx: twelve 16:9 slides sized for an
18-minute presentation, each carrying only headline figures and a diagram
placeholder, with the spoken script in the PowerPoint speaker notes.

Run:  python reports/make_slides.py
"""
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Emu, Inches, Pt

OUT = Path("reports/slides/fyp2_viva.pptx")

NAVY = RGBColor(0x0B, 0x2B, 0x5B)
BLUE = RGBColor(0x1A, 0x73, 0xE8)
INK = RGBColor(0x1F, 0x2A, 0x37)
GREY = RGBColor(0x5B, 0x66, 0x72)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
PANEL = RGBColor(0xEF, 0xF4, 0xFB)

W, H = Inches(13.333), Inches(7.5)


def _text(frame, runs, space_after=6):
    """Fill a text frame: runs is a list of (text, size, bold, colour)."""
    frame.word_wrap = True
    for i, (text, size, bold, colour) in enumerate(runs):
        para = frame.paragraphs[0] if i == 0 else frame.add_paragraph()
        para.space_after = Pt(space_after)
        run = para.add_run()
        run.text = text
        run.font.size = Pt(size)
        run.font.bold = bold
        run.font.color.rgb = colour
        run.font.name = "Calibri"
    return frame


def _box(slide, x, y, w, h, fill=None, line=None):
    from pptx.enum.shapes import MSO_SHAPE
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h)
    shape.adjustments[0] = 0.06
    if fill is None:
        shape.fill.background()
    else:
        shape.fill.solid()
        shape.fill.fore_color.rgb = fill
    if line is None:
        shape.line.fill.background()
    else:
        shape.line.color.rgb = line
        shape.line.width = Pt(1.25)
    shape.shadow.inherit = False
    return shape


def _slide(prs, title, kicker=""):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    bar = slide.shapes.add_shape(1, 0, 0, W, Inches(1.05))
    bar.fill.solid()
    bar.fill.fore_color.rgb = NAVY
    bar.line.fill.background()
    bar.shadow.inherit = False
    tb = slide.shapes.add_textbox(Inches(0.55), Inches(0.14), Inches(12.2), Inches(0.8))
    runs = [(title, 30, True, WHITE)]
    if kicker:
        runs.append((kicker, 13, False, RGBColor(0xC7, 0xDA, 0xF2)))
    _text(tb.text_frame, runs, space_after=0)
    return slide


def _notes(slide, text):
    slide.notes_slide.notes_text_frame.text = text.strip()


def _stat(slide, x, y, w, value, label):
    """A single large headline figure with a caption underneath."""
    _box(slide, x, y, w, Inches(1.65), fill=PANEL, line=RGBColor(0xC7, 0xDA, 0xF2))
    tb = slide.shapes.add_textbox(x, y + Inches(0.18), w, Inches(1.3))
    tf = tb.text_frame
    tf.word_wrap = True
    p1 = tf.paragraphs[0]
    p1.alignment = PP_ALIGN.CENTER
    r1 = p1.add_run()
    r1.text = value
    r1.font.size = Pt(38)
    r1.font.bold = True
    r1.font.color.rgb = BLUE
    p2 = tf.add_paragraph()
    p2.alignment = PP_ALIGN.CENTER
    r2 = p2.add_run()
    r2.text = label
    r2.font.size = Pt(13)
    r2.font.color.rgb = GREY


def _bullets(slide, x, y, w, h, items, size=18):
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    for i, item in enumerate(items):
        para = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        para.space_after = Pt(14)
        run = para.add_run()
        run.text = "\u2022  " + item
        run.font.size = Pt(size)
        run.font.color.rgb = INK
        run.font.name = "Calibri"


def _figure_slot(slide, x, y, w, h, caption):
    """Placeholder to drop a screenshot or chart into."""
    _box(slide, x, y, w, h, fill=RGBColor(0xF7, 0xF9, 0xFC),
         line=RGBColor(0xB6, 0xC6, 0xDA))
    tb = slide.shapes.add_textbox(x, y + h / 2 - Inches(0.3), w, Inches(0.6))
    tf = tb.text_frame
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = caption
    r.font.size = Pt(14)
    r.font.italic = True
    r.font.color.rgb = GREY


def _table(slide, x, y, w, rows, col_w=None, size=14):
    n_rows, n_cols = len(rows), len(rows[0])
    height = Inches(0.42) * n_rows
    shape = slide.shapes.add_table(n_rows, n_cols, x, y, w, height)
    table = shape.table
    if col_w:
        for i, cw in enumerate(col_w):
            table.columns[i].width = cw
    for r, row in enumerate(rows):
        for c, val in enumerate(row):
            cell = table.cell(r, c)
            cell.text = str(val)
            para = cell.text_frame.paragraphs[0]
            para.alignment = PP_ALIGN.CENTER if c else PP_ALIGN.LEFT
            for run in para.runs:
                run.font.size = Pt(size)
                run.font.bold = (r == 0)
                run.font.color.rgb = WHITE if r == 0 else INK
                run.font.name = "Calibri"
    return table


def build() -> Path:
    prs = Presentation()
    prs.slide_width, prs.slide_height = W, H

    # ---------------------------------------------------------------- 1 title
    s = prs.slides.add_slide(prs.slide_layouts[6])
    band = s.shapes.add_shape(1, 0, 0, W, H)
    band.fill.solid()
    band.fill.fore_color.rgb = NAVY
    band.line.fill.background()
    band.shadow.inherit = False
    tb = s.shapes.add_textbox(Inches(1.0), Inches(2.1), Inches(11.3), Inches(3.2))
    _text(tb.text_frame, [
        ("Adaptive Email Spam Detection Using AI", 40, True, WHITE),
        ("and Content\u2013Metadata Fusion", 40, True, WHITE),
        ("", 12, False, WHITE),
        ("Lee Gong Yi", 22, False, RGBColor(0xC7, 0xDA, 0xF2)),
        ("Supervisor: Dr. Abdulrahman Aminu Ghali", 18, False, RGBColor(0xC7, 0xDA, 0xF2)),
        ("Faculty of Information and Communication Technology, UTAR Kampar Campus",
         14, False, RGBColor(0x9E, 0xBC, 0xE0)),
    ], space_after=4)
    _notes(s, """
Good morning. My project is an adaptive email spam detection system using AI and
content-metadata fusion. I am Lee Gong Yi, supervised by Dr. Abdulrahman Aminu Ghali.
[30 seconds. Do not read the slide - say it and move on.]
""")

    # -------------------------------------------------------------- 2 outline
    s = _slide(prs, "Outline")
    _bullets(s, Inches(1.4), Inches(1.7), Inches(10.5), Inches(5), [
        "The problem and why it is getting harder",
        "Gap in existing detection approaches",
        "Objectives",
        "System design and implementation",
        "Results: main corpus, classifier comparison, AI-generated phishing, adaptation",
        "Conclusion, limitations and future work",
    ], size=20)
    _notes(s, """
Briefly: I will cover the problem, the gap in existing work, my four objectives,
the system design, my results, and conclusions.
[30 seconds. The brief asks for an outline - this slide satisfies that.]
""")

    # -------------------------------------------------------------- 3 problem
    s = _slide(prs, "The Problem", "Email remains the primary attack vector")
    _stat(s, Inches(0.7), Inches(1.5), Inches(3.8), "~47%", "of world email traffic is spam (Kaspersky, 2024)")
    _stat(s, Inches(4.75), Inches(1.5), Inches(3.8), "USD 2.77bn", "BEC losses, 21,442 complaints (FBI IC3, 2024)")
    _stat(s, Inches(8.8), Inches(1.5), Inches(3.8), "21 s", "median time to click a phishing link (Verizon DBIR)")
    _bullets(s, Inches(0.9), Inches(3.6), Inches(11.5), Inches(3), [
        "Business email compromise contains no links and no keywords \u2014 signature filters miss it",
        "Large language models now write fluent, personalised phishing at scale",
        "Concept drift: a model trained once degrades as campaigns evolve",
    ])
    _notes(s, """
Email is still the main attack vector. Nearly half of all email is spam, business email
compromise cost 2.77 billion dollars last year across twenty-one thousand complaints, and
users click phishing links in a median of twenty-one seconds - faster than any manual review.

Two things make this harder now. BEC messages contain no links and no keywords, so anything
built on signatures misses them. And language models let attackers write fluent, typo-free
phishing at scale.
[2 minutes. These three numbers are the whole slide - say each one, then what it means.]
""")

    # ------------------------------------------------------------------ 4 gap
    s = _slide(prs, "Gap in Existing Approaches")
    _table(s, Inches(0.8), Inches(1.6), Inches(11.7), [
        ["Approach", "Strength", "Weakness"],
        ["Rule / keyword filters", "Explainable", "Brittle; evaded by rewording"],
        ["Content classifiers", "Learns from data", "Ignores message structure"],
        ["Metadata / reputation", "Catches anomalies", "Weak alone; evaded by clean BEC"],
        ["Commercial cloud filters", "Massive scale", "Proprietary; not reproducible"],
    ], col_w=[Inches(3.2), Inches(3.6), Inches(4.9)], size=15)
    _bullets(s, Inches(0.9), Inches(4.6), Inches(11.5), Inches(2), [
        "Content and metadata are complementary, not competing",
        "Few published systems are locally deployable, explainable AND adaptive",
    ])
    _notes(s, """
Rule filters break when attackers reword. Content models read what a message says but not how
it is built. Metadata catches structural anomalies but is bypassed by well-formed mail sent
from a properly configured account. Commercial filters work at scale but are proprietary, so
they cannot be benchmarked offline.

My argument is that content and metadata are complementary rather than competing, and that
very few published systems are locally deployable, explainable and adaptive at the same time.
[1.5 minutes.]
""")

    # ----------------------------------------------------------- 5 objectives
    s = _slide(prs, "Objectives")
    _bullets(s, Inches(1.1), Inches(1.8), Inches(11), Inches(5), [
        "Extract content features (body, subject, URLs) and metadata features "
        "(sender, header attributes) from raw email",
        "Design a content\u2013metadata fusion framework combining both in one "
        "machine-learning pipeline",
        "Train and evaluate Na\u00efve Bayes, logistic regression and support vector machines "
        "on the fused feature set",
        "Implement an adaptive retraining mechanism that updates the model with newly "
        "reviewed samples",
    ], size=19)
    _notes(s, """
Four objectives: extract content and metadata features; fuse them into one pipeline; train and
compare three classifiers; and implement adaptive retraining from reviewed samples.
[1 minute. Read them briefly - do not dwell, the detail comes in the results.]
""")

    # --------------------------------------------------------------- 6 design
    s = _slide(prs, "System Design", "Three feature streams fused into one classifier")
    _figure_slot(s, Inches(0.8), Inches(1.5), Inches(11.7), Inches(5.3),
                 "[ INSERT Figure 4.1 \u2014 system block diagram ]")
    _notes(s, """
Each message is parsed to RFC 5322, then three feature streams are extracted.

Word TF-IDF captures phrasing. Character n-grams, three to five characters, survive
obfuscation such as inserted symbols. And thirteen structural metadata signals - URL count,
unique link domains, sender-to-link domain mismatch, reply-to presence, SPF and DKIM
indicators, casing and urgency statistics.

These are fused into a single sparse vector, the metadata is standardised so raw lengths
cannot dominate the normalised text features, and a class-balanced logistic regression
produces a spam probability. Above the threshold the message is quarantined - never deleted.
Every decision goes to a review queue, and reviewer corrections feed the next retraining cycle.
[2 minutes. This is the core slide. Point at each stream as you name it.]
""")

    # ------------------------------------------------------- 7 implementation
    s = _slide(prs, "Implementation")
    _bullets(s, Inches(0.9), Inches(1.6), Inches(5.6), Inches(5), [
        "Python 3.13, scikit-learn, FastAPI",
        "Trained on 81,152 de-duplicated public emails",
        "Runs on a commodity CPU \u2014 no GPU required",
        "Live IMAP watcher over TLS, port 993",
        "Quarantine, review console, feedback store",
    ])
    _stat(s, Inches(7.0), Inches(1.7), Inches(2.6), "81,152", "emails after de-duplication")
    _stat(s, Inches(9.9), Inches(1.7), Inches(2.6), "13 ms", "median latency per email (CPU)")
    _stat(s, Inches(7.0), Inches(3.7), Inches(2.6), "13", "structural metadata signals")
    _stat(s, Inches(9.9), Inches(3.7), Inches(2.6), "75 / 25", "stratified train / test split")
    _notes(s, """
The system is implemented in Python with scikit-learn and FastAPI. It trained on 81,152
de-duplicated public emails from six merged corpora, and it runs entirely on a commodity CPU -
no graphics processor - at a median of thirteen milliseconds per email.

It includes a live IMAP watcher that connects over TLS on port 993, a quarantine action, a
browser review console and a feedback store for retraining.
[1.5 minutes.]
""")

    # -------------------------------------------------- 8 results main corpus
    s = _slide(prs, "Results \u2014 Held-out Test Split", "n = 20,288 emails never seen in training")
    _stat(s, Inches(0.7), Inches(1.45), Inches(2.9), "99.2%", "Accuracy")
    _stat(s, Inches(3.75), Inches(1.45), Inches(2.9), "0.991", "Precision")
    _stat(s, Inches(6.8), Inches(1.45), Inches(2.9), "0.992", "Recall")
    _stat(s, Inches(9.85), Inches(1.45), Inches(2.9), "1.000", "ROC-AUC")
    _table(s, Inches(0.8), Inches(3.5), Inches(6.2), [
        ["Confusion matrix", "Count"],
        ["True positives (phishing caught)", "10,399"],
        ["False negatives (phishing missed)", "80"],
        ["True negatives (legitimate passed)", "9,719"],
        ["False positives (legitimate flagged)", "90"],
    ], col_w=[Inches(4.2), Inches(2.0)], size=14)
    _box(s, Inches(7.5), Inches(3.5), Inches(5.0), Inches(2.1), fill=PANEL,
         line=RGBColor(0xC7, 0xDA, 0xF2))
    tb = s.shapes.add_textbox(Inches(7.8), Inches(3.75), Inches(4.4), Inches(1.7))
    _text(tb.text_frame, [
        ("False-positive rate \u2248 0.9%", 20, True, NAVY),
        ("90 of 9,809 legitimate messages flagged.", 14, False, INK),
        ("Blocking legitimate mail is the costlier error, "
         "so this is the operationally important figure.", 13, False, GREY),
    ])
    _notes(s, """
On the held-out split of 20,288 emails the fused model reached 99.2% accuracy, precision
0.991, recall 0.992 and ROC-AUC of 1.000.

The number that matters operationally is the false-positive rate of 0.9% - ninety of nine
thousand eight hundred legitimate messages. Blocking legitimate mail is the costlier error in
an organisation, so that is the figure I optimised around.

One clarification: the ROC-AUC of 1.000 is rounded. It is not literally perfect - it means the
model ranks spam above legitimate mail almost without exception on this corpus.
[2.5 minutes. Volunteer the AUC rounding point - it pre-empts a question.]
""")

    # ----------------------------------------------- 9 classifier comparison
    s = _slide(prs, "Classifier and Feature-Group Comparison", "Same split, same preprocessing, 0.5 threshold")
    _table(s, Inches(0.7), Inches(1.55), Inches(11.9), [
        ["Configuration", "Accuracy", "Precision", "Recall", "F1", "ROC-AUC"],
        ["Na\u00efve Bayes (content only)", "0.968", "0.988", "0.950", "0.969", "0.997"],
        ["Logistic regression (content only)", "0.988", "0.987", "0.990", "0.989", "0.999"],
        ["Linear SVM (content only)", "0.992", "0.990", "0.993", "0.992", "1.000"],
        ["Logistic regression (fusion \u2014 deployed)", "0.992", "0.990", "0.994", "0.992", "1.000"],
        ["Linear SVM (fusion)", "0.993", "0.992", "0.995", "0.993", "1.000"],
    ], col_w=[Inches(4.4), Inches(1.5), Inches(1.5), Inches(1.5), Inches(1.5), Inches(1.5)], size=14)
    _bullets(s, Inches(0.9), Inches(4.9), Inches(11.5), Inches(2), [
        "Fusion raised recall over content-only for both linear classifiers \u2014 "
        "metadata bought additional phishing caught",
        "SVM led by 0.001 (within noise); logistic regression deployed for calibrated "
        "probability, tunable threshold and explainable signals",
    ], size=17)
    _notes(s, """
All five configurations used the same split, the same preprocessing and the same default
threshold, so the comparison reflects only the classifier and the feature set.

Naive Bayes was weakest at 0.968 - it predicts spam conservatively, so it has high precision
but the lowest recall at 0.950, missing about five percent of phishing.

Adding metadata raised recall for both linear classifiers: logistic regression from 0.990 to
0.994, SVM from 0.993 to 0.995. That is the fusion design working as intended.

The SVM was marginally highest at 0.993 versus 0.992 - one thousandth, within noise. I deployed
logistic regression because it outputs a calibrated probability. That is what lets me tune the
threshold and show a confidence value and signal explanation. Explainability was a stated
objective, so I took the tunable model over a statistically indistinguishable alternative.
[1.5 minutes. Expect a question here - this answer is the answer.]
""")

    # ------------------------------------------------------- 10 LLM phishing
    s = _slide(prs, "Generalisation to AI-Generated Phishing", "4,986 emails from GPT-4.1, DeepSeek 3.2 and LLaMA 3.3 \u2014 never trained on")
    _stat(s, Inches(0.8), Inches(1.6), Inches(3.4), "92%", "caught at a recall-focused threshold (4,565 / 4,986)")
    _stat(s, Inches(4.45), Inches(1.6), Inches(3.4), "84%", "caught at the deployed 0.55 threshold")
    _stat(s, Inches(8.1), Inches(1.6), Inches(3.4), "0", "AI-generated emails used in training")
    _figure_slot(s, Inches(2.6), Inches(3.6), Inches(8.1), Inches(3.2),
                 "[ INSERT Figure 6.3 \u2014 catch rate versus decision threshold ]")
    _notes(s, """
I tested the detector on 4,986 phishing emails generated by GPT-4.1, DeepSeek 3.2 and
LLaMA 3.3. None of these were used in training - this is a pure generalisation test.

It caught 92% at a recall-focused threshold and 84% at the deployed 0.55.

The important observation is the shape of that curve: the catch rate falls faster than it does
on classic phishing, which means the model is systematically less confident on AI-written mail.
That is evidence these messages are genuinely harder, and it is the direct motivation for the
adaptive retraining mechanism I show next.
[2 minutes.]
""")

    # -------------------------------------------------------- 11 adaptation
    s = _slide(prs, "Adaptive Retraining", "One reviewed retraining cycle on a disjoint feedback batch")
    _table(s, Inches(0.8), Inches(1.6), Inches(7.2), [
        ["Measure", "Before", "After"],
        ["ROC-AUC (modern-threat set)", "0.810", "0.945"],
        ["Phishing recall at 0.55", "95%", "95%"],
        ["Main-corpus accuracy", "0.991", "0.991"],
        ["Demo campaign caught", "0 / 6", "5 / 6"],
    ], col_w=[Inches(3.8), Inches(1.7), Inches(1.7)], size=15)
    _box(s, Inches(8.4), Inches(1.6), Inches(4.1), Inches(3.4), fill=RGBColor(0xFF, 0xF7, 0xE6),
         line=RGBColor(0xE8, 0xC4, 0x6A))
    tb = s.shapes.add_textbox(Inches(8.7), Inches(1.85), Inches(3.5), Inches(3.0))
    _text(tb.text_frame, [
        ("Scope of the claim", 17, True, NAVY),
        ("16 of the 30 test messages share a threat family with the feedback batch "
         "(TF-IDF cosine \u2265 0.70). No message appears in both sets.", 13, False, INK),
        ("Read as adaptation to a represented threat family, not a general gain.",
         13, True, INK),
    ])
    _bullets(s, Inches(0.9), Inches(5.3), Inches(11.5), Inches(1.6), [
        "Validation gate: a candidate model replaces the deployed one only if ranking "
        "quality on the held-out split is not reduced",
    ], size=17)
    _notes(s, """
After one reviewed retraining cycle on a disjoint feedback batch, ranking on the modern-threat
set improved from AUC 0.81 to 0.945, while recall held at 95% and main-corpus accuracy was
maintained at 0.991. In a controlled before-and-after on a held-out campaign, messages caught
rose from zero out of six to five out of six.

I want to be honest about the scope. I measured the similarity between the feedback batch and
that test set: sixteen of the thirty test messages have a TF-IDF cosine similarity of 0.70 or
above to at least one feedback message, although no message appears in both sets. So this
should be read as adaptation to a threat family represented in the feedback, not as a general
gain on arbitrary unseen threats. I report that in Section 6.2.4.

Retraining is reviewer-initiated, and a candidate model is deployed only if it does not reduce
ranking quality on the held-out split.
[2 minutes. Volunteering the similarity limit is the strongest thing you can do here.]
""")

    # -------------------------------------------- 12 conclusion + limitations
    s = _slide(prs, "Conclusion, Limitations and Future Work")
    _bullets(s, Inches(0.8), Inches(1.5), Inches(5.8), Inches(3), [
        "All four objectives achieved",
        "99.2% accuracy, 0.9% FPR, 13 ms on CPU",
        "92% on unseen LLM-generated phishing",
        "Measurable adaptation from reviewed feedback",
    ], size=18)
    _box(s, Inches(6.9), Inches(1.45), Inches(5.6), Inches(3.3), fill=PANEL,
         line=RGBColor(0xC7, 0xDA, 0xF2))
    tb = s.shapes.add_textbox(Inches(7.2), Inches(1.7), Inches(5.0), Inches(3.0))
    _text(tb.text_frame, [
        ("Two limitations I measured", 17, True, NAVY),
        ("URL counting reads only the plain-text MIME part, so links inside HTML "
         "are not counted.", 13, False, INK),
        ("Authentication signals learned inversely: the corpus's legitimate mail predates "
         "SPF, so SPF presence correlates with spam. Same message scored 11.5% without "
         "auth headers, 100% with.", 13, False, INK),
    ])
    _bullets(s, Inches(0.8), Inches(5.0), Inches(11.7), Inches(2), [
        "Future work: HTML-aware URL extraction; a corpus with modern legitimate mail; "
        "head-to-head commercial comparison on one shared labelled set",
    ], size=17)
    _notes(s, """
To conclude: all four objectives were achieved. 99.2% accuracy at a 0.9% false-positive rate,
thirteen milliseconds on a CPU, 92% on unseen AI-generated phishing, and measurable adaptation
from reviewed feedback.

Two limitations I measured rather than assumed. First, URL counting reads only the plain-text
MIME part, so links inside HTML href attributes are not counted - that under-counts on modern
marketing mail. Second, the authentication signals learned the association inversely: the
legitimate mail in the public corpus predates SPF and DKIM while much of the spam carries them,
so the model associates their presence with spam. I isolated this with a controlled test - the
same message scored 11.5% with the authentication headers removed and 100% with them present.
It is invisible on the held-out split because the distribution matches, but it inflates scores
on live mail.

Future work: HTML-aware URL extraction, a training corpus containing modern legitimate mail
with authentication headers, and a head-to-head comparison against commercial filters on one
shared labelled corpus.

Thank you. I am happy to take questions.
[1.5 minutes. Say the limitations before you are asked - it reads as confidence.]
""")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    prs.save(OUT)
    return OUT


if __name__ == "__main__":
    path = build()
    print(f"wrote {path}")
