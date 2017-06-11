'''
Created: 1st May, 2017
@author dgbrizan@usfca.edu

You are not allowed to change this file. When submitting, do not submit this file.
'''

if __name__ == '__main__':
    import sys
    from name_cluster_manager import name_cluster_manager

    manager = name_cluster_manager(sys.argv)
    manager.cluster_names()
    manager.print_names()
