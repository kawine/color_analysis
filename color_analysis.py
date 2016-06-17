from book import * 
from multiprocessing import Pool
import storage, time
from lxml import html
import pickle, sys, os
from nltk.stem import snowball

reload(sys)
sys.setdefaultencoding('UTF-8')
NUM_THREADS = 22

def get_color_list(filename):
	"""
	Get the list of colors stored in a csv file with name filename;
	return the list of all colors and a sublist of only the abstract ones.
	"""
	colors, colors_to_store = {}, []

	with open(filename, 'rb') as csvfile:
		reader = csv.reader(csvfile)
		# Skip the first line, which is a description.
		next(reader)					

		for row in reader:
			# For consistency, replace all spaces in the basename with a hyphen (e.g. bright blue -> bright-blue)
			basename = row[0].strip().lower().replace(' ', '-') # without modifiers (i.e. green will be there, not light green)
			
			base_color = row[1].strip().lower()					# e.g. yellow for gold
			complexity = row[2].strip().lower()					# either basic or elaborate
			kind = row[3].strip().lower()						# concrete, abstract, object-sensitive
			may_be_obj = kind == 'concrete'						# can it be an object?

			# key: color_name -> value : (whether color is abstract and whether it can be an obj) (important traits)
			colors[basename] = { 'abstract' : kind == "abstract", 'non_obj' : (not may_be_obj) }
			# list of colors to be inserted into SQL database
			colors_to_store.append((basename, "", base_color, complexity, kind, may_be_obj))
			# Also include all modifiers of the color (e.g. blond -> pale-blond, pastel-blond, ...)
			for modifier in ['bright', 'dark', 'light', 'pastel', 'pale', 'deep', 'pure']:
				variation = modifier + '-' + basename
				colors[variation] = { 'abstract' : kind == "abstract", 'non_obj' : (not may_be_obj) }
				colors_to_store.append((basename, modifier, base_color, complexity, kind, may_be_obj))

	return colors, colors_to_store


def word_count():
	"""
	Get the word count of each word in the corpus (to be used for calculating vocabulary richness).
	Note that this uses the results of the SENNA tagger for POS, not the Stanford Tagger.
	"""
	count = {}	# map words to counts
	stemmer = snowball.EnglishStemmer() # for stemming words so that different forms aren't counted separately
	stoplist = set("""( ) : , . { } [ ] ; . ' " ! ? @ # $ % * \ + what at "n't" if for a an on of the and to from in by or either neither so where there those these this that it which who whose but be is have should would it about into 've he she them i i. w. hi him her my me you your their our we with 't 's then than when have not""".split())

	dn = '/Volumes/Seagate Slim/litlab/tagged/'
	books = [ fn for fn in os.listdir(dn) if fn.endswith('_tagged.txt') ]

	for book in books:
		print book
		with open(dn + book) as f:
			sent_count = 0

			# skip the first three sentences (which is just meta-data)
			while sent_count < 3:
				line = f.readline().strip()
				
				if not line:
					sent_count = sent_count + 1

			# each token is on a separate line
			for line in f:
				if line.strip():
					token, pos = line.split()[:2]

					parenth_replacements = { '(' : '-LRB-', ')' : '-RRB-'  }
					token = parenth_replacements.get(token, token)

					# handle edge case that you forgot to handle earlier
					if token.startswith('grey-'):
						token = 'gray-' + token[5:]

					# for colors or things that share a name with a color
					is_color = token.startswith("__COLOR__") and token.endswith("__COLOR__")
					tokens = (token[9:-9] if is_color else token).split("_")

					for t in tokens:
						t = stemmer.stem(t.lower())		# lowercase and stem words for normalization
						if t not in stoplist:	# exclude proper nouns, common words, and punctuation
							if t not in count:
								count[t] = 1
							else:
								count[t] = count[t] + 1

	pickle.dump(count, open('word_count', 'w'))


(color_list, to_store) = get_color_list("extended_colors.csv")


def tokenize_books(indices):
	for i in indices:
		replace_book_colors("/Volumes/Seagate Slim/litlab/formatted/" + str(i) + "_formatted.txt", color_list)


