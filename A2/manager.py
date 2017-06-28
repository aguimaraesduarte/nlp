'''
Created: 26th June, 2017
@author aguimaraesduarte@usfca.edu
'''

if __name__ == '__main__':
	import sys
	reload(sys)
	sys.setdefaultencoding('utf8')

	from extractor1 import extractor

	wiki_url_ = "https://en.wikipedia.org/wiki/{}"
	bands_list_ = ["10,000 Maniacs",
				   "Belly",
				   "Belly (band)",
				   "Black Star",
				   "Black Star (rap duo)",
				   "Bob Marley and the Wailers",
				   "The Breeders",
				   "Lupe Fiasco",
				   "Run the Jewels",
				   "Talking Heads",
				   "Throwing Muses",
				   "Tom Tom Club"]
	train_ner_ = False
	train_rel_ = False
	threshold_ = 0.0
	ner_model_name_ = 'model_ner.dat'
	rel_model_name_ = 'model_rel.svm'
	mitie_path_ = "/Users/aduarte/Desktop/MITIE/"

	trainerTester = extractor(wiki_url_ = wiki_url_,
		                      bands_list_ = bands_list_,
							  train_ner_ = train_ner_,
							  train_rel_ = train_rel_,
							  threshold_ = threshold_,
							  ner_model_name_ = ner_model_name_,
							  rel_model_name_ = rel_model_name_,
							  mitie_path_ = mitie_path_)

	sys.path.append(trainerTester.MITIE_PATH + 'mitielib')
	from mitie import named_entity_extractor, binary_relation_detector
	
	cache_path = trainerTester.getCachePath()
	trainer_ner, trainer_rel = trainerTester.training(cache_path)
	ner_model, rel_model = trainerTester.modelLoading(trainer_ner, named_entity_extractor, trainer_rel, binary_relation_detector)
	trainerTester.testing(cache_path, ner_model, rel_model)

	# trainerTester.main()
