import os, sys, nltk, csv
import color_analysis as ca
import re
from nltk.tree import Tree, ParentedTree
from nltk.wsd import lesk
from curses.ascii import isdigit
import storage, pickle, codecs, math
from nltk.stem import snowball

modifiers = ['bright', 'dark', 'light', 'pastel', 'pale', 'deep', 'pure']
punc_tags = ['-LRB-', '-RRB-', ':', ',', '.', 'POS', 'SYM', '``', "''"]
stoplist = set("""( ) : , . { } [ ] ; . ' " ! ? @ # $ % * \ + what at "n't" if for a an on of the and to from in by or either neither so where there those these this that it which who whose but be is have should would it about into 've he she them i i. w. hi him her my me you your their our we with 't 's then than when have not""".split())
all_pos = ['S','SBAR','SBARQ','SINV','SQ','ADJP','ADVP','CONJP','FRAG','INTJ','LST','NAC','NP','NX','PP','PRN','PRT','QP','RRC','UCP','VP','WHADJP','WHAVP','WHNP','WHPP','X','CC','CD','DT','EX','FW','IN','JJ','JJR','JJS','LS','MD','NN','NNS','NNP','NNPS','PDT','POS','PRP','PRP$','RB','RBR','RBS','RP','SYM','UH','VB','VBD','VBG','VBN','VBP','VBZ','WDT','WP','WP$','WRB']
corpus_count = pickle.load(open('word_count.p'))


def initialize_counts_dict():
	"""
	Return a dictionary of parts-of-speech counts.
	"""
	pos_counts = {}

	for pos in all_pos: 
		pos_counts[pos] = 0

	return pos_counts


def get_counts(t, counts):
	"""
	Update the pos counts dictionary with the number of nodes in tree t with each part of speech.
	"""
	if t.label() in counts:
		counts[t.label()] = counts[t.label()] + 1

	for i in range(len(t)):
		if isinstance(t[i], Tree):
			get_counts(t[i], counts)


def get_pos(t, include_punc):
	"""
	Return the parts-of-speech and pre-order position of all words in the parse tree t, except for punctuation 
	if include_punc is set to True.
	"""
	punctuation = [] if include_punc else punc_tags
	pos_trees = list(t.subtrees(filter = lambda st: (len(st) > 0) and (not isinstance(st[0], Tree)) and (not st.label() in punctuation)))
	# no need to lowercase words since that should have been done in pre-processing
	pos_and_positions = [ [pos_tree.label(), pos_tree[0]] for pos_tree in pos_trees ]
	# the pre-order positions for the leaves (leave out punctuation if necessary)
	leaf_positions = [ position for position in t.treepositions('leaves') if t[position[:-1]].label() not in punctuation]

	# add the pre-order position, since you want to be able to access specific nodes in the tree
	for i, pre_order_position in enumerate(leaf_positions): 
		# assume that the order in which the leaf nodes are extracted is the order in which their words actually appear
		assert t[pre_order_position] == pos_and_positions[i][1]
		# exclude the last index of the pre-order position, because you want the leaf node, not the string
		pos_and_positions[i].append(pre_order_position[:-1])

	return pos_and_positions


def get_periodicity(t, distance_from_start=0, distance_from_root=0):
	"""
	Return the index of the first word in the top-level verb phrase in the sentence. The higher
	the index, the greater the periodicity. 
	"""
	min_dist_from_root = sys.maxint 	# distance from top level verb phrase to root
	min_periodicity = -1				# index of first word in top-level verb phrase

	if isinstance(t, Tree):
		# exclude verb phrases with gerunds (e.g. 'Crossing the road, I ...')
		if(t.label() == 'VP') and any(st.label() in ['VBP', 'VBZ', 'VBD', 'VBN', 'VB'] for st in t):
			min_dist_from_root = distance_from_root		# vertical distance from root
			# main verb may not be the first subtree, so find the index of the first verb in verb phrase
			min_periodicity = distance_from_start + next(i for i in range(len(t)) if t[i].label() in ['VBP', 'VBZ', 'VBD', 'VBN', 'VB'])	
		else: 
			# recursively call the method on all of t's children to find the top level VP 
			for i in range(len(t)):
				if isinstance(t[i], Tree):
					(p, d) = get_periodicity(t[i], distance_from_start, distance_from_root+1)
					# distance from start increases as you go through subtrees from left to right
					# only include non-punctuation tokens in this distance
					distance_from_start = distance_from_start + len(list(t[i].subtrees(filter = lambda st: (not isinstance(st[0], Tree)) and (not st.label() in punc_tags))))

					# closeness to the root takes priority (actual periodicity value is secondary)
					if (d < min_dist_from_root) or ((d == min_dist_from_root) and (p < min_periodicity)):
						min_dist_from_root = d
						min_periodicity = p

	return (min_periodicity, min_dist_from_root)


