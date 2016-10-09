import sqlite3
import math
import numpy
import matplotlib.pyplot as plt

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

book_ids = [3759, 3694,5727, 4032, 4637, 2743, 5866, 1032, 5155, 2410]
book_ids_to_names = {}
# stores all color mentions for each book with id in book_ids
# format key: book id, value: (color name, color base, index of mention, hex)
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
    hex_codes[color[0]] = color[2].strip('\n').upper()

# get sentence lengths
for id in book_ids:
    sentences[id] = {}
    mentions[id] = []
    c.execute("""SELECT index_in_book, length FROM sentence where book=?""", [id])
    for row in c.fetchall():
 #       print(str(row[0]) + " " + str(row[1])
        sentences[id][row[0]] = row[1]

    book_lengths[id] = sum(sentences[id])


# index of last word before sentence containing mention
def get_index_mention(book, sentence):
##    result = 0
##    for i in range(sentence - 1):
##        result = result + sentences[book][i]
##    print(result)
    result = 0
    return result

# populate mentions dict
query = """SELECT sentence.index_in_book, color.name, color.base, book.id, mention.index_in_sent, book.title
FROM color, mention, sentence, clause, book WHERE mention.color=color.id AND
mention.clause=clause.id AND clause.sentence=sentence.id AND sentence.book=book.id AND
book.id IN (3759, 3694,5727, 4032, 4637, 2743, 5866, 1032, 5155, 2410)"""
c.execute(query)
for row in c.fetchall():
    sentence_index = row[0]
    mention_index = row[4] # in sentence
    color_name = row[1]
    color_base = row[2]
    book_id = row[3]
    title = row[5]

    mention_index_in_book = get_index_mention(book_id, sentence_index)
    book_ids_to_names[book_id] = title

    if (color_base != 'NULL'):
        mentions[book_id].append((color_name, color_base,
                              mention_index_in_book + mention_index, hex_codes[color_name]))
    

def create_mat(len1, len2):
    mat = []
    for i in range(len1):
        mat.append([0 for x in range(len2)])
    return mat

# dynamic time warping
def d(a, b):    
    return abs(a[2] - b[2]) * abs(int(a[3], 16) - int(b[3], 16))    

def dtw_distance(s, t):
    DTW = create_mat(len(s), len(t))
    for i in range(len(s)):
        #print(i)
        DTW[i][0] = math.inf
    for i in range(len(t)):
        DTW[0][i] = math.inf

    DTW[0][0] = 0

    for i in range(len(s)):
        for j in range(len(t)):
            try:
                int(s[i][3], 16)
                int(t[j][3], 16)
            except:
                print(t[j])

            
            cost = d(s[i], t[j])
            DTW[i][j] = cost + min(min(DTW[i-1][j], DTW[i][j-1]), DTW[i - 1][j -1])

    return DTW[len(s) - 1][len(t) - 1]


matrix = create_mat(len(mentions) + 1 , len(mentions) + 1)

for i in range(len(mentions)):
    matrix[i + 1][0] = book_ids_to_names[book_ids[i]]
    matrix[0][i + 1] = book_ids_to_names[book_ids[i]]

i = 1
j = 1
for book in book_ids:
    for book2 in book_ids:
        matrix[i][j] = dtw_distance(mentions[book], mentions[book2])
        j += 1
    i += 1
    j = 1


options = []



##
##
##
##for row in c.execute(query, options):
##    print(str(row))
