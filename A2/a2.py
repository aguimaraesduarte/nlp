import urllib2
from bs4 import BeautifulSoup
import string
import sys  
reload(sys)  
sys.setdefaultencoding('utf8')

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

TRAIN_NER = False
TRAIN_REL = False
SCORE_THRESHOLD = 0.0

NER_MODEL_NAME = "ner_band_member.dat"
REL_B2M_MODEL_NAME = "rel_band_to_member.svm"
REL_M2B_MODEL_NAME = "rel_member_to_band.svm"


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
            print "adding {} xrange({}, {}) => ({})".format(rel_, j[0], j[1], tokens_[j[0]:j[1]])
            sample_.add_entity(xrange(j[0], j[1]), rel_)
            trainer_ner_.add(sample_)

        except:
            pass


def find_positions(group_, tokens_, sample_, trainer_ner_, cond_NER_, trainer_rel_b2m_, trainer_rel_m2b_, cond_REL_, grp2_indices_, rel_):
    for grp in group_:
        grp_indices = []
        grp_token = tokenize(grp)
        indices = [idx for idx, tok in enumerate(tokens_) if tok in grp_token]
        breaks = [pos1+1 for pos1, pos2 in zip(indices, indices[1:]) if pos2-pos1 != 1]

        if len(indices) > 0:
            breaks.append(indices[-1])
        # create list of tuples
        create_tuple_indices(breaks, indices, grp_indices, grp_token)

        if cond_NER_:
            # add binary relations
            add_ner_entities(grp_indices, tokens_, sample_, trainer_ner_, rel_)

        if cond_REL_:
            for i in grp2_indices_:
                for j in grp_indices:
                    try:
                        if rel_ == "band":
                            # add positive to band=>member
                            # add negative to member=>band
                            trainer_rel_b2m_.add_positive_binary_relation(tokens_, xrange(i[0], i[1]), xrange(j[0], j[1]))
                            trainer_rel_m2b_.add_negative_binary_relation(tokens_, xrange(j[0], j[1]), xrange(i[0], i[1]))

                        else:
                            # add positive to member=>band
                            # add negative to band=>member
                            trainer_rel_m2b_.add_positive_binary_relation(tokens_, xrange(i[0], i[1]), xrange(j[0], j[1]))
                            trainer_rel_b2m_.add_negative_binary_relation(tokens_, xrange(j[0], j[1]), xrange(i[0], i[1]))

                    except:
                        pass


def iterate_phrases(phrases_, rel_, rel2_, trainer_ner_, cond_NER_, trainer_rel_b2m_, trainer_rel_m2b_, cond_REL_, grp2_, grp_token_):
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

            if cond_NER_:
                # add binary relations
                add_ner_entities(grp_indices, tokens, sample, trainer_ner_, rel_)

            # find positions of <rel2_>
            find_positions(grp2_, tokens, sample, trainer_ner_, cond_NER_, trainer_rel_b2m_, trainer_rel_m2b_, cond_REL_, grp_indices, rel2_)


def extract_from_html(cpath_, grpname_, grp_, grp2_, trainer_ner_, cond_NER_, trainer_rel_b2m_, trainer_rel_m2b_, cond_REL_):
    # tokenize group name
    grp_token = tokenize(grpname_)
    # make filename
    filename = cpath_ + makeFilename(str(grpname_))
    # print "\tfilename", fn
    html = getHtmlFromFilename(filename)
    # get list of grp
    grp = getTableMembers(html)
    # get phrases from wikipedia text
    phrases = getTextFromHtml(html)
    # iterate through phrases
    iterate_phrases(phrases, grp_, grp2_, trainer_ner_, cond_NER_, trainer_rel_b2m_, trainer_rel_m2b_, cond_REL_, grp, grp_token)
    
    return grp


def print_relations(adj_ent_, ner_model_, rel_model_, tokens_, grp_, grpname_, l_names_, thresh_):
    for i, j in adj_ent_:
        relation = ner_model_.extract_binary_relation(tokens_, i, j)
        score = rel_model_(relation)
        i_name = ' '.join(tokens_[i].decode() for i in i)
        j_name = ' '.join(tokens_[i].decode() for i in j)

        if i_name == grp_ and i_name != j_name and j_name not in l_names_ and score > thresh_:
            if grpname_ == "band":
                print i_name, "has member", j_name, "(", score, ")"

            else:
                print i_name, "in band", j_name, "(", score, ")"

            l_names_.append(j_name)


def find_from_html(html_, ner_model_, rel_model_, grp_, grpname_, thresh_):
    # get phrases from wikipedia text
    phrases = getTextFromHtml(html_)
    l_names = []
    for phrase in phrases:
        # tokenize
        tokens = tokenize(phrase.text)

        if len(tokens) > 0:
            # run ner
            entities = ner_model_.extract_entities(tokens)
            adjacent_entities = [(entities[i][0], entities[i+1][0]) for i in xrange(len(entities)-1)]
            adjacent_entities += [(r, l) for (l, r) in adjacent_entities]
            # run rel extractor
            print_relations(adjacent_entities, ner_model_, rel_model_, tokens, grp_, grpname_, l_names, thresh_)

    if len(l_names) == 0:
        print "Could not find anything."