def calc_vocab_score(tokens):
	"""
	Return a float that represents the richness of the vocabulary in the sentence. The more unique the 
	vocabulary, the higher the score (all scores are positive). The score is calculated as
	follows: for every word w in the sentence, score = \sum{ log( ||C|| / w_c ) } / len(tokens), where 
	w_c is the frequency in the corpus. This favours the use of rare words over penalization of the use
	of common words.
	"""
	stemmer = snowball.EnglishStemmer() # for stemming words so that different forms aren't counted separately
	score = 0
	num_used = 0	# number of tokens actually used in the calculation

	for token in tokens:
		token = stemmer.stem(token.lower())

		if token in corpus_count:	# this check automatically excludes stopwords and pronouns
			score = score + math.log( corpus_count['_TOTAL_'] ) - math.log( corpus_count[token] )
			num_used = num_used + 1

	return score / max(float(num_used), 1)
	# return score


# Need this because clauses aren't necessarily contiguous.
def get_most_probable_index(index_in_clause, clause_pos, item, sent_pos): 
	"""
	Given a (tag, word) pair called item in the clause clause_pos, and the index of item in the clause,
	find and return the index of item in the overall sentence sent_pos. Note: both sentence and clause
	are represented by their parts of speech.
	"""
	# all possible indices of word in overall sentence (more than one if it appears multiple times)
	# note that item only contains (tag, word) whereas sent_pos also contains pre_order position
	indices = [i for i, x in enumerate(sent_pos) if x[:2] == item]

	"""
	For each possible index, we radiate outwards to check if the neighbours of the word at the index
	in the sentence match the neighbours of item in the clause. Of the possible indices, the one with 
	greatest number of matching neighbours wins. Only in rare cases will dist need to be incremented.
	"""
	# distance at which neighbours are examined (e.g. 1 word away, 2 words away, etc)
	dist = 1 

	# do until there is only one possible index
	while len(indices) > 1: 	
		for index in indices:
			# can't remove an index more than once
			removed = False
			# make sure not to go out of bounds
			if (index_in_clause - dist) >= 0 and (index - dist) >= 0:
				if (clause_pos[index_in_clause - dist][:2] != sent_pos[index - dist][:2]):
					indices.remove(index)
					removed = True 

			if (not removed) and (index_in_clause + dist) < len(clause_pos) and (index + dist) < len(sent_pos):
				if (clause_pos[index_in_clause + dist][:2] != sent_pos[index + dist][:2]):
					indices.remove(index)
			
			if len(indices) == 1: 
				break 

		dist += 1 

	return indices[0]


