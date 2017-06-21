import urllib2
from bs4 import BeautifulSoup
import string
import sys

sys.path.append('/Users/aduarte/Desktop/MITIE/mitielib')
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
        print "getting", element
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


def main():
    # get cached path argument from command line
    cachePath = parseArgs()
    print "cachePath", cachePath
    if not cachePath:
        getAndSavePages(GLOBAL_BANDS + people)
        cachePath = "./"

    # TRAINING

    # create ner model and binary relationship extractor
    trainer = ner_trainer('/Users/aduarte/Desktop/MITIE/MITIE-models/english/total_word_feature_extractor.dat')

    # iterate through each band page saved locally
    for band in GLOBAL_BANDS:
        band_token = tokenize(band)
        members = []
        print "GETTING BANDS"
        print "band", band
        # read html from local file
        filename = cachePath + makeFilename(band)
        print "\tfilename", filename
        html = getHtmlFromFilename(filename)
        # get list of members
        members = getTableMembers(html)
        members_token = [tokenize(m) for m in members]
        print "\tmembers", members
        # get phrases from wikipedia text
        phrases = getTextFromHtml(html)
        # for each phrase,
        for phrase in phrases:
            band_indices = []
            # tokenize
            tokens = tokenize(phrase.text)
            sample = ner_training_instance(tokens)
            if len(tokens) > 0:
                # find positions of <band>
                indices = [idx for idx, tok in enumerate(tokens) if tok in band_token]
                breaks = [pos1+1 for pos1, pos2 in zip(indices, indices[1:]) if pos2-pos1 != 1]
                if len(indices)>0:
                    breaks.append(indices[-1])
                k = 0
                for b in breaks:
                    tup = [n for n in indices[k:] if n <= b]
                    if len(tup) > 1:
                        band_indices.append((tup[0], tup[-1]+1))
                    k += len(tup)
                #print [tokens[j[0]:j[1]] for j in band_indices]
                for i in band_indices:
                    print "adding BAND xrange({}, {}) => ({}, {})".format(i[0], i[1], tokens[i[0]], tokens[i[1]-1])
                    sample.add_entity(xrange(i[0], i[1]), "band")
                    trainer.add(sample)
                # find positions of <members>
                for member in members:
                    member_indices = []
                    member_token = tokenize(member)
                    indices = [idx for idx, tok in enumerate(tokens) if tok in member_token]
                    breaks = [pos1+1 for pos1, pos2 in zip(indices, indices[1:]) if pos2-pos1 != 1]
                    if len(indices)>0:
                        breaks.append(indices[-1])
                    k = 0
                    for b in breaks:
                        tup = [n for n in indices[k:] if n <= b]
                        if len(tup) > 1:
                            member_indices.append((tup[0], tup[-1]+1))
                        k += len(tup)
                    #print [tokens[j[0]:j[1]] for j in member_indices]
                    # add binary relations
                    for j in member_indices:
                        try:
                            print "adding MEMBER xrange({}, {}) => ({}, {})".format(j[0], j[1], tokens[j[0]], tokens[j[1]-1])
                            sample.add_entity(xrange(j[0], j[1]), "member")
                            trainer.add(sample)
                        except:
                            pass
        # iterate through each member page saved locally
        for member in members:
            member_token = tokenize(member)
            bands = []
            print "\tGETTING MEMBERS"
            print "\t\tmember", member
            # get local filename
            filename = cachePath + makeFilename(str(member))
            print "\t\tfilename", filename
            # try to get the local html
            try:
                html = getHtmlFromFilename(filename)
                # get list of bands
                bands = getTableBands(html)
                bands_token = [tokenize(b) for b in bands]
                # get phrases from wikipedia text
                phrases = getTextFromHtml(html)
                # for each phrase,
                for phrase in phrases:
                    member_indices = []
                    # tokenize
                    tokens = tokenize(phrase.text)
                    sample = ner_training_instance(tokens)
                    if len(tokens) > 0:
                        # find positions of <member>
                        indices = [idx for idx, tok in enumerate(tokens) if tok in member_token]
                        breaks = [pos1+1 for pos1, pos2 in zip(indices, indices[1:]) if pos2-pos1 != 1]
                        if len(indices)>0:
                            breaks.append(indices[-1])
                        k = 0
                        for b in breaks:
                            tup = [n for n in indices[k:] if n <= b]
                            if len(tup) > 1:
                                member_indices.append((tup[0], tup[-1]+1))
                            k += len(tup)
                        #print [tokens[j[0]:j[1]] for j in member_indices]
                        for i in member_indices:
                            print "adding MEMBER xrange({}, {}) => ({}, {})".format(i[0], i[1], tokens[i[0]], tokens[i[1]-1])
                            sample.add_entity(xrange(i[0], i[1]), "member")
                            trainer.add(sample)
                        # find positions of <bands>
                        for band in bands:
                            band_indices = []
                            band_token = tokenize(band)
                            indices = [idx for idx, tok in enumerate(tokens) if tok in band_token]
                            breaks = [pos1+1 for pos1, pos2 in zip(indices, indices[1:]) if pos2-pos1 != 1]
                            if len(indices)>0:
                                breaks.append(indices[-1])
                            k = 0
                            for b in breaks:
                                tup = [n for n in indices[k:] if n <= b]
                                if len(tup) > 1:
                                    band_indices.append((tup[0], tup[-1]+1))
                                k += len(tup)
                            #print [tokens[j[0]:j[1]] for j in band_indices]
                            # add binary relations
                            for j in band_indices:
                                try:
                                    print "adding BAND xrange({}, {}) => ({}, {})".format(j[0], j[1], tokens[j[0]], tokens[j[1]-1])
                                    sample.add_entity(xrange(j[0], j[1]), "band")
                                    trainer.add(sample)
                                except:
                                    pass
            except:
                pass
            print "\t\tbands", bands

    # save binary relationship extractor
    # ...

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
                # run binary extractor
                # ...
                # return bands
            except:
                print "Could not find {}".format(filename)
        elif user_input.startswith("band "):
            band = user_input.split("band ")[1]
            filename = cachePath + makeFilename(band)
            try:
                html = getHtmlFromFilename(filename)
                # run binary extractor
                # ...
                # return members
            except:
                print "Could not find {}".format(filename)
        else:
            pass

    sys.exit("Bye!")

main()



