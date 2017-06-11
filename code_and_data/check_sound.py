'''
This source file checks the "soundex" function on the "sound" class to ensure the
expected string is generated.

@author dgbrizan@usfca.edu
'''

if __name__ == '__main__':
    from sound import sound

    sound_dictionary = {'California': 'C416',
                        'David': 'D130',
                        'Google': 'G240',
                        'Robert': 'R163',
                        'Rupert': 'R163',
                        'Tigger': 'T260'}

    sound = sound()
    for word in sound_dictionary:
        if sound.get_soundex(word) == sound_dictionary[word]:
            print 'Soundex works for', word
        else:
            print 'Soundex failed for', word, 'generated:', sound.get_soundex(word), 'but expected', sound_dictionary[word]
            exit(-1)
    print 'All soundex tests passed!'