def get_colors(clause_pos, color_list, tokens, sent_pos, parse, conn):
	"""
	Return a list of predicative colors and a list of attributive colors in the phrase represented
	by the parts-of-speech list pos.
	"""
	predicative, attributive, nouns, verbs = [], [], [], []
	types = { 'noun' : nouns, 'pred' : predicative, 'attr' : attributive, 'verb' : verbs }

	prev, prev_tag = "", ""				# used to keep track of previous word and tag
	name = ""							# the part of the color name that has been extracted so far	
	clause_index = 0					# index of the word in the clause
	preceding = [''] * 3 				# list of words preceding the current word 

	"""
	The list of preceding words is needed to catch terms that have multiple components that are not
	colors on their own (e.g. bright Tyrian purple). In the list of colors, there are never more than 
	2 such preceding terms for any color (the list is size three here for good measure).
	"""	

	def add_current_color():
		"""
		Add the current contents of the variable name to appropriate list of colors. If the list 
		preceding contains some sublist of valid prefixes/modifiers, add those as well.
		"""
		# the name of the color to be added
		new_name = name

		# find the largest sublist preceding[j:], where each item can be prefixed to the name
		for j in range(len(preceding)):
			if '-'.join(preceding[j:] + [name]) in color_list:
				new_name = '-'.join(preceding[j:] + [name])
				break

		# clause_index-1 is used because the index of the color is the one before the current word
		i = get_most_probable_index(clause_index-1, clause_pos, [prev_tag, prev], sent_pos)
		
		# for noun colors, it is enough to check the tag
		if sent_pos[i][0] in ['NN', 'NNP', 'NNS', 'NNPS']:
			# hack: assume that colors that are nouns are actually attributive if they appear immediately before a noun (improves accuracy)
			if i + 1 < len(sent_pos) and sent_pos[i+1][0] in ['NN', 'NNP', 'NNS', 'NNPS']:
				parse[sent_pos[i][2]].set_label('JJ')
				color_type = 'attr'
			# hack: when VP (NP (NN), go with VP, and set NN to JJ instead
			elif len(parse[sent_pos[i][2]].parent()) == 1 and parse[sent_pos[i][2]].parent().label() == 'NP' and parse[sent_pos[i][2]].parent().parent().label() == 'VP':
				parse[sent_pos[i][2]].set_label('JJ')
				color_type = 'pred'
			else:
				color_type = 'noun'

		elif sent_pos[i][0].startswith('VB'):
			color_type = 'verb'
		# for attributive colors, keep going up the tree until you hit a VP (predicative) or NP ()
		elif sent_pos[i][0] in ['JJ', 'JJS', 'JJR']:
			node = parse[sent_pos[i][2]]

			while node and node.label() not in ['VP', 'NP']:
				node = node.parent()

			if not node:
				color_type = 'noun'
			elif node.label() == 'NP':
				color_type = 'attr'
			elif node.label() == 'VP':
				color_type = 'pred'
				
		types[color_type].append((new_name, i)) 


	for tag, word, pre_order_position in clause_pos: 
		# If a word is an adjective, it might be a color. If it's a noun and cannot be an object, it's a color.
		maybe_color = (tag in ['JJ', 'JJS', 'JJR']) 
		is_color = False
		original = word

		# first, check for plurals (most colors just have an extra -s, -es, -ies at the end)
		if tag in ['NNS', 'NNPS']:
			if word[-1] == 's' and word[:-1] in color_list:
				word = word[:-1]
			elif len(word) >= 2 and word[-2:] == 'es' and word[:-2] in color_list:
				word = word[:-2]
			elif len(word) >= 3 and word[-3:] == 'ies' and word[:-3] in color_list:
				word = word[:-3]

		# if color is a noun and ...
		if (not maybe_color) and color_list.get(word) and tag in ['NN', 'NNP', 'NNS', 'NNPS']:
			# it cannot be an object, then it may be a color
			if color_list[word]['non_obj']:
				maybe_color = True
			# or if 'color' or 'color' appear in a 5-word window, the reference is probably not to an object definition
			else:
				window = [w for t, w, p in clause_pos[max(0, clause_index-10):clause_index+10]] 
				if 'color' in window or 'colored' in window or 'hue' in window or 'tint' in window:
					maybe_color = True

		# edge case: catch compound words that are tagged as nouns but which have some component that is a non-obj color
		if (not maybe_color) and (tag in ['NN', 'NNP', 'NNS', 'NNPS']):
			maybe_color = any((color_list.get(w) and color_list[w]['non_obj']) for w in word.split('-'))

		# colors may also be verbs (check tenses and switch to base form)
		if (not maybe_color) and tag.startswith('VB'):
			if word in color_list:
				maybe_color = True 
			elif word.endswith('ing') and word[:-3] in color_list:
				word = word[:-3]
				maybe_color = True
			elif word.endswith('ed') and word[:-2] in color_list:
				word = word[:-2]
				maybe_color = True 	

		# if the color is capitalized and not at the start of a sentence (i.e. non-null prev), then assume it's a name
		if prev and word[0] == word[0].upper():
			maybe_color = False 

		if maybe_color:
			is_color = (word in color_list)

			# check if color is object-sensitive; if so, add it to the master color list	
			if not is_color: 
				(word, is_color) = is_object_sensitive(word, conn)
				if is_color: 
					color_list[word] = { 'abstract' : False, 'non_obj' : True }
					for variation in (mod + '-' + word for mod in modifiers):
						color_list[variation] = { 'abstract' : False, 'non_obj' : True }

			# check if color is of the form color-X (e.g. pink-flowering, not a new color) 
			# or X-color (e.g. milky-white, which is a new color)
			if not is_color: 
				(word, is_color, is_abstract) = extends_color(word, color_list, conn)
				if is_color and word not in color_list:
					color_list[word] = { 'abstract' : is_abstract, 'non_obj' : True }
					for variation in (mod + '-' + word for mod in modifiers):
						color_list[variation] = { 'abstract' : is_abstract, 'non_obj' : True }

			if is_color:
				# name is non-empty only when it has been set to a valid color
				if name:
					# when you can add to the existing color (e.g. bluish + green -> bluish green)
					if (name + '-' + word) in color_list:
						name += '-' + word
					# case where you have two distinct colors not separated by a comma (e.g. yellow livid skin)
					else:
						add_current_color()
						# reset list of preceding words
						preceding = [''] * 3 
						name = word 
				# name is empty
				else: 
					name = word
		
		if not is_color: 
			# when no more possible color terms to add, color name cannot possible be longer
			if name:
				add_current_color()
				preceding = [''] * 3 
				name = ""
			# add non-color terms to list of preceding words (they may actually be part of the color in the end)
			# lowercase because they're not so by default
			preceding.append(word.lower())

			if len(preceding) > 3:
				preceding.pop(0)

		clause_index += 1 
		# use original here because some words (e.g. pink-flowering) might have changed 
		# (i.e. cannot be searched for).
		prev = original 	
		prev_tag = tag 

	# the last word in pos may be part of a color, so check again
	if name: add_current_color()

	return (predicative, attributive, nouns, verbs, color_list)	


