res = []
count = i
with open('../extended_colors.csv', 'r') as f:
    for row in f:
        row = row.split(',')
        res.append(row[0])
    return res
