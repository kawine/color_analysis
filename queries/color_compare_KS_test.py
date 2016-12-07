import sqlite3
conn = sqlite3.connect('../color_analysis_merged.db')
c = conn.cursor()


# make end = None if no upper limit
def count_color_appearance_in_sentence_lengths(res, color_list, start, end):
##    if end == None:
##        query = """SELECT color.name, color.id, color.base, count(*) FROM color, mention, sentence, clause, book WHERE mention.color=color.id AND mention.clause=clause.id AND clause.sentence=sentence.id AND sentence.book=book.id AND book.id and book.year >=""" + str(start) + """ GROUP BY color.name, color.id"""
##    else:
    query = """SELECT color.name, color.id, color.base, count(*) FROM color, mention, sentence, clause, book WHERE mention.color=color.id AND mention.clause=clause.id AND clause.sentence=sentence.id AND sentence.book=book.id AND book.id and book.year >=""" + str(start) + """ AND book.year <""" + str(end) + """ GROUP BY color.name, color.id, color.base"""

    c.execute(query)

    for row in c.fetchall():
        color_name = row[0]
        color_id = row[1]
        base = row[2]
        count = row[3]

        if base in color_list:
            if color_name not in res:
                res[color_name] = {
                           '1800_1810':0,
                           '1810_1820':0,
                           '1820_1830':0,
                           '1830_1840':0,
                           '1850_1860':0,
                           '1860_1870':0,
                           '1870_1880':0,
                           '1880_1890':0,
                           '1890_1900':0
                           }
                        
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
count_color_appearance_in_sentence_lengths(res, color_list, 1800, 1810)
count_color_appearance_in_sentence_lengths(res, color_list, 1810, 1820)
count_color_appearance_in_sentence_lengths(res, color_list, 1830, 1840)
count_color_appearance_in_sentence_lengths(res, color_list, 1840, 1850)
count_color_appearance_in_sentence_lengths(res, color_list, 1850, 1860)
count_color_appearance_in_sentence_lengths(res, color_list, 1860, 1870)
count_color_appearance_in_sentence_lengths(res, color_list, 1870, 1880)
count_color_appearance_in_sentence_lengths(res, color_list, 1880, 1890)
count_color_appearance_in_sentence_lengths(res, color_list, 1890, 1900)

# write to file
f = open('../color_count_per_decade.txt', 'w');

for color in res:
    s = color

    for key, val in res[color].items():
        s = s + ',' + str(val)

    f.write(s + '\n')
    
f.close()    
    
