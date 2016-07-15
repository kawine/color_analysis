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
        relative_freq.append((item[0], item[1]/total_freq))

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

    relative_freq = get_freqs()

    print(relative_freq)
    #show(relative_freq, '1990-1995')
    
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
