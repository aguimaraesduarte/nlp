'''
Created: 1st June, 2017
@author aguimaraesduarte@usfca.edu
'''
from sound import sound
from linguistic_distance import linguistic_distance
from sklearn.cluster import AgglomerativeClustering
import numpy as np

class name_cluster_manager(object):
    '''
    This class is the manager for the name cluster algorithm. It forms clusters and prints them.
    '''


    def __init__(self, argv):
        '''
        Constructor
        '''
        self.names_file = argv[1]
        self.clusters_to_form = int(argv[2])
        self.names = []
        self.soundexes = []
        self.clusters = []

        # Sound object
        self.sound = sound()

        # Linguistic_distance object
        self.ldist = linguistic_distance()

        # Call the read_names function right away
        self.read_names(False)

        # Call the build_soundex_matrix right away
        self.soundex_matrix = np.zeros((len(self.soundexes), len(self.soundexes)))
        self.build_soundex_matrix()


    def read_names(self, clear_names_first):
        '''
        This function reads the names from storage to memory.
        Input: clear_names_first: True if any existing names should be flushed prior to filling self.names.
        Output: none.
        Precondition: self.names_file is a list of names, one per line.
        Postcondition: self.names is a list of names read from self.names_file
        '''
        if clear_names_first:
            self.names = []
            self.soundexes = []
        with open(self.names_file) as f:
            for name in f:
                self.names.append(name.strip())
                self.soundexes.append(self.sound.get_soundex(name.strip()))


    def build_soundex_matrix(self):
        '''
        This function build the soundex matrix with Levenshtein distances between each and every soundex.
        This will be passed to the Agglomerative Clustering function in cluster_names().
        Input: none.
        Outupt: none.
        Precondition: self.soundexes is a list of soundexes corresponding to self.names.
        Postcondition: self.soundex_matrix is a nxn matrix with Levenshtein distances between each soundex.
        '''
        for i, sdx1 in enumerate(self.soundexes):
            for j, sdx2 in enumerate(self.soundexes):
                self.soundex_matrix[i, j] = self.ldist.levenshtein(sdx1, sdx2)

    def cluster_names(self):
        '''
        This function forms clusters according to the requirements.
        Input: none.
        Output: none.
        Precondition: self.soundex_matrix is a nxn zeros matrix.
        Postcondition: self.clusters contains the cluster belongings for each name in names[].
        '''
        # Create and fit AggloClust model
        model = AgglomerativeClustering(n_clusters=self.clusters_to_form)
        self.clusters = model.fit_predict(self.soundex_matrix)


    def print_names(self):
        '''
        This function prints the clusters formed as specified in the pdf.
        Input: none.
        Output: none.
        '''
        for k in range(self.clusters_to_form):
            print " ".join([self.names[i] for i, j in enumerate(self.clusters) if j == k])


