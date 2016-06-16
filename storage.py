# COLOR ( id, name, modifier, base, complexity, could be object
# SENTENCE ( book_id, index_in_book, length, height, periodicity, num_dep, num_indep, vocab_richness)
# MENTION ( sentence_id, clause_id, color_id, attributive )
# CLAUSE ( id, dependent, length, height)

import sqlite3

def new_connection(database_index):
	return sqlite3.connect('color_analysis_{0}.db'.format(database_index))

def create_tables(conn):
	"""
	Create all the tables in the database, namely one for books, sentences,
	clauses, colors, and mentions of color.
	"""
	cursor = conn.cursor()
	# Enable foreign key constraints.
	cursor.execute("""PRAGMA foreign_keys = 1""")

	# Order here is important (begin with that which refers to others).
	for table in ['mention', 'clause', 'color', 'sentence', 'book']:
		cursor.execute("DROP TABLE IF EXISTS " + table + ";")

	modifiers = ["'bright'", "'dark'", "'light'", "'pastel'", "'pale'", "'deep'", "'pure'", "''"]
	mod_constraints = ("modifier LIKE " + mod for mod in modifiers)

	complexities = ["'elaborate'", "'basic'"]
	complex_constraints = ("complexity LIKE " + com for com in complexities)

	kinds = ["'object-sensitive'", "'abstract'", "'concrete'"]
	kind_constraints = ("kind LIKE " + k for k in kinds)

	type_constraints = ("type LIKE " + t for t in ["'attr'", "'pred'", "'noun'", "'verb'"])

	dep_states = ("dependency_state LIKE " + s for s in ["'ind'", "'dep'", "'fra'"])

	# For the color table, each modifier-name (e.g. "bright-red") combo must be unique.
	cursor.execute("""
	CREATE TABLE color ( 
	id INTEGER PRIMARY KEY,	
	name VARCHAR(20),
	modifier VARCHAR(6) CHECK(""" + " OR ".join(list(mod_constraints)) + """), 
	base VARCHAR(10), 
	complexity VARCHAR(10) CHECK(""" + " OR ".join(list(complex_constraints)) + """), 
	kind VARCHAR(20) CHECK(""" + " OR ".join(list(kind_constraints)) + """), 
	object BOOLEAN,
	UNIQUE(name, modifier));""")

	cursor.execute("""
	CREATE TABLE book ( 
	id INTEGER PRIMARY KEY AUTOINCREMENT,	
	title VARCHAR(255),
	author VARCHAR(255),
	year INTEGER);""")

	cursor.execute("""
	CREATE TABLE sentence ( 
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	text VARCHAR(1500),
	book INTEGER REFERENCES book(id),
	index_in_book INTEGER,
	length INTEGER,
	height INTEGER, 
	periodicity INTEGER,
	num_dep INTEGER,
	num_indep INTEGER,
	vocab_richness FLOAT,
 	S INTEGER, 
	SBAR INTEGER,
	SBARQ INTEGER,
	SINV INTEGER,
	SQ INTEGER,
	ADJP INTEGER,
	ADVP INTEGER,
	CONJP INTEGER,
	FRAG INTEGER,
	INTJ INTEGER,
	LST INTEGER,
	NAC INTEGER,
	NP INTEGER,
	NX INTEGER,
	PP INTEGER,
	PRN INTEGER,
	PRT INTEGER,
	QP INTEGER,
	RRC INTEGER,
	UCP INTEGER,
	VP INTEGER,
	WHADJP INTEGER,
	WHAVP INTEGER,
	WHNP INTEGER,
	WHPP INTEGER,
	X INTEGER,
	CC INTEGER,
	CD INTEGER,
	DT INTEGER,
	EX INTEGER,
	FW INTEGER,
	PREPOSITION INTEGER,
	JJ INTEGER,
	JJR INTEGER,
	JJS INTEGER,
	LS INTEGER,
	MD INTEGER,
	NN INTEGER,
	NNS INTEGER,
	NNP INTEGER,
	NNPS INTEGER,
	PDT INTEGER,
	POS INTEGER,
	PRP INTEGER,
	PRP$ INTEGER,
	RB INTEGER,
	RBR INTEGER,
	RBS INTEGER,
	RP INTEGER,
	SYM INTEGER,
	UH INTEGER,
	VB INTEGER,
	VBD INTEGER,
	VBG INTEGER,
	VBN INTEGER,
	VBP INTEGER,
	VBZ INTEGER,
	WDT INTEGER,
	WP INTEGER,
	WP$ INTEGER,
	WRB INTEGER);""")

	cursor.execute("""
	CREATE TABLE clause ( 
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	sentence INTEGER REFERENCES sentence(id),	
	dependency_state VARCHAR(3) CHECK(""" + " OR ".join(list(dep_states)) + """), 
	length INTEGER,
	height INTEGER);""")

	cursor.execute("""
	CREATE TABLE mention ( 
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	index_in_sent INTEGER,
	clause INTEGER REFERENCES clause(id),
	color INTEGER REFERENCES color(id),
	type VARCHAR(4) CHECK(""" + " OR ".join(list(type_constraints)) + """));""")

	# Save changes.
	conn.commit()


