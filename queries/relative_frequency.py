import sqlite3
import math
import matplotlib.pyplot as plt
import numpy as np
import collections
import csv

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

def get_freqs_over_period(period, threshold, filename):
    """
    Get a list of (color_name, period, absolute_freq, relative_freq) tuples
    """
    absolute_freq_query = """SELECT color.name, book.year / {p} * {p}, count(*) as frequency
        FROM mention
        JOIN color ON mention.color = color.id
        JOIN clause ON mention.clause = clause.id
        JOIN sentence ON clause.sentence = sentence.id
        JOIN book ON sentence.book = book.id
        GROUP BY book.year / {p} * {p}, color.name
        ORDER BY book.year / {p} * {p}, count(*) desc;""".format(p=period)

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

    # {Period: number of distinct colors} mapping
    period_to_num_colors = dict()
    for item in absolute_freq:
        if item[1] not in period_to_num_colors:
            period_to_num_colors[item[1]] = 1
        else:
            period_to_num_colors[item[1]] += 1

    # List of (color_id, color_name, period, abs_freq, rel_freq) tuples
    relative_freq = []
    cur_period = 0
    for i in range(0, len(absolute_freq)):
        item = absolute_freq[i]
        period = item[1]
        if cur_period != period:
            cur_period = period
            threshold_val = absolute_freq[i + math.ceil(period_to_num_colors[period] * threshold)][2]
            rel_threshold_val = float(threshold_val)/period_to_length[period] * 100000
            print(period, period_to_num_colors[period], threshold_val, rel_threshold_val)
        rel_freq = float(item[2])/period_to_length[period] * 100000
        relative_freq.append((item[0], period, item[2], rel_freq, threshold_val, rel_threshold_val))

    with open(filename, 'w+') as out:
        csv_out=csv.writer(out)
        csv_out.writerow(["color_name", "period", "absolute_freq", "relative_freq", "absolute_freq_threshold", "relative_freq_threshold"])
        for row in relative_freq:
            csv_out.writerow(row)

    return relative_freq

def get_frequent_colors(threshold, period):
    """
    Get a dictionary in the form
    {color_name:
        {   periods_above_threshold: [ list of periods ],
            always_above_threshold: true/false }, ...}
    """
    absolute_freq_query = """SELECT color.name, book.year / {p} * {p}, count(*) as frequency
        FROM mention
        JOIN color ON mention.color = color.id
        JOIN clause ON mention.clause = clause.id
        JOIN sentence ON clause.sentence = sentence.id
        JOIN book ON sentence.book = book.id
        GROUP BY book.year / {p} * {p}, color.name
        ORDER BY book.year / {p} * {p}, count(*) desc;""".format(p=period)

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

    # {Period: number of distinct colors} mapping
    period_to_num_colors = dict()
    for item in absolute_freq:
        if item[1] not in period_to_num_colors:
            period_to_num_colors[item[1]] = 1
        else:
            period_to_num_colors[item[1]] += 1

    # {(color_id, color_name): {'periods_above_threshold': lst, 'always_above_threshold': bool}}
    relative_freq = collections.OrderedDict()
    cur_period = 0
    num_periods = 0
    for i in range(0, len(absolute_freq)):
        item = absolute_freq[i]
        key = item[0]
        period = item[1]
        freq = item[2]
        if cur_period != period:
            cur_period = period
            num_periods += 1
            threshold_val = absolute_freq[i + math.ceil(period_to_num_colors[period] * threshold)][2]
            rel_threshold_val = float(threshold_val)/period_to_length[period] * 100000
        freq_val = float(item[2])/period_to_length[period] * 100000
        if key not in relative_freq:
            relative_freq[key] = {'periods_above_threshold': [], 'always_above_threshold': True}
        if freq_val >= rel_threshold_val:
            relative_freq[key]['periods_above_threshold'].append(period)
        else:
            relative_freq[key]['always_above_threshold'] = False

    for key in relative_freq:
        if len(relative_freq[key]['periods_above_threshold']) < num_periods:
            relative_freq[key]['always_above_threshold'] = False

    return relative_freq

def get_colors_above_threshold(threshold, period, freq_data, filename):
    """
    Get a list of color ids that are always above the given threshold
    """

    above_threshold = []
    for key in freq_data:
        if freq_data[key]['always_above_threshold']:
            above_threshold.append([key])

    with open(filename, 'w+') as out:
        csv_out=csv.writer(out)
        csv_out.writerow(["color_name"])
        for row in above_threshold:
            csv_out.writerow(row)

    return above_threshold

def get_colors_not_above_threshold(threshold, period, freq_data, filename):
    """
    Get a list of colors ids that are not always above the given threshold
    """

    not_above_threshold = []
    for key in freq_data:
        if not freq_data[key]['always_above_threshold']:
            not_above_threshold.append((key, freq_data[key]['periods_above_threshold']))

    with open(filename, 'w+') as out:
        csv_out=csv.writer(out)
        csv_out.writerow(["color_name", "periods_above_threshold"])
        for row in not_above_threshold:
            csv_out.writerow(row)

    return not_above_threshold

def show(data, period):

    plt.bar(np.arange(len(data)), [x[1] for x in data], align='center', alpha=0.5)
    plt.xticks(np.arange(len(data)), [x[0] for x in data], rotation='vertical', fontsize=5)
    plt.ylabel('Usage')
    plt.title('Relative frequencies for ' + period)


    plt.show()



if __name__ == '__main__':
    conn = sqlite3.connect('../color_analysis_merged.db')
    c = conn.cursor()
    # relative_freq = get_freqs()

    # print(relative_freq)
    # show(relative_freq, '1990-1995')
    freq_data = get_frequent_colors(0.8, 10)

    # get_freqs_over_period(10, 0.8, "freq_10yr_80percent.csv")
    get_colors_above_threshold(0.8, 10, freq_data, "colors_always_above_threshold_10yr_80per.csv")
# get_colors_not_above_threshold(0.8, 10, freq_data, "colors_sometimes_below_threshold_10yr_80per.csv")

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
