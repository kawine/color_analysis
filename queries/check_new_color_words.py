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
    f = open('filtered.txt', 'w+');
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
            f.write(str(row[1]) + ',' + str(row[0]) + ',,'  + '\n')
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

def remove_n_words(c, filename):

    with open(filename, 'r') as f:
        for row in f:
            row = row.split(',')
            if (row[2] == 'n' and row[3] == '' and row[4] == ''):
                c.execute("""DELETE FROM color WHERE name like ?""", [row[1]]); 
                    

    r = open('non_n_words.txt', 'w+')
    for row in c.execute("SELECT distinct name FROM color"):
        r.write(row[0] + '\n')
    r.close()


def fix_typos(c, filename, color_list):
    with open(filename, 'r') as f:
        for row in f:
            row = row.split(',')
            if ((row[2] == 'n' or row[2] == 'c') and row[3] != ''):
                c.execute("""SELECT * FROM color WHERE name=?""", [row[3]]); 
                if not list(c.fetchall()):
                    c.execute("""UPDATE color SET name=? WHERE name like ?""", [row[3], row[1]])
                else:
                    for row2 in c.execute("""SELECT mention.id, modifier FROM mention, color WHERE mention.color=color.id AND color.id IN (SELECT id FROM color WHERE name like ?)""", [row[1]]):
                        c.execute("""SELECT name, id FROM color WHERE name like ? AND modifier like ?""", [row[3], row2[1]])
                        new_color_id = c.fetchone()
                        #print(row[1] + " " + new_color_id[0])
                        c.execute("""UPDATE mention SET color=? WHERE id=?""", [new_color_id[1], row2[0]])
                        c.execute("""DELETE FROM color WHERE name like ?""", [row[1]])
                    

    r = open('non_typo_words.txt', 'w+')
    for row in c.execute("SELECT distinct name FROM color"):
        r.write(row[0] + '\n')
    r.close()    

def parse_color_list(filename):
    result = [];
    
    with open(filename, 'r') as f:
        for row in f:
            row = row.split(',')
            result.append(row[0])

    return result

def get_empty_col(c):
    res_file = open('empty_cols2.txt', 'w+')
    query = """SELECT distinct name FROM color
    WHERE base is 'NULL';"""

    res = c.execute(query)

    for row in res:
        res_file.write(row[0])
        res_file.write('\n')

    res_file.close()

def add_base(c, filename):
    with open(filename, 'r') as f:
        for row in f:
            row = row.split(',')
            if row[1] != '':
                c.execute("""UPDATE color SET base=? WHERE name LIKE ?""", [row[1], row[0]])

if __name__ == '__main__':

    conn = sqlite3.connect('../color_analysis_merged.db')
    c = conn.cursor()
    
    color_list = parse_color_list('../extended_colors.csv');

 #   remove_n_words(c, '../christina.csv');
#    fix_typos(c, '../christina.csv', color_list);
#    get_empty_col()
    add_base(c, '../empty_cols2.csv')

 #   remove_modifier(c)
 #   filter_noncolors(c)

    # uncomment to save DB updates
    #conn.commit()
    


    

    
