
def read_text(filename):
    import nltk
    from nltk import word_tokenize

    with open(filename) as f:
        content = f.read()
    text = nltk.word_tokenize(content)
    return text


def get_ngrams(text, n):
    import nltk
    from nltk.util import ngrams

    return ngrams(text, n)


if __name__ == '__main__':
    import sys
    from collections import Counter

    if len(sys.argv) < 3:
        sys.exit("Usage: python ngrams.py /path/to/file n (integer)")

    text = read_text(sys.argv[1])
    #print text
    print '{}-grams:'.format(sys.argv[2]),
    print Counter(get_ngrams(text, int(sys.argv[2])))