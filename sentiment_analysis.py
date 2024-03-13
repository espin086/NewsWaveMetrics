import nltk
nltk.download('vader_lexicon')
nltk.download('punkt')
from nltk.sentiment import SentimentIntensityAnalyzer

def analyze_sentiment(text):
    sia = SentimentIntensityAnalyzer()
    sentiment_score = sia.polarity_scores(text)['compound']

    if sentiment_score >= 0.05:
        return 'Positive'
    elif sentiment_score <= -0.05:
        return 'Negative'
    else:
        return 'Neutral'


news_article_text = "Today, the stock market experienced a significant downturn, with major indices plunging to multi-month lows. Investor confidence has been shaken by escalating geopolitical tensions, uncertainty surrounding global economic recovery, and fears of an impending recession. Companies across various sectors are reporting dismal earnings, further exacerbating the market's downward spiral. Analysts warn that the current bearish sentiment may persist in the coming weeks, casting a shadow over the prospects of a swift recovery."
sentiment_label = analyze_sentiment(news_article_text)
print(f"Sentiment: {sentiment_label}")