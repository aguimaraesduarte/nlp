'''
This script checks the Porter Stemmer, as implemented in NLTK.
'''


def read_file(file_name):
    input = []
    with open(file_name) as f:
        content = f.readlines()
        for line in content:
            input.append(line.strip())
    return input


if __name__ == "__main__":
    import sys

    try:
        if sys.argv[1] == 'snowball':
            print "Using Snowball Stemmer."
            from nltk.stem.snowball import SnowballStemmer
            stemmer = SnowballStemmer("english")
        else:
            print "Using Porter Stemmer (default)."
            from nltk.stem.porter import PorterStemmer
            stemmer = PorterStemmer()
    except:
        sys.exit("You need to specify a stemmer ('porter' or 'snowball')")

    print_correct = raw_input("Do you want to see correct matchings? (y|n) ")
    print print_correct
    while print_correct != "y" and print_correct != "n":
        print_correct = raw_input("Do you want to see correct matchings? (y|n) ")

    vocs = read_file('voc.txt')
    outputs = read_file('output.txt')
    instances_checked = 0
    instances_incorrect = 0

    for voc, output in zip(vocs, outputs):
        stemmed_word = stemmer.stem(voc)
        instances_checked += 1
        if stemmed_word != output:
            print '[X]', voc, '--> got', stemmed_word, '(expected', output + ')'
            instances_incorrect += 1
        else:
            if print_correct == "y":
                print '[ ]', voc, '-->', output
    print 'Accuracy: {:.2%}'.format(float(instances_checked - instances_incorrect) / float(instances_checked))

    # print stemmer.stem('internationalisation') # should produce 'internation', but produces 'internationalis'