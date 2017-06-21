import urllib2
from bs4 import BeautifulSoup
import string
import sys  
reload(sys)  
sys.setdefaultencoding('utf8')

TRAIN_NER = False
TRAIN_REL = False

MITIE_PATH = '/Users/aduarte/Desktop/MITIE/'
sys.path.append(MITIE_PATH + 'mitielib')
from mitie import *

mainWikiURL = "https://en.wikipedia.org{}"
template_wikiURL = "/wiki/{}"

GLOBAL_BANDS = ["10,000 Maniacs",
                "Belly", # (band)
                "Black Star", # (rap duo)
                "Bob Marley and the Wailers",
                "The Breeders",
                "Lupe Fiasco",
                "Run the Jewels",
                "Talking Heads",
                "Throwing Muses",
                "Tom Tom Club"]


def parseArgs():
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg.startswith("-cached="):
            path = arg[8:]
            return path


def getHtmlFromFilename(filename):
    with open(filename, "r") as f:
        html = BeautifulSoup(f.read(), "html.parser")
    return html


def getHtmlFromUrl(URL):
    response = urllib2.urlopen(URL)
    html = BeautifulSoup(response, "html.parser")
    return html


def stringToWikiUrl(searchString):
    return "_".join(searchString.split()) # Something_like_this


def getHtmlFromSearchString(searchString):
    wikiURL = stringToWikiUrl(searchString)
    searchURL = template_wikiURL.format(wikiURL)
    URL = mainWikiURL.format(searchURL)
    try:
        return str(getHtmlFromUrl(URL))
    except Exception, e:
        return "{} is not a valid search term".format(searchString)


def makeFilename(searchString):
    return searchString.translate(None, string.punctuation).replace(" ", "_") + ".html"


def saveHtmlToFile(html, searchString):
    with open(makeFilename(searchString), "w") as f:
        f.write(html)


def getAndSavePages(listOfStrings):
    for element in listOfStrings:
        # print "getting", element
        html = getHtmlFromSearchString(element)
        saveHtmlToFile(html, element)


def getTextFromHtml(html):
    return html.findAll('p')


# return a list of members of a band from a band page.
def getTableMembers(html):
    artists = []
    try:
        th = html.findAll('th', text='Members')[0]
        td = th.findNext('td')
        artists.extend([li.text for li in td.findAll('li')])
        artists.extend([a.text for a in td.findAll('a')])
    except:
        None
    try:
        th = html.findAll('th', text='Past members')[0]
        td = th.findNext('td')
        artists.extend([li.text for li in td.findAll('li')])
        artists.extend([a.text for a in td.findAll('a')])
    except:
        None
    return artists


# return a list of bands associated with the artist from the artist page.
def getTableBands(html):
    bands = []
    try:
        th = html.findAll('th', text='Associated acts')[0]
        td = th.findNext('td')
        bands.extend([li.text for li in td.findAll('li')])
        bands.extend([a.text for a in td.findAll('a')])
    except:
        None
    return bands


def create_tuple_indices(breaks_, indices_, ner_indices_, grp_token_):
    k = 0
    for b in breaks_:
        tup = [n for n in indices_[k:] if n <= b]
        if len(tup) == len(grp_token_):
            ner_indices_.append((tup[0], tup[-1]+1))
        k += len(tup)


def add_ner_entities(indices_, tokens_, sample_, trainer_ner_, rel_):
    for j in indices_:
        try:
            print "adding {} xrange({}, {}) => ({}, {})".format(rel_, j[0], j[1], tokens_[j[0]], tokens_[j[1]-1])
            sample_.add_entity(xrange(j[0], j[1]), rel_)
            trainer_ner_.add(sample_)
        except:
            pass