def add_colors(colors, conn):
	"""
	Given specifications for a color, add it to the table of colors. Assume that any 
	modifiers (e.g. 'bright') are included.
	"""
	cursor = conn.cursor()
	for name, modifier, base, complexity, kind, obj in colors:
		try: 
			(name, modifier, base, complexity, kind) = esc_quotes([name, modifier, base, complexity, kind])
			obj = '1' if obj else '0' 
			command = """INSERT INTO color VALUES (NULL, '{n}', '{m}', '{b}', '{c}', '{k}', {o});"""
			cursor.execute(command.format(n=name, m=modifier, b=base, c=complexity, k=kind, o=obj))
		except sqlite3.IntegrityError:
			print "{0} {1} is already in the database".format(modifier, name)

	conn.commit()


def add_book(title, author, year, conn): 
	"""
	Given specifications for a book, insert it into the database.
	"""
	(title, author) = esc_quotes([title, author])
	cursor = conn.cursor()
	command = """INSERT INTO book VALUES (NULL, '{t}', '{a}', {y});"""
	cursor.execute(command.format(t=title, a=author, y=year))
	conn.commit()
	return cursor.lastrowid


def add_sentence(text, book, index, length, height, periodicity, num_dep, num_indep, vocab_richness, counts, conn):
	"""
	Insert a given sentence (and statistics about it) into the database.
	"""
	cursor = conn.cursor()
	command = """INSERT INTO sentence VALUES (NULL, '{t}', {b}, {i}, {l}, {h}, {p}, {nd}, {ni}, {vr}, {c});"""
	cursor.execute(command.format(t=(esc_quotes([text])[0]), b=book, i=index, l=length, h=height, p=periodicity, 
		nd=num_dep, ni=num_indep, vr=vocab_richness, c=', '.join([str(count) for count in counts])))
	conn.commit()
	return cursor.lastrowid


def add_clause(sentence, dependency_state, length, height, conn):
	"""
	Insert a given clause (and statistics about it) into the database.
	"""
	dependency_state = esc_quotes([dependency_state])[0]
	cursor = conn.cursor()
	command = """INSERT INTO clause VALUES (NULL, {s}, '{d}', {l}, {h});"""
	cursor.execute(command.format(s=sentence, d=dependency_state.lower(), l=length, h=height))
	conn.commit()
	return cursor.lastrowid


def add_mentions(clause, predicative, attributive, nouns, verbs, conn):
	"""
	Given a list of colors that arem predicative, attributive, nouns, and verbs, and which all
	belong to a particular clause, insert them one by one into the database. 
	"""
	cursor = conn.cursor()
	categories = { 'pred': predicative, 'attr': attributive, 'noun' : nouns, 'verb' : verbs }

	for abbr in categories:
		for color, index in categories[abbr]:
			command = """INSERT INTO mention VALUES (NULL, {i}, {cl}, {co}, '{t}');"""
			cursor.execute(command.format(i=index, cl=clause, co=get_color_id(color, cursor), t=abbr))
	
	conn.commit()


def get_color_id(color, cursor):
	"""
	Given a color (with modifier attached, e.g. bright-moss-green), find its ID in the database
	and return it. Raise exception if not found.
	"""
	for mod in ['bright-', 'dark-', 'light-', 'pastel-', 'pale-', 'deep-', 'pure-', ""]:
		if color.startswith(mod):
			command = """SELECT id FROM color WHERE modifier LIKE '{m}' AND name LIKE '{n}';"""
			# Separate colors into the modifier and base name when searching the table.
			cursor.execute(command.format(m=(mod[:-1] if mod else mod), n=color[len(mod):]))
			result = cursor.fetchone()

			if result is not None:
				return result[0]

	raise Exception(color + " not found in database")


def esc_quotes(strs):
	"""
	Given a list of strings, escape the single quotes (which will otherwise cause an error during
	insertion).
	"""
	for i in range(len(strs)):
		strs[i] = strs[i].replace("'", "''")

	return strs


def seed_autoincrement(database_index):
	"""
	Make sure rows in parallel databases don't have overlapping IDS (important for merging).
	160 is the amount of books per thread. 25000 is the upper bound on sentences per bood. 10 is the upper bound on clauses per sentence.
	unlikely for there to be more than one mention per clause.
	"""
	conn = new_connection(database_index)
	cursor = conn.cursor()
	cursor.execute("""INSERT INTO book VALUES ({id}, NULL, NULL, NULL);""".format(id=(database_index * 160 + 1)))
	cursor.execute("""INSERT INTO sentence VALUES ({id}, {rest});""".format(id=(database_index * 160 * 25000 + 1), rest=(', '.join(['NULL' for i in range(70)]))))
	cursor.execute("""INSERT INTO clause VALUES ({id}, NULL, NULL, NULL, NULL);""".format(id=(database_index * 160 * 25000 * 10 + 1)))
	cursor.execute("""INSERT INTO mention VALUES ({id}, NULL, NULL, NULL, NULL);""".format(id=(database_index * 160 * 25000 * 10 + 1)))
	conn.commit()


def unseed_autoincrement(database_index):
	"""
	Remove the rows that were used for seeding.
	"""
	conn = new_connection(database_index)
	cursor = conn.cursor()
	cursor.execute("""DELETE FROM mention WHERE id = {0};""".format(database_index * 160 * 25000 * 10 + 1))
	cursor.execute("""DELETE FROM clause WHERE id = {0};""".format(database_index * 160 * 25000 * 10 + 1))
	cursor.execute("""DELETE FROM sentence WHERE id = {0};""".format(database_index * 160 * 25000 + 1))
	cursor.execute("""DELETE FROM book WHERE id = {0};""".format(database_index * 160 + 1))
	conn.commit()







