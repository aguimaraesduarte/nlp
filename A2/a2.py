import urllib2
from bs4 import BeautifulSoup
import string
import sys
from collections import defaultdict

sys.path.append('/Users/aduarte/Desktop/MITIE/mitielib')
from mitie import *

mainWikiURL = "https://en.wikipedia.org{}"
template_wikiURL = "/wiki/{}"

GLOBAL_BANDS = ["10,000 Maniacs",
         "Belly (band)",
         "Black Star (rap duo)",
         "Bob Marley and the Wailers",
         "The Breeders",
         "Lupe Fiasco",
         "Run the Jewels",
         "Talking Heads",
         "Throwing Muses",
         "Tom Tom Club"]

d = defaultdict(list)

# people = ["Dennis Drew",
#           "Steve Gustafson",
#           "Jerry Augustyniak",
#           "Mary Ramsey",
#           #"Jeff Erickson",
#           "Rob Buck",
#           "John Lombardo",
#           #"Chet Cardinale",
#           #"Teri Newhouse",
#           "Natalie Merchant",
#           #"Tim Edborg",
#           #"Jim Colavito",
#           #"Debbie Heverly",
#           #"Duane Calhoun",
#           #"Bob \"O'Matic\" Wachter",
#           #"Jim Foti",
#           "Oskar Saville"] + \
#          ["Tanya Donelly",
#           #"Thomas Gorman",
#           #"Chris Gorman",
#           #"Fred Abong",
#           "Gail Greenwood"] + \
#          ["Mos Def",
#           "Talib Kweli"] + \
#          ["Bob Marley",
#           "Peter Tosh",
#           "Bunny Wailer",
#           "Junior Braithwaite",
#           "Cherry Smith",
#           "Beverley Kelso",
#           "Constantine Walker",
#           "Aston Barrett",
#           "Carlton Barrett",
#           "Earl Lindo",
#           "Tyrone Downie",
#           "Rita Marley",
#           "Marcia Griffiths",
#           "Judy Mowatt",
#           "Al Anderson",
#           "Alvin Patterson",
#           "Earl \"Chinna\" Smith",
#           "Donald Kinsey",
#           "Junior Marvin"] + \
#          ["Kim Deal",
#           "Kelley Deal",
#           "Josephine Wiggs",
#           "Jim Macpherson",
#           "Jose Medeles",
#           #"Mando Lopez",
#           "Cheryl Lyndsey",
#           "Tanya Donelly",
#           "Carrie Bradley",
#           #"Richard Presley",
#           #"Nate Farley",
#           "Britt Walford",
#           "Jon Mattock"] + \
#          ["El-P",
#           "Killer Mike"] + \
#          ["David Byrne",
#           "Chris Frantz",
#           "Tina Weymouth",
#           "Jerry Harrison"] + \
#          ["Kristin Hersh",
#           "David Narcizo",
#           "Bernard Georges",
#           #"Leslie Langston",
#           #"Fred Abong",
#           #"Elaine Adamedes",
#           #"Becca Blumen",
#           "Tanya Donelly"] + \
#          ["Chris Frantz",
#           "Tina Weymouth",
#           #"Bruce Martin",
#           "Victoria Clamp",
#           "Pablo Martin",
#           "Adrian Belew",
#           #"Monte Browne",
#           "Tyrone Downie",
#           #"Mark Roule",
#           #"Gary Pozner",
#           #"Steve Scales",
#           "Steven Stanley",
#           "Alex Weir",
#           #"Mystic Bowie",
#           #"Laura Weymouth",
#           "Charles Pettigrew",
#           "Wally Badarou"]


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
    # ...

    # iterate through each band page saved locally
    for band in GLOBAL_BANDS:
        band_token = tokenize(band)
        members = []
        # print "GETTING BANDS"
        # print "band", band
        # read html from local file
        filename = cachePath + makeFilename(band)
        # print "\tfilename", filename
        html = getHtmlFromFilename(filename)
        # get list of members
        members = getTableMembers(html)
        members_token = [tokenize(m) for m in members]
        # print "\tmembers", members
        # get phrases from wikipedia text
        phrases = getTextFromHtml(html)
        # for each phrase, tokenize and find positions of <band> + <members>
        for phrase in phrases:
            tokens = tokenize(phrase.text)
            # ...
        # ...
        # iterate through each member page saved locally
        for member in members:
            bands = []
            # print "\tGETTING MEMBERS"
            # print "\t\tmember", member
            # get local filename
            filename = cachePath + makeFilename(str(member))
            # print "\t\tfilename", filename
            # try to get the local html
            try:
                html = getHtmlFromFilename(filename)
            except:
                pass
            # get list of bands
            bands = getTableBands(html)
            bands_token = [tokenize(b) for b in bands]
            # print "\t\tbands", bands
            # build binary relations
            # ...

    # save binary relationship extractor
    # ...

    # TESTING
    # ask user for input
    user_input = ''
    while user_input != "quit":
        user_input = raw_input("Find: ")

    sys.exit("Bye!")

main()