def is_object_sensitive(name, conn=None):
	"""
	Checks whether the term name is of the form X-colo[u]r[ed]; returns a tuple of the form 
	(X-color[ed], True) if it is and (name, False) if it is not.
	"""
	for suffix in ['-colored', '-color']:
		if name[-len(suffix):] == suffix:
			# Add the new color (in its entirety) to database (along with variations).
			colors_to_add = [(name, mod, "NULL", "elaborate", "object-sensitive", False) for mod in [""] + modifiers]
			# connection may be left out
			if conn:
				storage.add_colors(colors_to_add, conn)

			return (name, True)
	
	return (name, False)


def extends_color(name, color_list, conn=None):
	"""
	Checks whether the term name is of the form color-X or X-color; returns a tuple of the form 
	(color, True) if it is and (name, False) if it is not.
	"""
	new_name = ""
	is_abstract = None

	# you're automatically going in order from smallest to largest
	for match in re.finditer(r'-', name):
		dash_index = match.start(0)

		after_dash = name[(dash_index+1):]
		before_dash = name[:dash_index]
		# checks for colors of the form X-color_name (e.g. milky-white) and add these colors as new colors
		if name[(dash_index+1):] in color_list:
			# colors like pinkish-blue are abstract (b/c pinkish is abstract) while milky-white is object-sensitive
			kind = "abstract" if color_list.get(before_dash) and color_list[before_dash]['abstract'] else "object-sensitive"
			# color is the full color; base color is what comes after the hyphen
			colors_to_add = [(name, mod, after_dash, "elaborate", kind, False) for mod in [""] + modifiers]
			# Add the new color (in its entirety) to database (along with variations).
			if conn:
				storage.add_colors(colors_to_add, conn)

			new_name = name
			is_abstract = (kind == "abstract")

		# also check for the largest color name that matches color_name-X (e.g. pink-flowering)
		elif name[:dash_index] in color_list:
			new_name = name[:dash_index]
			is_abstract = color_list[new_name]['abstract']
	
	return (name if not new_name else new_name, new_name != "", is_abstract)


