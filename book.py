import re, codecs, time, sys, nltk, os, csv, unicodedata, pickle
import storage
import sentence
from multiprocessing import Pool
from nltk.tree import ParentedTree
from nltk import word_tokenize
from nltk.util import ngrams

def uk_to_amer(token):
	"""
	Replace UK spelling with American.
	"""
	token = token.replace('grey', 'gray').replace('colour', 'color').replace("terra cotta", "terra-cotta").replace("-and-", "_and_")
	token = token.replace('Grey', 'Gray').replace('Colour', 'Color').replace("Terra cotta", "Terra-cotta")
	return token

def replace_sentence_colors(sent, color_list):
	"""
	Replace every mention of a color X with __COLOR__X in the sentence sent.
	This is prevent incorrect POS-tagging by Senna. It's fine if objects with the same
	name (e.g. orange, the fruit) are replaced as well - it shouldn't make a difference
	with classification. Following changes are made:

	bright-white ---> __COLOR__bright-white
	X-colored ---> __COLOR__X-colored
	bright lily-white ---> __COLOR__bright-lily-white
	yellow livid ---> __COLOR__yellow __COLOR__livid

	Note that this might cause tagging to be 'NNP' instead of 'NN'.

	"""
	name = ("", -1, -1)	# refers to the color name, start index, end index
	preceding = [''] * 3
	modifiers = ['bright', 'dark', 'light', 'pastel', 'pale', 'deep', 'pure']
	# tokens with original-case but with american spelling
	sentence = [uk_to_amer(token) for token in word_tokenize(sent)]	
	# tokens with lowered case (as in the actual color list)
	tokens = [token.lower() for token in sentence]	
	# subsequences to replace, of the form (start, end, replacement)
	subsequences_to_replace = []

	def add_replacement():
		"""
		Add the color name to the list of replacements to be made. Check the
		preceding words as well.
		"""
		for j in range(len(preceding)):
			extended_name = name

			if '-'.join(preceding[j:] + [name[0].replace('_', '-')]) in color_list:
				# we also move the start index to that of the preceding word
				new_start = name[1] - (len(preceding) - j)
				new_end = name[2]
				# when checking membership in the color list, we use '-' because that's how colors are stored
				# when choosing the modified color, we use '_' because we want to split on it later and return the sentence 
				# to its unmodified form (important for features like word count)
				extended_name = ('_'.join(sentence[new_start:new_end+1]), new_start, new_end)
				break

		subsequences_to_replace.append(extended_name)


	for i, word in enumerate(tokens):
		is_color = word in color_list 

		# check if color is of the form color-X (e.g. pink-flowering, not a new color) 
		# or X-color (e.g. milky-white, which is a new color)
		if not is_color: 
			(new_color, is_color, is_abstract) = extends_color(word, color_list)

			if is_color:
				color_list[new_color] = { 'abstract' : is_abstract, 'non_obj' : True }
				for variation in (mod + '-' + word for mod in modifiers):
					color_list[new_color] = { 'abstract' : is_abstract, 'non_obj' : True }

		# check if color is object-sensitive; if so, add it to the master color list	
		if not is_color: 
			(word, is_color) = is_object_sensitive(word)

			if is_color: 
				color_list[word] = { 'abstract' : False, 'non_obj' : True }
				for variation in (mod + '-' + word for mod in modifiers):
					color_list[variation] = { 'abstract' : False, 'non_obj' : True }

		# if there is a capitalized color not at the start of a sentence, assume it's a name (e.g. Dorian Gray)
		if i > 0 and sentence[i][0] == sentence[i][0].upper():
			is_color = False


		if is_color:
			# name is non-empty only when it has been set to a valid color
			if name[0]:
				# when you can add to the existing color (e.g. bluish + green -> bluish green)
				if (name[0] + '-' + word) in color_list:
					name = (name[0] + '_' + word, name[1], i)
				# case where you have two distinct colors not separated by a comma (e.g. yellow livid skin)
				else:
					add_replacement()
					# reset list of preceding words
					preceding = [''] * 3 
					name = (word, i, i)
			# name is empty
			else: 
				name = (word, i, i)
	
		else: 
			# when no more possible color terms to add, color name cannot possible be longer
			if name[0]:
				add_replacement()
				preceding = [''] * 3 
				name = ("", -1, -1)
			# add non-color terms to list of preceding words 
			preceding.append(word)

			if len(preceding) > 3:
				preceding.pop(0)

	new_tokens = []	# the new sequence of tokens representing the sentence

	for i, word in enumerate(tokens):
		# first check if the word is in a to-be-replaced subsequence
		if subsequences_to_replace and i >= subsequences_to_replace[0][1] and i <= subsequences_to_replace[0][2]:
			# only add the new word once
			if i == subsequences_to_replace[0][1]:
				new_tokens.append('__COLOR__' + subsequences_to_replace[0][0] + '__COLOR__')

			# remove the subsequence from the list once you're done
			if i == subsequences_to_replace[0][2]:
				subsequences_to_replace.pop(0)
		else:
			# remove extra dashes on the end
			new_tokens.append(sentence[i].strip('-').strip(u'\u2014'))

	return new_tokens


