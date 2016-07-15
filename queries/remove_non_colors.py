import sqlite3

def get_noncolors(c):
##    res_file = open('result2.txt', 'w+');
    query = """SELECT distinct c1.name
    FROM color as c1 INNER JOIN color as c2
    ON LENGTH(c1.name) > LENGTH(c2.name) AND c1.name LIKE '%' || c2.name || '%';"""

    res = c.execute(query);

##    for row in res:
##        res_file.write(str(row))
##        res_file.write('\n')
##    res_file.close()
    return res;
    

def delete_noncolors(c, non_color_id):
    non_color_id = list(non_color_id)
    query = 'DELETE FROM color WHERE name LIKE ?;'
    c.executemany(query, non_color_id)


if __name__ == '__main__':

    conn = sqlite3.connect('../color_analysis_merged.db')
    c = conn.cursor()

    get_noncolors(c)

    
