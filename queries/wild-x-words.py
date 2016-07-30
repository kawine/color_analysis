import sqlite3

f = open('sentences-with-wild-x.txt', 'w+')

conn = sqlite3.connect('../color_analysis_merged.db')
c = conn.cursor()

#c.execute("SELECT id FROM color WHERE name LIKE 'wild-cherry'")

for row in c.execute("""SELECT text FROM sentence WHERE id IN
                     (SELECT sentence FROM clause WHERE id IN
                     (SELECT clause FROM mention WHERE color IN
                     (SELECT id FROM color WHERE name IN
                     ("hair-colored"))))"""):
    print(str(row))
     
    f.write(row[0] + '\n\n')


f.close()
