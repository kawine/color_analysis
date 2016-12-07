import sqlite3
conn = sqlite3.connect('../color_analysis_merged.db')
c = conn.cursor()


# make end = None if no upper limit
def count_color_appearance_in_sentence_lengths(res, color_list, start, end):
    if end == None:
        query = """SELECT color.name, color.id, color.base, count(*) FROM color, mention, sentence, clause, book WHERE mention.color=color.id AND mention.clause=clause.id AND clause.sentence=sentence.id AND sentence.book=book.id AND book.id and sentence.length >=""" + str(start) + """ GROUP BY color.name, color.id"""
    else:
        query = """SELECT color.name, color.id, color.base, count(*) FROM color, mention, sentence, clause, book WHERE mention.color=color.id AND mention.clause=clause.id AND clause.sentence=sentence.id AND sentence.book=book.id AND book.id and sentence.length >=""" + str(start) + """ AND sentence.length <""" + str(end) + """ GROUP BY color.name, color.id"""

    c.execute(query)

    for row in c.fetchall():
        color_name = row[0]
        color_id = row[1]
        base = row[2]
        count = row[3]

        if base in color_list:
            if color_name not in res:
                res[color_name] = {'0_5':0,
                           '5_15':0,
                           '15_25':0,
                           '25_35':0,
                           '35-45':0,
                           '65-85':0,
                           '85':0}
                        
            res[color_name][str(start) + '_' + str(end)] = count

            
# get list of valid base colors
def parse_color_list():
    res = []
    with open('../color_list.csv', 'r') as f:
        for row in f:
            row = row.split(',')
            res.append(row[0]) 

    f.close()
    return res


# build and empty result dictionary
color_list = parse_color_list();

res = {}

# get counts
count_color_appearance_in_sentence_lengths(res, color_list, 0, 5)
count_color_appearance_in_sentence_lengths(res, color_list, 5, 15)
count_color_appearance_in_sentence_lengths(res, color_list, 15, 25)
count_color_appearance_in_sentence_lengths(res, color_list, 25, 35)
count_color_appearance_in_sentence_lengths(res, color_list, 35, 45)
count_color_appearance_in_sentence_lengths(res, color_list, 45, 65)
count_color_appearance_in_sentence_lengths(res, color_list, 65, 85)
count_color_appearance_in_sentence_lengths(res, color_list, 85, None)

# write to file
f = open('../color_count_in_various_ranges_of_sentence_length.txt', 'w');

for color in res:
    s = color

    for key, val in res[color].items():
        s = s + ',' + str(val)

    f.write(s + '\n')
    
f.close()    
    


##### CHUNK1: write query results q to filename name
##def write_to_file(q, name):
##    f = open(name, 'w')
##    for row in q.fetchall():
##        color_name = row[0]
##        color_id = row[1]
##        count = row[2]
##
##        s = str(color_name) + ',' + str(color_id) + ',' + str(count)
##        f.write(s)
##        f.write('\n')
##
##
##import sqlite3
##conn = sqlite3.connect('../color_analysis_merged.db')
##c = conn.cursor()
##
##query = """
##SELECT color.name, color.id, count(*)
##FROM color, mention, sentence, clause, book
##WHERE mention.color=color.id AND
##mention.clause=clause.id AND clause.sentence=sentence.id AND sentence.book=book.id AND
##book.id and sentence.length <= 45 AND sentence.length >= 36
##GROUP BY color.name, color.id
##"""
##
##c.execute(query)
##
##write_to_file(c, '36to45.txt')
#####

### create empty result dictionary
##def parse_color_dict():
##    res = []
##    with open('../color_list.csv', 'r') as f:
##        for row in f:
##            row = row.split(',')
##            res.append(row[0])
##    return res
##
##
##
##
### get list of colors
##color_names = parse_color_list()
##
### how many times each color appears in setences of length 0-5 (key 1),
### 5-15 (key 2), all the way to over 85 words 
### {color_name:  {1:, 2:, 3:, ... } }
##result = {}
##