def replace_book_colors(book_name, color_list):
	"""
	For every sentence in a formatted book file, replace mentions of colors with __COLOR__X.
	"""
	print book_name

	with codecs.open(book_name, 'r', 'utf-8-sig') as f, codecs.open(book_name.replace('formatted.txt', 'tokenized.txt'), 'w', 'utf-8-sig') as g:
		for i in range(3): 
			g.write(f.readline())

		for line in f:
			g.write(' '.join(replace_sentence_colors(line.strip(), color_list)))
			g.write('\n')


def get_sentences(book_name, color_list):
	"""
	Read the tagged file with name book_name and return a list in the form of (sentence, parse_tree, has_color).
	"""
	sents = []

	with codecs.open(book_name, 'r', 'utf-8-sig') as f:

		count = 0
		current_sent = []	# the current sentence (token sequence)
		current_tree = ""	# the current tree (syntax parse)
		has_color = False 	# if the current sentence has any color, so that you only store text of colorful sentences
		text = []			# in the (sentence, tree) format

		line = f.readline()

		while line:
			
			if not line.strip():			# indicating end of the line
				if current_sent:			# if not blank line, append sentence to list of finished ones
					text.append(( ' '.join(current_sent), current_tree, has_color ))
					
				current_sent = []			# reset sentence, tree, and adj type list
				current_tree = ""
				has_color = False
				count = count + 1

			elif count >= 3:				# skip meta-data, which will be read by the calling function
				columns = line.strip().split()
				token, pos, branch  = unicodedata.normalize('NFKD', columns[0]).encode('ASCII', 'ignore'), columns[1], columns[-1]
				
				# replace parenthenses with their tag (to avoid being mistaked when parsing trees)
				parenth_replacements = { '(' : '-LRB-', ')' : '-RRB-'  }
				token = parenth_replacements.get(token, token)

				# if there are other parentheses, remove them
				token = re.sub(r'[\(\)\[\]\{\}]', '', token)

				token = token.replace("-and-", "_and_")	# underscores will be split on later (handles cases like 'red-and-purple')

				# for colors or things that share a name with a color
				is_color = token.startswith("__COLOR__") and token.endswith("__COLOR__")

				# if the color is not the first word in the sentence and it is capitalized, assume it refers to a name (e.g. Mr. Black)
				if current_sent and is_color and token[9:-9][0] == token[9:-9][0].upper():
					is_color = False
					tokens = ["__NOT__" + token]
				# when you actually have a color ...
				elif is_color:
					# strip the __COLOR__ at both ends
					tokens = token[9:-9].split("_")
				# normal word, not a color
				else:
					# handle edge case that you forgot to handle earlier
					if token.lower().startswith('grey-'):
						token = 'gray-' + token[5:]
					elif token.lower().endswith('grey'):
						token = token[:-4] + 'gray'
					elif token.lower().endswith('colour'):
						token = token[:-6] + 'color'
					elif token.lower().endswith('coloured'):
						token = token[:-8] + 'colored'

					tokens = (token.strip('-') if token.strip('-') else token).split("_") # strip hyphen in weird cases like lips-that
				
				current_sent.extend(tokens)

				# as soon as you encounter a color ...
				if is_color:
					has_color = True

				# add all tokens from the term to the syntax tree (assume everything except last term is automatically an adjective)
				# since in cases like "__COLOR"
				filler = ''.join(['({0} {1})'.format('JJ', tokens[i]) for i in range(len(tokens) - 1)] + ['({0} {1})'.format(pos, tokens[-1])])
				filler = ('(ADJP' if len(tokens) > 1 else '') + filler + (')' if len(tokens) > 1 else '')
				branch = branch.replace('*', filler) 
				current_tree = current_tree + branch

			line = f.readline()

		return text


