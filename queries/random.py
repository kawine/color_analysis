import sqlite3
conn = sqlite3.connect('../color_analysis_merged.db')
c = conn.cursor()

query = """SELECT color.name, color.id, color.base, count(*) FROM color, mention, sentence, clause, book WHERE mention.color=color.id AND mention.clause=clause.id AND clause.sentence=sentence.id AND sentence.book=book.id AND book.id and book.year >=""" + str(1820) + """ AND book.year <""" + str(1840) + """ GROUP BY color.name, color.id, color.base"""

c.execute(query)

for row in c.fetchall():
    print(row)
