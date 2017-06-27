def get_files(directory):
	from os import listdir
	from os.path import isfile, join
	return [f for f in listdir(directory) if isfile(join(directory, f))]

def get_text(filename):
	with open(filename) as f:
		content = f.read()
	return content.replace('\n', '')

if __name__ == '__main__':
	import sys
	from nltk.sentiment.vader import SentimentIntensityAnalyzer

	pos_files = get_files(sys.argv[1] + 'pos/')
	neg_files = get_files(sys.argv[1] + 'neg/')
	num_pos = len(pos_files)
	num_neg = len(neg_files)

	vader = SentimentIntensityAnalyzer()

	correct_pos = 0
	for file in pos_files:
		text = get_text(sys.argv[1] + 'pos/' + file)
		pos = vader.polarity_scores(text)['pos']
		neg = vader.polarity_scores(text)['neg']
		if pos > neg:
			correct_pos += 1

	correct_neg = 0
	for file in neg_files:
		text = get_text(sys.argv[1] + 'neg/' + file)
		pos = vader.polarity_scores(text)['pos']
		neg = vader.polarity_scores(text)['neg']
		if neg > pos:
			correct_neg += 1

	print "positive accuracy: {}".format(1.0*correct_pos/num_pos)
	print "negative accuracy: {}".format(1.0*correct_neg/num_pos)
	print "overall accuracy: {}".format(1.0*(correct_pos+correct_neg)/(num_pos+num_neg))