def find_positions(group_, tokens_, sample_, trainer_ner_, train_ner_, trainer_rel_, train_rel_, grp2_indices_, rel_):
    for grp in group_:
        grp_indices = []
        grp_token = tokenize(grp)
        indices = [idx for idx, tok in enumerate(tokens_) if tok in grp_token]
        breaks = [pos1+1 for pos1, pos2 in zip(indices, indices[1:]) if pos2-pos1 != 1]
        if len(indices) > 0:
            breaks.append(indices[-1])
        # create list of tuples
        create_tuple_indices(breaks, indices, grp_indices, grp_token)
        if train_ner_:
            # add binary relations
            add_ner_entities(grp_indices, tokens_, sample_, trainer_ner_, rel_)
        if train_rel_:
            for i in grp2_indices_:
                for j in grp_indices:
                    try:
                        trainer_rel_.add_positive_binary_relation(tokens_, xrange(i[0], i[1]), xrange(j[0], j[1]))
                        trainer_rel_.add_negative_binary_relation(tokens_, xrange(j[0], j[1]), xrange(i[0], i[1]))
                    except:
                        pass


def iterate_phrases(phrases_, rel_, rel2_, trainer_ner_, train_ner_, trainer_rel_, train_rel_, grp2_, grp_token_):
    for phrase in phrases_:
        grp_indices = []
        # tokenize
        tokens = tokenize(phrase.text)
        sample = ner_training_instance(tokens)
        if len(tokens) > 0:
            # find positions of <rel_>
            indices = [idx for idx, tok in enumerate(tokens) if tok in grp_token_]
            breaks = [pos1+1 for pos1, pos2 in zip(indices, indices[1:]) if pos2-pos1 != 1]
            if len(indices) > 0:
                breaks.append(indices[-1])
            # create list of tuples
            create_tuple_indices(breaks, indices, grp_indices, grp_token_)
            # print [tokens[j[0]:j[1]] for j in grp_indices]
            if train_ner_:
                # add binary relations
                add_ner_entities(grp_indices, tokens, sample, trainer_ner_, rel_)
            # find positions of <rel2_>
            find_positions(grp2_, tokens, sample, trainer_ner_, train_ner_, trainer_rel_, train_rel_, grp_indices, rel2_)


def extract_from_filename(fn_, grp_, grp2_, trainer_ner_, train_ner_, trainer_rel_, train_rel_, grp_token_):
    # print "\tfilename", fn
    html = getHtmlFromFilename(fn_)
    # get list of grp
    grp = getTableMembers(html)
    # get phrases from wikipedia text
    phrases = getTextFromHtml(html)
    # for each phrase,
    iterate_phrases(phrases, grp_, grp2_, trainer_ner_, train_ner_, trainer_rel_, train_rel_, grp, grp_token_)
    # return
    return grp


