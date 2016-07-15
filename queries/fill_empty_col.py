import sqlite3

def get_empty_col():
    query = """SELECT * FROM color
    WHERE base is NULL
    OR name is NULL
    OR complexity is NULL
    OR kind is NULL
    OR object is NULL;"""

    res = c.execute(query)

    for row in res:
        print(row)
    
    

def fill_empty_col(c):
    return 0
    


if __name__ == '__main__':

    conn = sqlite3.connect('../color_analysis_merged.db')
    c = conn.cursor()

    get_empty_col()

    
