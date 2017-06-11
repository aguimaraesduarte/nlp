'''
Created: 1st June, 2017
@author aguimaraesduarte@usfca.edu
'''

class sound(object):
    '''
    This class creates an object that allows for transformation of a word into its corresponding soundex.
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.soundex_dict = {
            'b': 1,
            'f': 1,
            'p': 1,
            'v': 1,
            'c': 2,
            'g': 2,
            'j': 2,
            'k': 2,
            'q': 2,
            's': 2,
            'x': 2,
            'z': 2,
            'd': 3,
            't': 3,
            'l': 4,
            'm': 5,
            'n': 5,
            'r': 6,
            'a': 7,
            'e': 7,
            'i': 7,
            'o': 7,
            'u': 7,
            'h': 7,
            'w': 7,
            'y': 7
        }
    
    def get_soundex(self, name):
        '''
        This function transforms a name into its soundex equivalent.
        Input: name: string that we want to get the soundex from.
        Output: string representing the soundex.
        '''
        # if no name provided or not a character string, return 0000
        if (not name) or (not name.isalpha()):
            return '0000'

        # convert name to "full" soundex. First character is uppercase
        soundex = name[0].upper() + ''.join(
            [str(self.soundex_dict.get(letter.lower())) for letter in name[1:]])

        # remove vowels, h, w, y
        soundex = soundex.replace('7', '')

        # remove consecutives
        soundex_copy = soundex[0]
        for num in soundex[1:]:
            if soundex_copy[-1] != num:
                soundex_copy += num

        # potentially pad with 0s and return
        return (soundex_copy + '0000')[:4]