def main():
    # get cached path argument from command line
    cachePath = parseArgs()
    # print "cachePath", cachePath
    if not cachePath:
        getAndSavePages(GLOBAL_BANDS + people)
        cachePath = "./"

    # TRAINING
    # create ner model and binary relationship extractor
    trainer_ner = ""
    trainer_rel = ""
    if TRAIN_NER:
        trainer_ner = ner_trainer(MITIE_PATH + 'MITIE-models/english/total_word_feature_extractor.dat')
    if TRAIN_REL:
        ner = named_entity_extractor('/Users/aduarte/Desktop/MITIE/MITIE-models/english/ner_model.dat')
        trainer_rel = binary_relation_detector_trainer('people.person.band.membership', ner)
        

    # iterate through each band page saved locally
    for band in GLOBAL_BANDS:
        band_token = tokenize(band)
        # read html from local file
        filename = cachePath + makeFilename(band)
        members = extract_from_filename(filename, "band", "person", trainer_ner, TRAIN_NER, trainer_rel, TRAIN_REL, band_token)

        # iterate through each member page saved locally
        for member in members:
            member_token = tokenize(member)
            # get local filename
            filename = cachePath + makeFilename(str(member))
            # try to get the local html
            try:
                extract_from_filename(filename, "person", "band", trainer_ner, TRAIN_NER, trainer_rel, TRAIN_rel, member_token)
            except:
                pass

    if TRAIN_NER:
        print "Training new NER model..."
        # train ner model
        ner_model = trainer_ner.train()
        print "Model trained with tags:", ner_model.get_possible_ner_tags()
        ner_model.save_to_disk("ner_person_band_member.dat")
    else:
        try:
            print "Loading already trained NER model"
            ner_model = named_entity_extractor("ner_person_band_member.dat") # load previously built extractor
        except:
            print "Could not load already trained NER model"
            print "Run again with option TRAIN_NER enabled"
            sys.exit(1)
    
    if TRAIN_REL:
        print "Training new REL model..."
        # train binary relationship model
        rel_model = trainer_rel.train()
        rel_model.save_to_disk("rel_person_band_member.svm")
    else:
        try:
            print "Loading already trained REL model"
            rel_model = binary_relation_detector("rel_person_band_member.svm") # load previously built extractor
        except:
            print "Could not load already trained REL model"
            print "Run again with option TRAIN_REL enabled"
            sys.exit(1)

    # TESTING
    # ask user for input
    user_input = ''
    while user_input != "quit":
        user_input = raw_input("Find: ")
        if user_input.startswith("person "):
            member = user_input.split("person ")[1]
            filename = cachePath + makeFilename(member)
            try:
                html = getHtmlFromFilename(filename)
            except:
                print "Could not find {}.".format(filename)
                pass
            try:
                # get phrases from wikipedia text
                phrases = getTextFromHtml(html)
                l_names = []
                for phrase in phrases:
                    # tokenize
                    tokens = tokenize(phrase.text)
                    if len(tokens) > 0:
                        # run ner
                        entities = ner_model.extract_entities(tokens)
                        adjacent_entities = [(entities[i][0], entities[i+1][0]) for i in xrange(len(entities)-1)]
                        adjacent_entities += [(r, l) for (l, r) in adjacent_entities]
                        # run rel extractor
                        for i, j in adjacent_entities:
                            relation = ner_model.extract_binary_relation(tokens, i, j)
                            score = rel_model(relation)
                            i_name = ' '.join(tokens[i].decode() for i in i)
                            j_name = ' '.join(tokens[i].decode() for i in j)
                            if i_name == member and i_name != j_name and j_name not in l_names and abs(score) > 0.25:
                                print i_name, "in band", j_name, "(", score, ")"
                                l_names.append(j_name)
                if len(l_names) == 0:
                    print "Could not find anything."
            except:
                print "Failed."
        elif user_input.startswith("band "):
            band = user_input.split("band ")[1]
            filename = cachePath + makeFilename(band)
            try:
                html = getHtmlFromFilename(filename)
            except:
                print "Could not find {}.".format(filename)
                pass
            try:
                # get phrases from wikipedia text
                phrases = getTextFromHtml(html)
                l_names = []
                for phrase in phrases:
                    # tokenize
                    tokens = tokenize(phrase.text)
                    if len(tokens) > 0:
                        # run ner
                        entities = ner_model.extract_entities(tokens)
                        adjacent_entities = [(entities[i][0], entities[i+1][0]) for i in xrange(len(entities)-1)]
                        adjacent_entities += [(r, l) for (l, r) in adjacent_entities]
                        # run rel extractor
                        for i, j in adjacent_entities:
                            relation = ner_model.extract_binary_relation(tokens, i, j)
                            score = rel_model(relation)
                            i_name = ' '.join(tokens[i].decode() for i in i)
                            j_name = ' '.join(tokens[i].decode() for i in j)
                            if i_name == band and i_name != j_name and j_name not in l_names and abs(score) > 0.25:
                                print i_name, "has member", j_name, "(", score, ")"
                                l_names.append(j_name)
                if len(l_names) == 0:
                    print "Could not find anything."
            except:
                print "Failed."
        elif user_input == "quit":
            sys.exit("Bye")
        else:
            print "Could not parse request. Follow the format below or type <quit> to exit."
            print "Find: <person|band> <name of person|band>"

if __name__ == "__main__":
    main()

