import csv

""""
Returns a dictionary of
{(color_name, period): num_appearance}
"""
def read_relative_frequency(filename):
    ret_dict = {}
    all_colors = []
    all_decades = []
    csvfile = open(filename, 'r')
    lines = csvfile.readlines()
    for row in lines[1:]:
        line = row.split(',')
        key = (line[0], line[1])
        ret_dict[key] = line[2]
        all_colors.append(line[0])
        all_decades.append(line[1])
    return ret_dict, set(all_colors), set(all_decades)

def get_freq_percentage(readFile, writeFile, thresholds):
    frequencies, all_colors, all_decades = read_relative_frequency(readFile)
    num_all_colors = len(all_colors)

    with open(writeFile, 'w') as out:
        csv_out = csv.writer(out)
        csv_out.writerow(["absolute threshold", "number of colors always above threshold", "total number of colors", "percentage"])
        for threshold in thresholds:
            not_always_above_threshold_count = 0
            for color in all_colors:
                for decade in all_decades:
                    key = (color, decade)
                    if key not in frequencies.keys() or int(frequencies[key]) < threshold:
                        not_always_above_threshold_count += 1
                        break
            always_above_threshold_count = num_all_colors - not_always_above_threshold_count
            percentage = (num_all_colors - not_always_above_threshold_count) / num_all_colors
            csv_out.writerow([threshold, always_above_threshold_count, num_all_colors, percentage])

def get_colors_above_threshold(readFile, writeFile, threshold):
    """
    Generates a csv file containing a list of colors that
    appear at least threshold times during each decade
    """
    frequencies, all_colors, all_decades = read_relative_frequency(readFile)
    sorted_decades = list(all_decades)
    sorted_decades.sort()

    with open(writeFile, 'w') as out:
        csv_out = csv.writer(out)
        csv_out.writerow(["color_term"] + sorted_decades)
        for color in all_colors:
            if_always_above_threshold = True
            frequency_during_decade = []
            for decade in sorted_decades:
                key = (color, decade)
                if key not in frequencies.keys() or int(frequencies[key]) < threshold:
                    if_always_above_threshold = False
                    break
                frequency_during_decade.append(frequencies[(color, decade)])
            if if_always_above_threshold:
                csv_out.writerow([color] + frequency_during_decade)

def get_freq_percentage_for_decade(readFile, writeFile, thresholds):
    frequencies, all_colors, all_decades = read_relative_frequency(readFile)
    num_all_colors = len(all_colors)
    sorted_decades = list(all_decades)
    sorted_decades.sort()

    with open(writeFile, 'w') as out:
        csv_out = csv.writer(out)
        csv_out.writerow(["absolute threshold", "decade", "number of colors above threshold", "total number of colors", "percentage"])
        for threshold in thresholds:
            for decade in sorted_decades:
                num_frequent_colors = 0
                for color in all_colors:
                    key = (color, decade)
                    if key in frequencies.keys() and int(frequencies[key]) >= threshold:
                        num_frequent_colors += 1
                percentage = num_frequent_colors / num_all_colors
                csv_out.writerow([threshold, decade, num_frequent_colors, num_all_colors, percentage])

def get_colors_appear_in_num_decades(readFile, writeFile, num_decades):
    """
    Generates a csv file containing a list of colors that
    appear in at least num_decades decades.
    """
    frequencies, all_colors, all_decades = read_relative_frequency(readFile)

    color_to_num_decades = {}
    for color in frequencies.keys():
        if color[0] not in color_to_num_decades.keys():
            color_to_num_decades[color[0]] = 1
        else:
            color_to_num_decades[color[0]] += 1

    with open(writeFile, 'w') as out:
        csv_out = csv.writer(out)
        csv_out.writerow(["color", "num_decades"])
        for color in color_to_num_decades.keys():
            cur_num_decades = color_to_num_decades[color]
            if cur_num_decades >= num_decades:
                csv_out.writerow([color, cur_num_decades])


if __name__ == '__main__':

    # # Get percentages of colors that appear more than threshold times
    # # during 'every' decade
    # readFile = "freq_10yr_80percent.csv"
    # writeFile = "percentage_color_mentioned.csv"
    # get_freq_percentage(readFile, writeFile, [1, 5, 10, 15, 20, 30, 50])
    #
    # # Get a list of colors that always appear more than threshold times
    # readFile = "freq_10yr_80percent.csv"
    # writeFile = "colors_above_threshold.csv"
    # get_colors_above_threshold(readFile, writeFile, 1)

    # Get percentages of colors that appear more than threshold times
    # in each 'distinct' decade
    # readFile = "freq_10yr_80percent.csv"
    # writeFile = "percentage_color_mentioned_for_each_decade.csv"
    # get_freq_percentage_for_decade(readFile, writeFile, [1, 5, 10, 15, 20, 30, 50])


    readFile = "freq_10yr_80percent.csv"
    writeFile = "colors_appear_in_3_decades.csv"
    get_colors_appear_in_num_decades(readFile, writeFile, 3)