def test_run():
	color_list, to_store = get_color_list('extended_colors.csv')
	conn = storage.new_connection('sample')
	storage.create_tables(conn)
	storage.add_colors(to_store, conn)
	conn.close()
	parse_book('test_sentences_tagged.txt', color_list, 'sample')


def build_database((database_index, fns)):
	print "Building database ", database_index
	color_list, to_store = get_color_list('extended_colors.csv')
	conn = storage.new_connection(database_index)
	storage.create_tables(conn)
	storage.add_colors(to_store, conn)
	conn.close()

	storage.seed_autoincrement(database_index)

	for i, fn in enumerate(fns):
		print database_index, i, fn[fn.rindex('/'):], len(fns)
		parse_book(fn, color_list, database_index)
		break

	storage.unseed_autoincrement(database_index)
		

if __name__ == "__main__":
	print "Gathering files..."
	# with open('metadata.p') as f:
	# 	metadata = pickle.load(f)
	# 	dn = 'tagged/'
	# 	fns = [ dn + fn.replace('tokenized', 'tagged') for fn in metadata if (metadata[fn][2] >= 1800 and metadata[fn][2] < 1900) ]

	# pool = Pool(NUM_THREADS)
	# pool.map(build_database, [(i, fns[i::NUM_THREADS]) for i in range(NUM_THREADS)])
	build_database((1, ['/Volumes/Seagate Slim/litlab/tagged/1_tagged.txt']))
	# build_database((2, ['/Volumes/Seagate Slim/litlab/tagged/2_tagged.txt']))
	# build_database((3, ['/Volumes/Seagate Slim/litlab/tagged/3_tagged.txt']))


def merge_databases():
	merged_conn = storage.new_connection('merged')
	merged_cursor = merged_conn.cursor()
	storage.create_tables(merged_conn)
	
	# first create a comprehensive dictionary of colors
	colors = {}

	for database_index in range(NUM_THREADS):
		conn = storage.new_connection(database_index)
		cursor = conn.cursor()
		cursor.execute("""SELECT * FROM color;""")

		for ID, name, modifier, base, complexity, kind, obj in cursor.fetchall():
			colors[modifier + ' ' + name] = [name, modifier, base, complexity, kind, obj]

		conn.close()

	# insert comprehensive list of colors into database
	for color in colors:
		name, modifier, base, complexity, kind, obj = colors[color]
		merged_cursor.execute("""INSERT INTO color VALUES (NULL, '{n}', '{m}', '{b}', '{c}', '{k}', {o});""".format(n=name, m=modifier, b=base, c=complexity, k=kind, o=obj))
		colors[color] = merged_cursor.lastrowid

	merged_conn.commit()

	# insert the rest of the data into the merged table
	for i in range(NUM_THREADS):
		merged_cursor.execute("""ATTACH DATABASE 'color_analysis_{0}.db' AS 'd{1}';""".format(i, i))
		merged_cursor.execute("""INSERT INTO book SELECT * FROM d{0}.book;""".format(i))
		merged_cursor.execute("""INSERT INTO sentence SELECT * FROM d{0}.sentence;""".format(i))
		merged_cursor.execute("""INSERT INTO clause SELECT * FROM d{0}.clause;""".format(i))

		conn = storage.new_connection(i)
		cursor = conn.cursor()
		cursor.execute("""SELECT mention.id, mention.index_in_sent, mention.clause, mention.type, color.name, color.modifier FROM mention JOIN color ON mention.color = color.id;""")

		for ID, index_in_sent, clause, typ, name, modifier in cursor.fetchall():
			# use the color dictionary, which maps to the new color ids, to replace the id of the referenced color
			#print """INSERT INTO mention VALUES (NULL, {iis}, {cl}, {co}, {t});""".format(iis=index_in_sent, cl=clause, co=colors[modifier + ' ' + name], t=typ)
			merged_cursor.execute("""INSERT INTO mention VALUES ({id}, {iis}, {cl}, {co}, '{t}');""".format(id=ID, iis=index_in_sent, cl=clause, co=colors[modifier + ' ' + name], t=typ))

		conn.close()
		merged_conn.commit()

	merged_conn.close()


		

