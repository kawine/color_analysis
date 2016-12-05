import sqlite3
conn = sqlite3.connect('../color_analysis_merged.db')
c = conn.cursor()

# get list of colors
def parse_color_list():
    res = []
    with open('../color_list.csv', 'r') as f:
        for row in f:
            row = row.split(',')
            res.append(row[0])
    return res

# color count in entire corpus
# to discount the first two decades, just
# modify the query
def color_count(color_list):
    res = {}
##    query = """
##    SELECT color.name, color.id, color.base, count(*)
##    FROM color, mention
##    WHERE color.id == mention.color
##    GROUP BY color.name, color.id, color.base
##    """

    query = """
    SELECT color.name, color.id, color.base, count(*)
    FROM color, mention, clause, sentence, book
    WHERE book.year >= 1820 and mention.color=color.id AND mention.clause=clause.id AND clause.sentence=sentence.id AND sentence.book=book.id
    GROUP BY color.name, color.id, color.base
    """


    c.execute(query)

    for row in c.fetchall():
        color_name = row[0]
        color_id = row[1]
        color_base = row[2]
        count = row[3]

        if color_base in color_list:
            res[color_name] = count

    return res

# get list of colors
color_list = parse_color_list();
# count colors
color_counts = color_count(color_list)

# distribution of counts
# ie atleast once in entire corpus, 5, ..., 100 etc. 
dist = {1:0, 5:0, 10:0, 20: 0, 30:0, 50:0, 100:0}

# calculate the distribution of counts
for color in color_counts:    
    if color_counts[color] >= 100:
        dist[100] = dist[100] + 1
        
    if color_counts[color] >= 50:
        dist[50] = dist[50] + 1
        
    if color_counts[color] >= 30:
        dist[30] = dist[30] + 1
        
    if color_counts[color] >= 20:
        dist[20] = dist[20] + 1
        
    if color_counts[color] >= 10:
        dist[10] = dist[10] + 1
        
    if color_counts[color] >= 5:
        dist[5] = dist[5] + 1
        
    dist[1] = dist[1] + 1
    




