'''
Created: 1st June, 2017
@author aguimaraesduarte@usfca.edu
'''
import numpy as np

class linguistic_distance(object):
    '''
    This class creates an object that allows for calculation of the Levenshtein distance between two words.
    '''


    def __init__(self):
        '''
        Constructor
        '''
        pass

    def levenshtein(self, str1, str2):
        '''
        This function calculates the Levenshtein distance between two strings.
        Input: str1, str2: the two strings that we want to calculate the Levenshtein distance.
        Output: Levenshtein distance (integer) between the two strings.
        '''
        if (not str1) or (not str2):
            return 0
        if len(str1) == 0:
            return len(str2)
        if len(str2) == 0:
            return len(str1)

        lev = np.zeros((len(str2)+1, len(str1)+1))
        lev[0, :] = range(len(str1)+1)
        lev[:, 0] = range(len(str2)+1)
        for i in range(1, len(str2)+1):
            for j in range(1, len(str1)+1):
                diff = 0
                if str2[i-1] != str1[j-1]:
                    diff = 2
                lev[i, j] = min(
                    lev[i-1, j] + 1,
                    lev[i, j-1] + 1,
                    lev[i-1, j-1] + diff
                )

        return lev[-1, -1]