def extract_clauses(t):
	"""
	Extract and return the independent and dependent clauses from the parse tree.
	"""
	dep_clauses, indep_clauses = [], []
	extract = False 						# whether the top level node is a clause (i.e. to be extracted)
	new_SBAR_branch = False					# whether a new dependent clause has to be extracted
	
	"""
	In cases where the top-level subordinate clause (SBAR) actually contains two dependent clauses, the 
	conjunction and second dependent clause are extracted separately. 
	e.g. "Even though the sky was red, and my heart was blue..."  -> ["Even though the sky was red," , 
	"and my heart was blue", ...]
	"""
	# indices of subtrees that are to be extracted (because they are clauses)
	to_remove = []

	# don't treat questions (e.g. Is anyone going to the store?, Which is the tallest mountain?) differently
	# treat inverted delcarative sentence (e.g. 'Had he been quicker...') as dep. clause (SINV -> SBAR)
	if t.label() in ['SINV', 'SBARQ']: t.set_label('SBAR')
	if t.label() in ['SQ', 'X'] : t.set_label('S')

	# Clauses composed solely of conjunctions, independent clauses, and punctuation don't need to be extracted, since after
	# extracting inner tags, they will be virtually empty. This is done by changing the label from 'S' to 'SX'.
	if t.label() == 'S' and all(isinstance(t[i], Tree) and (t[i].label() in (punc_tags + ['CC', 'S'])) for i in range(len(t))):
		t.set_label('SX')

	# Edge cases: if clause has one child, and that child is a VP, then the clause is effectively a SBAR
	if t.label() == 'S' and all(isinstance(t[i], Tree) and (t[i].label() in (punc_tags + ['VP'])) for i in range(len(t))):
		t.set_label('SBAR')

	# Edge cases: treat gerund verb phrase as subordinate
	if t.label() == 'VP' and t[0].label() == 'VBG':
		t.set_label('SBAR')

	# special case: where you have a sequence of clauses (i.e. (S (S (S ...)))), where each clause is the only
	# clause child of its parent, do not treat them as distinct - only the top-most clause is still considered
	# a clause (i.e. (S (SX (SX ...))))
	if t.label() == 'S':
		child = t 

		while child:
			children = filter(lambda i: isinstance(child[i], Tree) and (child[i].label() not in punc_tags), range(len(child)))

			if len(children) == 1:
				i = children[0]

				if child[i].label() == 'S':
					child[i].set_label('SX')

				child = child[i]
			else:
				child = None

	# The tree is parsed recursively, bottom-up: outer clause may contain 1+ inner clauses, without which the 
	# outer clause is not a clause. e.g. given (S (S CC S) ...), we do not care about the outer S
	for i in range(len(t)):
		if isinstance(t[i], Tree):
			"""
			For the first clause under any higher-level SBAR, we do not want it to be extracted as an 
			independent clause, so we label it as 'S-IN-SBAR'. Subsequent clauses under the same SBAR 
			become new SBARs, so that there's a 1-1 association between SBARs and clauses.
			"""
			if (t.label() == 'SBAR' or t.label() == 'S-IN-SBAR') and t[i].label() == 'S': 
				# if there is some clause already under t
				if new_SBAR_branch:			
					t[i].set_label('SBAR')
				# t[i] is the first clause under t 
				else: 
					t[i].set_label('S-IN-SBAR')
					new_SBAR_branch = True

			# if there is a subordinate clause precededed by a conjunction, remove that conjunction 
			if (t[i].label() == 'SBAR') and (i > 0) and (t[i-1].label() == 'CC'):
				to_remove.append(i-1)

			# Add the extracted clauses from each subtree.
			(dlst, ilst, prune) = extract_clauses(t[i])
			dep_clauses.extend(dlst)
			indep_clauses.extend(ilst)

			# Prune the subtree if necessary (if it has been extracted).
			if prune: to_remove.append(i)

	# Clauses composed solely of conjunctions, independent clauses, and punctuation don't need to be extracted, since after
	# extracting inner tags, they will be virtually empty. This is done by changing the label from 'S' to 'SX'.
	if t.label() == 'S' and all(isinstance(t[i], Tree) and (t[i].label() in (punc_tags + ['CC', 'S'])) for i in range(len(t))):
		t.set_label('SX')

	# Edge cases: if clause has one child, and that child is a VP, then the clause is effectively a SBAR
	if t.label() == 'S' and all(isinstance(t[i], Tree) and (t[i].label() in (punc_tags + ['VP'])) for i in range(len(t))):
		t.set_label('SBAR')

	# Edge cases: treat gerund verb phrase as subordinate
	if t.label() == 'VP' and t[0].label() == 'VBG':
		t.set_label('SBAR')

	# Prune the tree.
	for i in to_remove: 
		i = i - to_remove.index(i) 	# removing subtrees causes the indices of the later ones fall as well
		t.remove(t[i])

	# Remove any subtree consisting solely of punctuation, conjunctions, and propositions
	if all(isinstance(t[i], Tree) and (t[i].label() in (punc_tags + ['CC', 'IN'])) for i in range(len(t))):
		extract = True
	else:
		if t.label() == 'SBAR':
			dep_clauses.append(t)
			extract = True
		
		if t.label() == 'S':
			indep_clauses.append(t)
			extract = True

	return (dep_clauses, indep_clauses, extract)


	
