from spam_detection.model import EmailSpamDetector

HAM = "From: team@acme.example\nSubject: Weekly project update\n\nThe meeting is on Tuesday at 10am."
SPAM = "From: alerts@secure-acme-login.example\nReply-To: collector@evil.example\nSubject: URGENT! Verify your password now!!!\n\nYour account is suspended. Click here: https://evil.example/login"

def test_train_predict_and_round_trip(tmp_path):
    model = EmailSpamDetector().fit([HAM, SPAM, HAM + " Notes", SPAM + " Act now"], [0, 1, 0, 1])
    result = model.predict(SPAM)
    assert result.label == "spam"
    assert 0 <= result.spam_probability <= 1
    output = tmp_path / "detector.joblib"
    model.save(output)
    assert EmailSpamDetector.load(output).predict(HAM).label == "ham"
