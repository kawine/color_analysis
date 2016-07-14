import sqlite3
import math
import matplotlib.pyplot as plt
import numpy as np

def get_freqs():
    absolute_freq_query = """SELECT name, count(*) as frequency
        FROM mention JOIN color WHERE mention.color = color.id
        GROUP BY color;"""
    summed_freq_query = 'SELECT SUM(length) FROM sentence;'

    absolute_freq = list(c.execute(absolute_freq_query))
    total_freq = c.execute(summed_freq_query).fetchone()[0]

    relative_freq = []

    for item in absolute_freq:
        relative_freq.append((item[0], float(item[1])/total_freq * 1000))
        # relative_freq.append((item[0], math.log(1/(float(item[1])/total_freq))))

    return relative_freq

def get_freqs_over_years(threshold, period):
    """
    Get a dictionary in the form
    {(color_id, color_name):
        {   periods_above_threshold: [ list of periods ],
            always_above_threshold: true/false }, ...}
    """
    absolute_freq_query = """SELECT color.id, color.name, book.year / {p} * {p}, count(*) as frequency
        FROM mention
        JOIN color ON mention.color = color.id
        JOIN clause ON mention.clause = clause.id
        JOIN sentence ON clause.sentence = sentence.id
        JOIN book ON sentence.book = book.id
        GROUP BY book.year / {p} * {p}, mention.color;""".format(p=period)

    # List of (color_id, color_name, period, abs_freq) tuples
    absolute_freq = list(c.execute(absolute_freq_query))

    # List of (period, length) tuples
    lengths_query = """SELECT book.year / {p} * {p}, SUM(sentence.length)
        FROM sentence JOIN book ON sentence.book = book.id
        GROUP BY book.year / {p} * {p};""".format(p=period)
    lengths = list(c.execute(lengths_query))

    # {Period: total length} mapping
    period_to_length = dict()
    for tup in lengths:
        period_to_length[tup[0]] = tup[1]

    # {(color_id, color_name): {'periods_above_threshold': lst, 'always_above_threshold': bool}}
    relative_freq = {}
    for item in absolute_freq:
        key = (item[0], item[1])  # (color_id, color_name) tuple
        period = item[2]
        freq_val = float(item[3])/period_to_length[period] * 10000
        if key not in relative_freq:
            relative_freq[key] = {'periods_above_threshold': [], 'always_above_threshold': True}
        if freq_val >= threshold:
            relative_freq[key]['periods_above_threshold'].append(period)
        else:
            relative_freq[key]['always_above_threshold'] = False

    return relative_freq

def show(data, period):

    plt.bar(np.arange(len(data)), [x[1] for x in data], align='center', alpha=0.5)
    plt.xticks(np.arange(len(data)), [x[0] for x in data], rotation='vertical', fontsize=5)
    plt.ylabel('Usage')
    plt.title('Relative frequencies for ' + period)


    plt.show()



if __name__ == '__main__':

    conn = sqlite3.connect('../color_analysis_merged.db')
    c = conn.cursor()

    print get_freqs_over_years(3, 5)

    # relative_freq = get_freqs()
    # show(relative_freq, '1990-1995')

##datestamp, value = np.loadtxt(graphArray,delimiter=',', unpack=True,
##                              converters={ 0: mdates.strpdate2num(' %Y-%m-%d %H:%M:%S')})
##
##fig = plt.figure()
##
##rect = fig.patch
##
##ax1 = fig.add_subplot(1,1,1, axisbg='white')
##plt.plot_date(x=datestamp, y=value, fmt='b-', label = 'value', linewidth=2)
##plt.show()
