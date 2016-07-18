import sqlite3

# query: query to execute
# options: optional arguments to query
# c: connection
# filename: optional filename if want to save output to file
def query(query, options, c, filename):
    if options:
        res = c.execute(query, options);
    else:
        res = c.execute(query);

    if filename:
        res_file = open(filename, 'w+');
        for row in res:
            res_file.write(str(row))
            res_file.write('\n')
        res_file.close()

    return res


def parse_color_list():
    res = []
    with open('../extended_colors.csv', 'r') as f:
        for row in f:
            row = row.split(',')
            res.append(row[0])
    return res

def filter_noncolors(c):
    f = open('deleted.txt', 'w+');
    all_colors = query("""SELECT name, id FROM color WHERE modifier=''""", '', c, '')
    all_colors = c.fetchall()

    manually_set_colors = parse_color_list()[1:]

    for row in all_colors:
       
        is_manually_set = row[0] in manually_set_colors
        split = row[0].split('-')
        x_colored = False
        x_y = False
        if (len(split) == 2):
            x_colored = split[0] in manually_set_colors and (split[1] == 'color' or split[1] == 'colored') 
            x_y = split[0] in manually_set_colors and split[1] in manually_set_colors
        
        if not(is_manually_set or x_colored or x_y):
            f.write(str(row) + '\n')
##            query("""DELETE FROM color WHERE id=?""", [row[1]], c, '')


    f.close()
       
    
def remove_modifier(c):
    to_remove = query(
    """SELECT distinct name, id FROM color
    WHERE name LIKE 'bright %'
    OR name LIKE 'dark %'
    OR name LIKE 'light %'
    OR name LIKE 'pastel %'
    OR name LIKE 'pale %'
    OR name LIKE 'deep %'
    OR name LIKE 'pure %'
    """, '', c, '')

    to_remove = c.fetchall()

    for row in to_remove:
        new_name = row[0][row[0].find(' ') + 1:]
        query("""UPDATE color SET name=? WHERE id=?""", [new_name, row[1]], c, '')


if __name__ == '__main__':

    conn = sqlite3.connect('../color_analysis_merged.db')
    c = conn.cursor()

 #   remove_modifier(c)
    delete_noncolors(c)

    # uncomment to save DB updates
    # conn.commit()
    


    

    
