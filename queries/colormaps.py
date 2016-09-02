import sqlite3
import math

conn = sqlite3.connect('../color_analysis_merged.db')
c = conn.cursor()

##f = open('get_hex.txt', 'w+')
##query = """SELECT distinct color.name, color.base
##FROM color, mention, sentence, clause, book WHERE mention.color=color.id AND
##mention.clause=clause.id AND clause.sentence=sentence.id AND sentence.book=book.id AND
##book.id IN (3759, 3694,5727, 4032, 4637, 2743, 5866, 1032, 5155, 2410)"""
##c.execute(query)
##for row in c.execute(query):
##    f.write(row[0] + ' ' + row[1] + '\n')
##
##f.close()

book_ids = [4032,4637]
# stores all color mentions for each book with id in book_ids
# format key: book id, value: (color name, color base, index of mention)
mentions = {}

# stores length of each book with id in book_ids
# format key: book id, value: length of book
book_lengths = {}

# stores lengths of each sentence for every book in in book_ids
# format key: book id, value: {sentence_id: length}
sentences = {}

# hex codes
hex_codes = {}
for color in open('get_hex.txt', 'r'):
    color = color.split(' ')
    print(color)
    hex_codes[color[0]] = color[2].strip('\n').upper()

print(hex_codes)


# get sentence lengths
for id in book_ids:
    sentences[id] = {}
    mentions[id] = []
    c.execute("""SELECT index_in_book, length FROM sentence where book=?""", [id])
    for row in c.fetchall():
        sentences[id][row[0]] = row[1]

    book_lengths[id] = sum(sentences[id])


# index of last word before sentence containing mention
def get_index_mention(book, sentence):
    result = 0
    for i in range(sentence - 1):
        result += sentences[book][i]
    return 0

# populate mentions dict
query = """SELECT sentence.index_in_book, color.name, color.base, book.id, mention.index_in_sent
FROM color, mention, sentence, clause, book WHERE mention.color=color.id AND
mention.clause=clause.id AND clause.sentence=sentence.id AND sentence.book=book.id AND
book.id IN (4032, 4637)"""
c.execute(query)
for row in c.fetchall():
    sentence_index = row[0]
    mention_index = row[4] # in sentence
    color_name = row[1]
    color_base = row[2]
    book_id = row[3]

    mention_index_in_book = get_index_mention(book_id, sentence_index)
    
    mentions[book_id].append((color_name, color_base,
                              mention_index_in_book + mention_index, hex_codes[color_name]))
    

# dynamic time warping
def d(a, b):
    return math.abs(a[0] - b[0]) * math.abs(a[1] - b[1])    

def dtw_distance(s, t):
    DTW = [[0 for x in s], [0 for x in t]]
    for i in range(len(s)):
        DTW[i][0] = math.inf
    for i in range(len(t)):
        DTW[0][i] = math.inf

    DTW[0][0] = 0

    for i in range(len(s)):
        for j in range(len(t)):
            cost = d(s[i], t[j])
            DTW[i][j] = cost + min(min(DTW[i-1][j], DTW[i][j-1]), DTW[i - 1][j -1])

    return DTW[len(s) - 1][len(t) - 1]


matrix = [[0 for x in mentions], [0 for x in mentions]]

for i in range(len(mentions)):
    for j in range(len(mentions)):
        matrix[i][j] = dtw_distance(mentions[i], mentions[j])


options = []



##
##
##
##for row in c.execute(query, options):
##    print(str(row))
