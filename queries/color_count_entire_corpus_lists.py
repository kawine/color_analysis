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
    query = """
    SELECT color.name, color.base, count(*)
    FROM color, mention
    WHERE color.id == mention.color
    GROUP BY color.name, color.base
    """

##    query = """
##    SELECT color.name, color.base, count(*)
##    FROM color, mention, clause, sentence, book
##    WHERE book.year >= 1820 and mention.color=color.id AND mention.clause=clause.id AND clause.sentence=sentence.id AND sentence.book=book.id
##    GROUP BY color.name, color.base
##    """


    c.execute(query)

    for row in c.fetchall():
        color_name = row[0]
 #       color_id = row[1]
        color_base = row[1]
        count = row[2]

        if color_base in color_list:
            res[color_name] = count

    return res

# get list of colors
color_list = parse_color_list();
# count colors
color_counts = color_count(color_list)

# distribution of counts
# ie atleast once in entire corpus, 5, ..., 100 etc. 
dist = {1:0, 2:0, 3:0, 4:0, 5:0, 10:0, 20: 0, 30:0, 50:0, 100:0}
color_names_dist = {1:[], 2:[], 3:[], 4:[], 5:[], 10:[]}


# calculate the distribution of counts
for color in color_counts:
##    if color_counts[color] >= 1:
##        color_names_dist[1].append(color)
##    if color_counts[color] >= 2:
##        color_names_dist[2].append(color)
##    if color_counts[color] >= 3:
##        color_names_dist[3].append(color)
##    if color_counts[color] >= 4:
##        color_names_dist[4].append(color)
    if color_counts[color] >= 5:
        color_names_dist[5].append(color)
    if color_counts[color] >= 10:
        color_names_dist[10].append(color)

for count in color_names_dist:
    f = open('colors_appearing_at_most' + str(count) + '.txt' ,'w');

    for color in color_names_dist[count]:
        f.write(color + '\n')
        
    f.close()




