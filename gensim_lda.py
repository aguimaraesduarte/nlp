def clean(doc):
	from nltk.corpus import stopwords
	from nltk.stem.wordnet import WordNetLemmatizer
	import string

	stop = set(stopwords.words('english'))
	exclude = set(string.punctuation)
	lemma = WordNetLemmatizer()

	stop_free = " ".join([i for i in doc.lower().split() if i not in stop]).decode('ascii', 'ignore')
	punc_free = ''.join(ch for ch in stop_free if ch not in exclude)
	normalized = " ".join(lemma.lemmatize(word) for word in punc_free.split())

	return normalized.split()

def get_topics(corpus):
	import gensim

	# Creating the term dictionary of our courpus, where every unique term is assigned an index. 
	dictionary = gensim.corpora.Dictionary(corpus)

	# Converting list of documents (corpus) into Document Term Matrix using dictionary prepared above.
	doc_term_matrix = [dictionary.doc2bow(doc) for doc in corpus]

	# Creating the object for LDA model using gensim library
	Lda = gensim.models.ldamodel.LdaModel

	# Running and Trainign LDA model on the document term matrix.
	ldamodel = Lda(doc_term_matrix, num_topics=3, id2word = dictionary, passes=50)

	print(ldamodel.print_topics(num_topics=3, num_words=3))

def read_file(filename):
	with open(filename) as f:
		contents = f.readlines()
	text = ''

	for line in contents:
		text += line.strip()

	return text

def read_all_files(directory):
	import os

	documents = []
	file_list = os.listdir(directory)

	for filename in file_list:
		documents.append(read_file(os.path.join(directory, filename)))

	return documents

def get_text(filename):
	with open(filename) as f:
		content = f.read()

	return content.replace('\n', '')

def get_files(directory):
	from os import listdir
	from os.path import isfile, join

	return [get_text(join(directory, f)) for f in listdir(directory) if isfile(join(directory, f))]

if __name__ == '__main__':
	import gensim
	import sys

	normalized = [clean(d) for d in read_all_files(sys.argv[1])]

	get_topics(normalized)