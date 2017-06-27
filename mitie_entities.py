import sys

sys.path.append('/Users/aduarte/Desktop/MITIE/mitielib')

from mitie import *

ner = named_entity_extractor('/Users/aduarte/Desktop/MITIE/MITIE-models/english/ner_model.dat')
possible_tags = ner.get_possible_ner_tags()

# print ''
# print 'Possible Tags:'
# print possible_tags

tokens = tokenize(load_entire_file(sys.argv[1]))
entities = ner.extract_entities(tokens)

# print ''
# print 'Entities Detected:'
# for entity in entities:
#     print ' '.join(tokens[i].decode() for i in entity[0]),
#     print '=>', entity[1]

rel_detector = binary_relation_detector('/Users/aduarte/Desktop/MITIE/MITIE-models/english/binary_relations/rel_classifier_people.person.place_of_birth.svm')
adjacent_entities = [(entities[i][0], entities[i+1][0]) for i in xrange(len(entities)-1)]
adjacent_entities += [(r, l) for (l, r) in adjacent_entities]

# print ''
# print 'Checking birth relationship between:'
# for person, place in adjacent_entities:
#     person_name = ' '.join(tokens[i].decode() for i in person)
#     place_name  = ' '.join(tokens[i].decode() for i in place)
#     print person_name, 'and', place_name

print ''
print "Person born in Place (Score)"
for person, place in adjacent_entities:
    relation = ner.extract_binary_relation(tokens, person, place)
    score = rel_detector(relation)
    person_name = ' '.join(tokens[i].decode() for i in person)
    place_name  = ' '.join(tokens[i].decode() for i in place)
    if score > 0.25:
        print person_name, "born in", place_name, "(", score, ")"