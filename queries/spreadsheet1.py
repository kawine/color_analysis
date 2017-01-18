import sqlite3
from scipy import stats
conn = sqlite3.connect('../color_analysis_merged.db')
c = conn.cursor()

def total_occurence_per_color():
##    query = """SELECT color.name, count(*) FROM color, mention, sentence, clause, book
##    WHERE mention.color=color.id AND mention.clause=clause.id
##    AND clause.sentence=sentence.id AND sentence.book=book.id AND
##    book.id and color.name IN """ + color_list + """ GROUP BY color.name"""

    query = """SELECT color.name, count(*) FROM color, mention, sentence, clause, book
    WHERE mention.color=color.id AND mention.clause=clause.id
    AND clause.sentence=sentence.id AND sentence.book=book.id AND
    book.id and color.name GROUP BY color.name"""

    c.execute(query)

    for row in c.fetchall():
        print(row)

def parse_color_list():
    res = []
    with open('../query_results/colors_appearing_at_most10.txt', 'r') as f:
        for row in f:
            row = row.strip('\n')
            res.append(row) 

    f.close()
    return res

def stringify_color_list(color_list):
    res = "("
    for color in color_list:
        res = res + "'" + color + "'" + ","

    res = res[0:len(res) - 1] + ")"

    return res

def number_of_sentences_in_corpus():
    query = """SELECT count(*) FROM sentence"""

    c.execute(query)

    return c.fetchone()

def occurence_of_color_in_length(length_dist):
    res = {}

    for length in length_dist:
        
        query = """SELECT color.name, count(*) FROM color, mention, sentence, clause, book
        WHERE mention.color=color.id AND mention.clause=clause.id
        AND clause.sentence=sentence.id AND sentence.book=book.id AND
        book.id and color.name GROUP BY color.name AND sentence.length >= """ + str(length[0]) + """ AND sentence.length <= """ + str(length[1])
        
        c.execute(query)

        res[length] = c.fetchall()

    return res

def occurence_sentences_of_length(length_dist):
    res = {}
    
    for length in length_dist:
        query = """SELECT count(*) FROM sentence WHERE sentence.length >= """ + str(length[0]) + """ AND sentence.length <= """ + str(length[1])

        c.execute(query)

        res[length] = c.fetchone()[0]

    return res
       

co = parse_color_list()
##string_list = stringify_color_list(color_list)
to = total_occurence_per_color()

# considering sentence lengths of 0-5, 6-15, etc. 
length_dist = [(0, 5), (6, 15), (16, 25), (26, 35), (36, 45), (45, 65), (66, 85), (85, 10000)]

# number of sentences in corpus
num_sentences = number_of_sentences_in_corpus()

# get total occurrence of sentences for various lengths
occurences_sentences_in_length_dist = occurence_sentences_of_length(length_dist)






    

