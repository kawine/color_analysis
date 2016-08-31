import sqlite3
import math
import matplotlib.pyplot as plt
import numpy as np
import collections

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

def get_freqs_over_period(period):
    """
    Get a list of (color_id, color_name, period, absolute_freq, relative_freq) tuples
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

    # List of (color_id, color_name, period, abs_freq, rel_freq) tuples
    relative_freq = []
    for item in absolute_freq:
        rel_freq = float(item[3])/period_to_length[item[2]] * 10000
        relative_freq.append((item[0], item[1], item[2], item[3], rel_freq))

    return relative_freq

def get_frequent_colors(threshold, period):
    """
    Get a dictionary in the form
    {(color_id, color_name):
        {   periods_above_threshold: [ list of periods ],
            always_above_threshold: true/false }, ...}
    """
    absolute_freq_query = """SELECT color.id, color.name, book.year / {p} * {p}, count(*)
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
    relative_freq = collections.OrderedDict()
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

def get_colors_above_threshold(threshold, period):
    """
    Get a list of color ids that are always above the given threshold
    """
    freq_data = get_frequent_colors(threshold, period)

    above_threshold = []
    for key in freq_data:
        if freq_data[key]['always_above_threshold']:
            above_threshold.append(key[0])

    return above_threshold

def get_colors_not_above_threshold(threshold, period):
    """
    Get a list of colors ids that are not always above the given threshold
    """
    freq_data = get_frequent_colors(threshold, period)

    not_above_threshold = []
    for key in freq_data:
        if not freq_data[key]['always_above_threshold']:
            not_above_threshold.append(key[0])

    return not_above_threshold

def show(data, period):

    plt.bar(np.arange(len(data)), [x[1] for x in data], align='center', alpha=0.5)
    plt.xticks(np.arange(len(data)), [x[0] for x in data], rotation='vertical', fontsize=5)
    plt.ylabel('Usage')
    plt.title('Relative frequencies for ' + period)


    plt.show()



if __name__ == '__main__':

    conn = sqlite3.connect('../color_analysis_sample.db')
    c = conn.cursor()

    data = get_frequent_colors(90, 10)

    #relative_freq = get_freqs()

    #print(relative_freq)
    #show(relative_freq, '1990-1995')
##
##    print(get_colors_above_threshold(3, 10))
##    print(get_colors_not_above_threshold(3, 10))

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
