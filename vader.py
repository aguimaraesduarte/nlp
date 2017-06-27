def get_text(filename):
 with open(filename) as f:
  content = f.read()
 return content.replace('\n', '')

if __name__ == '__main__':
 import sys
 from nltk.sentiment.vader import SentimentIntensityAnalyzer
 
 vader = SentimentIntensityAnalyzer()
 text = get_text(sys.argv[1])
 score = vader.polarity_scores(text)
 print score
