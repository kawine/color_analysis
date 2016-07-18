import sqlite3

def get_empty_col():
    res_file = open('empty_cols.txt', 'w+')
    query = """SELECT distinct * FROM color
    WHERE base is 'NULL'
    OR modifier is 'NULL'
    OR name is 'NULL'
    OR complexity is 'NULL'
    OR kind is 'NULL'
    OR object is 'NULL';"""

    res = c.execute(query)

    for row in res:
        res_file.write(str(row))
        res_file.write('\n')

    res_file.close()
    

if __name__ == '__main__':

    conn = sqlite3.connect('../color_analysis_merged.db')
    c = conn.cursor()

    get_empty_col()

    
