'''
Created: 26th June, 2017
@author aguimaraesduarte@usfca.edu
'''

if __name__ == '__main__':
	import sys
	reload(sys)
	sys.setdefaultencoding('utf8')

	from extractor import extractor

	trainerTester = extractor("https://en.wikipedia.org/wiki/{}",
		                      ["10,000 Maniacs",
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
							   "Tom Tom Club"],
							  True,
							  True,
							  0.0,
							  "ner_band_member.dat",
							  "rel_band_to_member.svm",
							  "rel_member_to_band.svm",
							  "/Users/aduarte/Desktop/MITIE/")

	sys.path.append(trainerTester.MITIE_PATH + 'mitielib')
	from mitie import named_entity_extractor, binary_relation_detector
	
	cache_path = trainerTester.getCachePath()
	trainer_ner, trainer_rel_b2m, trainer_rel_m2b = trainerTester.training(cache_path)
	ner_model, rel_model_b2m, rel_model_m2b = trainerTester.modelLoading(trainer_ner, named_entity_extractor, trainer_rel_b2m, trainer_rel_m2b, binary_relation_detector)
	trainerTester.testing(cache_path, ner_model, rel_model_b2m, rel_model_m2b)

	#trainerTester.main()
