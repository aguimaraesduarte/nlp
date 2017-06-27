'''
Created: 26th June, 2017
@author aguimaraesduarte@usfca.edu
'''

class extractor(object):
	"""
	This class performs entity extraction of bands/persons using html wikipedia pages.
	It also creates binary relations between said entities within pages.
	It also tries to find said relations using only the html text of a possibly unknown page.
	"""

	def __init__(self, wiki_url_, bands_list_, train_ner_, train_rel_, threshold_, ner_model_name_, rel_model_name_, mitie_path_):
		"""
		Constructor
		"""
		self.WIKI_URL = wiki_url_

		self.BANDS = bands_list_

		self.TRAIN_NER = train_ner_
		self.TRAIN_REL = train_rel_
		self.SCORE_THRESHOLD = threshold_

		self.NER_MODEL_NAME = ner_model_name_
		self.REL_MODEL_NAME = rel_model_name_

		self.MITIE_PATH = mitie_path_

	def parseArgs(self):
		import sys
		"""
		This function returns the path of the cached html files if provided.
		"""
		if len(sys.argv) > 1:
			arg = sys.argv[1]

			if arg.startswith("-cached="):
				path = arg[8:]

				return path

			else:
				sys.exit("Need a '-chached=' command line argument with the path where the files are stored.")
		else:
			sys.exit("Need a '-chached=' command line argument with the path where the files are stored.")


	def getCachePath(self):
		"""
		This function returns the full path of the cache'd html files.
		If no such path is passed, it will get the html files of the input bands and save them to the
		current directory.
		"""
		cachePath = self.parseArgs()
		if not cachePath:
			self.getAndSavePages(self.BANDS)
			cachePath = "./"
		return cachePath


	def getHtmlFromFilename(self, filename_):
		from bs4 import BeautifulSoup
		"""
		This function returns the html from an input file as text.
		"""
		with open(filename_, "r") as f:
			html = BeautifulSoup(f.read(), "html.parser")

		return html


	def getHtmlFromUrl(self, URL_):
		import urllib2
		from bs4 import BeautifulSoup
		"""
		This function returns the html from an input wikipedia URL.
		"""
		response = urllib2.urlopen(URL_)
		html = BeautifulSoup(response, "html.parser")
		return html


	def stringToWikiUrl(self, searchString_):
		"""
		This function returns the input string where the spaces are converted to underscores
		in order to use it as a wikipedia URL.
		"""
		return "_".join(searchString_.split()) # Something_like_this


	def getHtmlFromSearchString(self, searchString_):
		"""
		This function returns the html from the wikipedia page corresponding to the input string.
		If no page is found, return an error string
		"""
		wikiURL = self.stringToWikiUrl(searchString_)
		URL = self.WIKI_URL.format(wikiURL)
		try:
			return str(getHtmlFromUrl(URL))

		except Exception, e:
			return "{} is not a valid search term".format(searchString_)


	def makeFilename(self, searchString_):
		import string
		"""
		This function transforms an input string into a valid html filename for saving.
		"""
		return searchString_.translate(None, string.punctuation).replace(" ", "_") + ".html"


	def saveHtmlToFile(self, html_, searchString_):
		"""
		This function saves the input html into a filename based on the input string.
		"""
		with open(self.makeFilename(searchString_), "w") as f:
			f.write(html_)


	def getAndSavePages(self, listOfStrings_):
		"""
		This function gets and saves the html from an input list of strings (band names, members, etc).
		"""
		for element in listOfStrings_:
			html = self.getHtmlFromSearchString(element)
			self.saveHtmlToFile(html, element)


	def getTextFromHtml(self, html_):
		"""
		This function extracts all the <p> tags from an html document.
		"""
		return html_.findAll('p')


	def getSidebarElements(self, html_, text_):
		"""
		This function returns all elements matching text_ from the html sidebar.
		"""
		elements = []
		try:
			th = html_.findAll('th', text=text_)[0]
			td = th.findNext('td')
			elements.extend([li.text for li in td.findAll('li')])
			elements.extend([a.text for a in td.findAll('a')])

		except:
			None

		return elements


	def getTableMembers(self, html_):
		"""
		This function returns a list of all members of a given band from the html document.
		"""
		artists = []
		artists.extend(self.getSidebarElements(html_, "Members"))
		artists.extend(self.getSidebarElements(html_, "Past Members"))

		return artists


	def getTableBands(self, html_):
		"""
		This function returns all the associated acts (alias for bands) from a person's html page.
		"""
		bands = []
		bands.extend(self.getSidebarElements(html_, "Associated acts"))

		return bands


	def createTupleIndices(self, breaks_, indices_, ner_indices_, grp_token_):
		"""
		This function creates tuple indices of start and end positions of a tag.
		"""
		k = 0
		for b in breaks_:
			tup = [n for n in indices_[k:] if n <= b]

			if len(tup) == len(grp_token_):
				ner_indices_.append((tup[0], tup[-1]+1))
			k += len(tup)


	def addNerEntities(self, indices_, tokens_, sample_, trainer_ner_, rel_):
		"""
		This function adds entities to an NER trainer based on the matching positions.
		"""
		for j in indices_:
			try:
				print "Adding {} xrange({}, {}) => ({})".format(rel_, j[0], j[1], tokens_[j[0]:j[1]])
				sample_.add_entity(xrange(j[0], j[1]), rel_)
				trainer_ner_.add(sample_)

			except:
				pass


	def findPositions(self, group_, tokens_, sample_, trainer_ner_, cond_NER_, trainer_rel_, cond_REL_, grp2_indices_, rel_):
		import sys
		# sys.path.append(self.MITIE_PATH + 'mitielib')
		from mitie import tokenize
		"""
		This function iterates through a group (band/person) find the positions of each entity,
		and adds the corresponding entities to the NER trainer if one is being trained.
		If a REL model is being trained, the positive/negative binary relationships are added to it.
		"""
		for grp in group_:
			grp_indices = []
			grp_token = tokenize(grp)
			indices = [idx for idx, tok in enumerate(tokens_) if tok in grp_token]
			breaks = [pos1+1 for pos1, pos2 in zip(indices, indices[1:]) if pos2-pos1 != 1]

			if len(indices) > 0:
				breaks.append(indices[-1])
			# create list of tuples
			self.createTupleIndices(breaks, indices, grp_indices, grp_token)

			if cond_NER_:
				# add binary relations
				self.addNerEntities(grp_indices, tokens_, sample_, trainer_ner_, rel_)

			if cond_REL_:
				for i in grp2_indices_:
					for j in grp_indices:
						try:
							trainer_rel_.add_positive_binary_relation(tokens_, xrange(i[0], i[1]), xrange(j[0], j[1]))
							trainer_rel_.add_negative_binary_relation(tokens_, xrange(j[0], j[1]), xrange(i[0], i[1]))

							print "Added relationship"

						except:
							pass


	def iteratePhrases(self, phrases_, rel_, rel2_, trainer_ner_, cond_NER_, trainer_rel_, cond_REL_, grp2_, grp_token_):
		import sys
		# sys.path.append(self.MITIE_PATH + 'mitielib')
		from mitie import tokenize, ner_training_instance
		"""
		This function iterates through the phrases of a document and add NER entities to the trainer if
		an NER is being trained. Then it iterates through the groups to add subsequent entities from the tree.
		"""
		for phrase in phrases_:
			grp_indices = []
			# tokenize
			tokens = tokenize(phrase.text)
			sample = ner_training_instance(tokens)

			if len(tokens) > 0:
				# find positions of <rel_>
				indices = [idx for idx, tok in enumerate(tokens) if tok in grp_token_]
				breaks = [pos1+1 for pos1, pos2 in zip(indices, indices[1:]) if pos2-pos1 != 1]

				if len(indices) > 0:
					breaks.append(indices[-1])
				# create list of tuples
				self.createTupleIndices(breaks, indices, grp_indices, grp_token_)

				if cond_NER_:
					# add binary relations
					self.addNerEntities(grp_indices, tokens, sample, trainer_ner_, rel_)

				# find positions of <rel2_>
				self.findPositions(grp2_, tokens, sample, trainer_ner_, cond_NER_, trainer_rel_, cond_REL_, grp_indices, rel2_)


	def extractFromHtml(self, cpath_, grpname_, grp_, grp2_, trainer_ner_, cond_NER_, trainer_rel_, cond_REL_):
		import sys
		# sys.path.append(self.MITIE_PATH + 'mitielib')
		from mitie import tokenize
		"""
		This function gets the elements from the sidebar, gets the phrases (<p> tags) from the html,
		and iterates through them adding the entities to the NER and/or REL trainer.
		"""
		# tokenize group name
		grp_token = tokenize(grpname_)
		# make filename
		filename = cpath_ + self.makeFilename(str(grpname_))
		# print "\tfilename", fn
		html = self.getHtmlFromFilename(filename)
		# get list of grp
		if grp_ == "band":
			grp = self.getTableMembers(html)

		else:
			grp = self.getTableBands(html)

		# get phrases from wikipedia text
		phrases = self.getTextFromHtml(html)
		# iterate through phrases
		self.iteratePhrases(phrases, grp_, grp2_, trainer_ner_, cond_NER_, trainer_rel_, cond_REL_, grp, grp_token)

		return grp


	def printRelations(self, adj_ent_, ner_model_, rel_model_, tokens_, grp_, grpname_, l_names_, thresh_):
		"""
		This function print the relations found by the model with the corresponding score.
		A threshold can be specified to limit these matchings.
		"""
		for i, j in adj_ent_:
			relation = ner_model_.extract_binary_relation(tokens_, i, j)
			score = rel_model_(relation)
			i_name = ' '.join(tokens_[i].decode() for i in i)
			j_name = ' '.join(tokens_[i].decode() for i in j)

			if i_name == grp_ and i_name != j_name and j_name not in l_names_ and score > thresh_:
				if grpname_ == "band":
					print i_name, "has member", j_name, "(", score, ")"

				else:
					print i_name, "in band", j_name, "(", score, ")"

				l_names_.append(j_name)


	def findFromHtml(self, html_, ner_model_, rel_model_, grp_, grpname_, thresh_):
		import sys
		# sys.path.append(self.MITIE_PATH + 'mitielib')
		from mitie import tokenize
		"""
		This function extracts the text from an html document, iterates through the phrases (<p> tags)
		and print the relations found within it.
		If no relations were found, then it prints an informative output.
		"""
		# get phrases from wikipedia text
		phrases = self.getTextFromHtml(html_)
		l_names = []
		for phrase in phrases:
			# tokenize
			tokens = tokenize(phrase.text)

			if len(tokens) > 0:
				# run ner
				entities = ner_model_.extract_entities(tokens)
				adjacent_entities = [(entities[i][0], entities[i+1][0]) for i in xrange(len(entities)-1)]
				adjacent_entities += [(r, l) for (l, r) in adjacent_entities]
				# run rel extractor
				self.printRelations(adjacent_entities, ner_model_, rel_model_, tokens, grp_, grpname_, l_names, thresh_)

		if len(l_names) == 0:
			print "Could not find anything."


	def tryExtract(self, grp_, grpname_, cpath_, ner_model_, rel_model_, thresh_):
		"""
		This function attempts to get an html document from the path given.
		If not found, an informative output is shown.
		"""
		filename = cpath_ + self.makeFilename(grp_)
		try:
			html = self.getHtmlFromFilename(filename)

			try:
				self.findFromHtml(html, ner_model_, rel_model_, grp_, grpname_, thresh_)

			except:
				print "Failed."

		except:
			print "Could not find {}.".format(filename)


	def trainLoadModel(self, condition_, type_, trainer_, fun_model_, save_filename):
		import sys
		"""
		This function trains a given model (NER or REL).
		If no training is to be done, this function attempts to load a previously trained and saved one.
		This function returns said model.
		If no model could be loaded, the program exits.
		"""
		if condition_:
			print """
			========================
			Training new {} model
			========================
			""".format(type_)
			# train ner model
			model = trainer_.train()
			try:
				print """
				========================
				Model trained with tags: {}
				========================
				""".format(model.get_possible_ner_tags())
			except:
				pass
			model.save_to_disk(save_filename)

		else:
			try:
				print """
				========================
				Loading already trained {} model
				========================
				""".format(type_)
				model = fun_model_(save_filename)

			except:
				print "========================"
				print "Could not load already trained {} model".format(type_)
				print "Run again with option TRAIN_{} enabled".format(type_)
				sys.exit(1)

		return model


	def modelLoading(self, trainer_ner_, fun_ner_, trainer_rel_, fun_rel_):
		"""
		This function traind/loads the three models we want (NER, REL Band to Member, REL Member to Band).
		"""
		ner_model = self.trainLoadModel(self.TRAIN_NER, "NER", trainer_ner_, fun_ner_, self.NER_MODEL_NAME)
		rel_model = self.trainLoadModel(self.TRAIN_REL, "REL", trainer_rel_, fun_rel_, self.REL_MODEL_NAME)

		return ner_model, rel_model


	def modelTraining(self, bands_list_, cpath_, trainer_ner_, cond_NER_, trainer_rel_, cond_REL_):
		"""
		This function performs the model training by iterating through the saved bands as well as each artist within a page.
		"""
		# iterate through each band page saved locally
		for band in bands_list_:
			print "Getting band", band
			try:
				members = self.extractFromHtml(cpath_, band, "band", "person", trainer_ner_, cond_NER_, trainer_rel_, cond_REL_)
			except:
				pass

			# iterate through each member page saved locally
			for member in members:
				print "\tGetting member", member
				try:
					self.extractFromHtml(cpath_, member, "person", "band", trainer_ner_, cond_NER_, trainer_rel_, cond_REL_)
				except:
					pass


	def training(self, cpath_):
		import sys
		# sys.path.append(self.MITIE_PATH + 'mitielib')
		from mitie import ner_trainer, named_entity_extractor, binary_relation_detector_trainer
		"""
		This function trains and returns an NER and REL models.
		"""
		# create ner model and binary relationship extractor
		trainer_ner = ""
		trainer_rel = ""

		if self.TRAIN_NER:
			print """
			========================
			Will train NER
			========================
			"""
			trainer_ner = ner_trainer(self.MITIE_PATH + 'MITIE-models/english/total_word_feature_extractor.dat')

		if self.TRAIN_REL:
			print """
			========================
			Will train REL
			========================
			"""
			try:
				ner = named_entity_extractor(self.NER_MODEL_NAME)
				trainer_rel = binary_relation_detector_trainer('rel.band.member', ner)

			except:
				sys.exit("Error! NER was not found. Run again with the training NER option set to True.")
			
		if self.TRAIN_NER or self.TRAIN_REL:
			print """
			========================
			Model(s) training
			========================
			"""
			self.modelTraining(self.BANDS, cpath_, trainer_ner, self.TRAIN_NER, trainer_rel, self.TRAIN_REL)

		return trainer_ner, trainer_rel


	def testing(self, cpath_, ner_model_, rel_model_):
		import sys
		"""
		This function performs the testing of the models on user input queries.
		"""
		# ask user for input
		user_input = ''

		while user_input != "quit":
			user_input = raw_input("Find: ")

			if user_input.startswith("person "):
				member = user_input.split("person ")[1]
				self.tryExtract(member, "member", cpath_, ner_model_, rel_model_, self.SCORE_THRESHOLD)

			elif user_input.startswith("band "):
				band = user_input.split("band ")[1]
				self.tryExtract(band, "band", cpath_, ner_model_, rel_model_, -self.SCORE_THRESHOLD)

			elif user_input == "quit":
				sys.exit("Bye")

			else:
				print "Could not parse request. Follow the format below or type <quit> to exit."
				print "Find: <person|band> <name of person|band>"


	def main(self):
		"""
		This function defines the general steps in order to perform training and/or testing.
		"""
		# get cached path argument from command line
		cache_path = self.getCachePath()

		# TRAINING
		trainer_ner, trainer_rel = self.training(cache_path)

		# train/load models
		ner_model, rel_model = self.modelLoading(trainer_ner, named_entity_extractor, trainer_rel, binary_relation_detector)

		# TESTING
		self.testing(cache_path, ner_model, rel_model)
