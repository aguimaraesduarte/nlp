'''
Created: 1st June, 2017
@author aguimaraesduarte@usfca.edu
'''
import numpy as np

def levenshtein(str1, str2):
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

usernames = []
with open("usernames.csv", "r") as file:
    for name in file:
        usernames.append(name.strip())

names = []
with open("names.csv", "r") as file:
    for name in file:
        names.append(name.strip())

results = {}
for uname in usernames:
    min_dist = np.inf
    min_name = ''
    for name in names:
        dist =  levenshtein(uname, name)
        if dist < min_dist:
            min_dist = dist
            min_name = name
    results[uname] = min_name

truth = {}
with open("name-username.csv", "r") as file:
    for line in file:
        name = line.split(',')[0].strip()
        uname = line.split(',')[1].strip()
        truth[uname] = name

right = 0
for uname in truth:
    if truth[uname] == results[uname]:
        right += 1

print "accuracy: {}".format(right*1.0/len(results))