def try_extract(grp_, grpname_, cpath_, ner_model_, rel_model_, thresh_):
    filename = cpath_ + makeFilename(grp_)
    try:
        html = getHtmlFromFilename(filename)

        try:
            find_from_html(html, ner_model_, rel_model_, grp_, grpname_, thresh_)

        except:
            print "Failed."

    except:
        print "Could not find {}.".format(filename)


def train_load_model(condition_, type_, trainer_, fun_model_, save_filename):
    if condition_:
        print "Training new {} model...".format(type_)
        # train ner model
        model = trainer_.train()
        try:
            print "Model trained with tags:", model.get_possible_ner_tags()
        except:
            pass
        model.save_to_disk(save_filename)

    else:
        try:
            print "Loading already trained {} model".format(type_)
            model = fun_model_(save_filename)

        except:
            print "Could not load already trained {} model".format(type_)
            print "Run again with option TRAIN_{} enabled".format(type_)
            sys.exit(1)

    return model


def model_training(bands_list_, cpath_, trainer_ner_, cond_NER_, trainer_rel_b2m_, trainer_rel_m2b_, cond_REL_):
    # iterate through each band page saved locally
    for band in bands_list_:
        members = extract_from_html(cpath_, band, "band", "person", trainer_ner_, cond_NER_, trainer_rel_b2m_, trainer_rel_m2b_, cond_REL_)

        # iterate through each member page saved locally
        for member in members:
            try:
                extract_from_html(cpath_, member, "person", "band", trainer_ner_, cond_NER_, trainer_rel_b2m_, trainer_rel_m2b_, cond_REL_)
            except:
                pass


def training(cond_NER_, cond_REL_, mpath_, bands_list_, cpath_):
    # create ner model and binary relationship extractor
    trainer_ner = ""
    trainer_rel_b2m = ""
    trainer_rel_m2b = ""

    if cond_NER_:
        trainer_ner = ner_trainer(mpath_ + 'MITIE-models/english/total_word_feature_extractor.dat')

    if cond_REL_:
        ner = named_entity_extractor(mpath_ + 'MITIE-models/english/ner_model.dat')
        trainer_rel_b2m = binary_relation_detector_trainer('band.to.member', ner)
        trainer_rel_m2b = binary_relation_detector_trainer('member.to.band', ner)
        
    if cond_NER_ or cond_REL_:
        model_training(bands_list_, cpath_, trainer_ner, cond_NER_, trainer_rel_b2m, trainer_rel_m2b, cond_REL_)

    return trainer_ner, trainer_rel_b2m, trainer_rel_m2b


def testing(cpath_, ner_model_, rel_model_b2m_, rel_model_m2b_, thresh_):
    # ask user for input
    user_input = ''

    while user_input != "quit":
        user_input = raw_input("Find: ")

        if user_input.startswith("person "):
            member = user_input.split("person ")[1]
            try_extract(member, "member", cpath_, ner_model_, rel_model_m2b_, thresh_)

        elif user_input.startswith("band "):
            band = user_input.split("band ")[1]
            try_extract(band, "band", cpath_, ner_model_, rel_model_b2m_, thresh_)

        elif user_input == "quit":
            sys.exit("Bye")

        else:
            print "Could not parse request. Follow the format below or type <quit> to exit."
            print "Find: <person|band> <name of person|band>"


def getCachePath(bands_list_):
    cachePath = parseArgs()
    if not cachePath:
        getAndSavePages(bands_list_)
        cachePath = "./"
    return cachePath


def main():
    # get cached path argument from command line
    CACHE_PATH = getCachePath(GLOBAL_BANDS)

    # TRAINING
    trainer_ner, trainer_rel_b2m, trainer_rel_m2b = training(TRAIN_NER, TRAIN_REL, MITIE_PATH, GLOBAL_BANDS, CACHE_PATH)

    # train/load model
    ner_model = train_load_model(TRAIN_NER, "NER", trainer_ner, named_entity_extractor, NER_MODEL_NAME)
    rel_model_b2m = train_load_model(TRAIN_REL, "REL", trainer_rel_b2m, binary_relation_detector, REL_B2M_MODEL_NAME)
    rel_model_m2b = train_load_model(TRAIN_REL, "REL", trainer_rel_m2b, binary_relation_detector, REL_M2B_MODEL_NAME)

    # TESTING
    testing(CACHE_PATH, ner_model, rel_model_b2m, rel_model_m2b, SCORE_THRESHOLD)

if __name__ == "__main__":
    main()

