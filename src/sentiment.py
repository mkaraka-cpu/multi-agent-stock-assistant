# src/sentiment.py
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
analyzer = SentimentIntensityAnalyzer()

def score_headlines(headlines):
    scored = []
    for h in headlines:
        s = analyzer.polarity_scores(h)
        compound = s["compound"]
        label = "neutral"
        if compound >= 0.05:
            label = "positive"
        elif compound <= -0.05:
            label = "negative"
        scored.append({"headline": h, "compound": compound, "label": label})
    return scored