def get_metadata(book_name):
	"""
	Read the formatted file with name book_name and return a tuple in the form of (title, author, year).
	"""
	with open('metadata.p') as f:
		metadata = pickle.load(f)
		return metadata[ book_name[book_name.rindex('/')+1:].replace('tagged', 'tokenized') ]


def parse_book(book_name, color_list, database_index):
	"""
	Given a book as well as the color list, parse all of the sentences 
	and save the results in the database.
	""" 
	# false_positives_list = []
	# missed_list = []
	# precise_num, precise_denom, recall_num, recall_denom = 0, 0, 0, 0
	# reader = csv.reader(open('test_data.csv'), escapechar='\\')
	# next(reader)

	conn = storage.new_connection(database_index)
	title, author, year = ('Test', 'Irena', 1894) # get_metadata(book_name)
	book_id = storage.add_book(title, author, year, conn)
	text = get_sentences(book_name, color_list)
	
	for index_in_book, (sent, parse, has_color) in enumerate(text):
		# expected = next(reader)
		# #print "EXPECTED " + expected[0]
		# #expected_attr, expected_pred, expected_noun, expected_verb = [], [], [], []
		# expected_attr, expected_pred, expected_noun, expected_verb = expected[1:]
		# expected_attr = re.split(r'\s*,\s*', expected_attr) if expected_attr.strip() else []
		# expected_pred = re.split(r'\s*,\s*', expected_pred) if expected_pred.strip() else []
		# expected_noun = re.split(r'\s*,\s*', expected_noun) if expected_noun.strip() else []
		# expected_verb = re.split(r'\s*,\s*', expected_verb) if expected_verb.strip() else []

		# print >> sys.stderr, (str(index_in_book) + "/" + str(len(text)))
		# print sent
		# print 

		parse = ParentedTree.fromstring(parse)			# parse tree
		pos = sentence.get_pos(parse, False) 			# non-punctuation tags + tokens
		pos_with_punc = sentence.get_pos(parse, True)	# all tags + tokens
		tokens = [ word for tag, word, position in pos ]# tokens (excluding punctuation)

		sent_length = len(pos)			# length of a sentence
		sent_height = parse.height()	# height of a sentence
		periodicity = sentence.get_periodicity(parse)[0]
		vocab_score = sentence.calc_vocab_score(tokens)

		# count the occurrences for each part of speech
		pos_counts_dict = sentence.initialize_counts_dict()
		sentence.get_counts(parse, pos_counts_dict)
		counts = [pos_counts_dict[tag] for tag in sentence.all_pos]
		# print pos_counts_dict

		dep_clauses, indep_clauses = [], []
		attributive, predicative, nouns, verbs = [], [], [], []

		if parse[0].label() in ['X', 'S', 'SBAR', 'SQ', 'SBARQ', 'SINV']: 
			# make a deep copy of the parse before extracting clauses, since the parse is broken down in the process
			# can't do it inside the function because it's recursive
			parse_copy = parse.copy(True)
			(dep_clauses, indep_clauses, _) = sentence.extract_clauses(parse_copy)
			# Add the sentence to the database and keep track of its id in the database.
			sent_id = storage.add_sentence(sent if has_color else "", book_id, index_in_book, sent_length, sent_height, periodicity, len(dep_clauses), len(indep_clauses), vocab_score, counts, conn)

			for clause_group, tag in [(indep_clauses, "IND"), (dep_clauses, "DEP")]:
				for c in clause_group:
					(p, a, n, v, new_color_list) = sentence.get_colors(sentence.get_pos(c, True), color_list, tokens, pos_with_punc, parse, conn)
					
					# Add all the clauses to the database. 
					clause_id = storage.add_clause(sent_id, tag, len(sentence.get_pos(c, False)), c.height(), conn)
					storage.add_mentions(clause_id, p, a, n, v, conn)

					attributive.extend([(color, index, tag) for color, index in a])
					predicative.extend([(color, index, tag) for color, index in p])
					nouns.extend([(color, index, tag) for color, index in n])
					verbs.extend([(color, index, tag) for color, index in v])
					color_list = new_color_list
		else:
			(p, a, n, v, new_color_list) = sentence.get_colors(sentence.get_pos(parse, True), color_list, tokens, pos_with_punc, parse, conn)

			# Add the fragment to the database.
			sent_id = storage.add_sentence(sent if has_color else "", book_id, index_in_book, sent_length, sent_height, periodicity, 0, 0, vocab_score, counts, conn)
			clause_id = storage.add_clause(sent_id, "FRA", sent_length, sent_height, conn)
			storage.add_mentions(clause_id, p, a, n, v, conn)

			attributive.extend([(color, index, 'FRA') for color, index in a])
			predicative.extend([(color, index, 'FRA') for color, index in p])
			nouns.extend([(color, index, 'FRA') for color, index in n])
			verbs.extend([(color, index, tag) for color, index in v])
			color_list = new_color_list

		# print
		# print ("LENGTH:\t\t\t" + str(sent_length))
		# print ("HEIGHT:\t\t\t" + str(sent_height))
		# print ("PERIODICITY:\t\t" + str(periodicity))
		# print
		# print ("ATTRIBUTIVE COLORS:\t" + str(attributive)) # + " " + str(expected_attr))
		# print ("PREDICATIVE COLORS:\t" + str(predicative)) # + " " + str(expected_pred))
		# print ("NOUN COLORS:\t\t" + str(nouns)) # + " " + str(expected_noun))
		# print ("VERB COLORS:\t\t" + str(verbs)) # + " " + str(expected_verb))
		# print
		# print ("DEPENDENT CLAUSES (" + str(len(dep_clauses)) + "):\t\t" + str([' '.join(c.leaves()) for c in dep_clauses]))
		# print ("INDEPENDENT CLAUSES (" + str(len(indep_clauses)) + "):\t" + str([' '.join(c.leaves()) for c in indep_clauses]))
		# print 

	# 	expected = expected_attr + expected_pred + expected_noun + expected_verb
	# 	actual = [ w for w, index, clause_type in attributive + predicative + nouns + verbs ]

	# 	true_positives = 0
	# 	false_positives = 0
	# 	expected_length = len(expected)

	# 	for a in actual:
	# 		try:
	# 			expected.remove(a)
	# 			true_positives = true_positives + 1
	# 		except Exception:
	# 			false_positives_list.append((index_in_book, a))
	# 			false_positives = false_positives + 1

	# 	if expected:
	# 		missed_list.append((index_in_book, expected))

	# 	if true_positives + false_positives > 0:
	# 		precision = true_positives / float(true_positives + false_positives)
	# 	else:
	# 		precision = None

	# 	# the stuff remaining in array actual is that which wasn't caught by the algorithm 
	# 	if expected_length > 0:
	# 		recall = (expected_length - len(expected)) / float(expected_length)
	# 	else:
	# 		recall = None

	# 	print ("PRECISION:\t\t" + str(precision))
	# 	print ("RECALL:\t\t" + str(recall))

	# 	precise_num = precise_num + true_positives
	# 	precise_denom = precise_denom + float(true_positives + false_positives)
	# 	recall_num = recall_num + (expected_length - len(expected))
	# 	recall_denom = recall_denom + float(expected_length)

	# print ("OVERALL PRECISION:\t\t" + str(precise_num / precise_denom))
	# print ("OVERALL RECALL:\t\t" + str(recall_num / recall_denom))
	# print ("FALSE POSITIVES " + str(false_positives_list))
	# print ("MISSED " + str(missed_list))



