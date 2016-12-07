import sqlite3
conn = sqlite3.connect('../color_analysis_merged.db')
c = conn.cursor()

##
### make end = None if no upper limit
##def count_color_appearance_in_sentence_lengths(res, color_list, start, end):
##    if end == None:
##        query = """SELECT color.name, color.id, color.base, count(*) FROM color, mention, sentence, clause, book WHERE mention.color=color.id AND mention.clause=clause.id AND clause.sentence=sentence.id AND sentence.book=book.id AND book.id and sentence.length >=""" + str(start) + """ GROUP BY color.name, color.id"""
##    else:
##        query = """SELECT color.name, color.id, color.base, count(*) FROM color, mention, sentence, clause, book WHERE mention.color=color.id AND mention.clause=clause.id AND clause.sentence=sentence.id AND sentence.book=book.id AND book.id and sentence.length >=""" + str(start) + """ AND sentence.length <""" + str(end) + """ GROUP BY color.name, color.id"""
##
##    c.execute(query)
##
##    for row in c.fetchall():
##        color_name = row[0]
##        color_id = row[1]
##        base = row[2]
##        count = row[3]
##
##        if base in color_list:
##            if color_name not in res:
##                res[color_name] = {'0_5':0,
##                           '5_15':0,
##                           '15_25':0,
##                           '25_35':0,
##                           '35-45':0,
##                           '65-85':0,
##                           '85':0}
##                        
##            res[color_name][str(start) + '_' + str(end)] = count
##
##            
### get list of valid base colors
##def parse_color_list():
##    res = []
##    with open('../color_list.csv', 'r') as f:
##        for row in f:
##            row = row.split(',')
##            res.append(row[0]) 
##
##    f.close()
##    return res
##
##
### build and empty result dictionary
##color_list = parse_color_list();
##
##res = {}
##
### get counts
##count_color_appearance_in_sentence_lengths(res, color_list, 5000)
##
### write to file
##f = open('../color_count_in_various_ranges_of_sentence_length.txt', 'w');
##
##for color in res:
##    s = color
##
##    for key, val in res[color].items():
##        s = s + ',' + str(val)
##
##    f.write(s + '\n')
##    
##f.close()    
##    
