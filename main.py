"""
Author: Igor Kim
E-mail: igor.skh@gmail.com

Reader module for R&S FSVR Signal Analyzer DAT files
"""
from FSVRReader import FSVRReader
import matplotlib.pyplot as plt


def time_delta_eval(reader, n=10):
    """
    Evaluates delta time between frames
    """
    time_delta = []
    last_time = 0
    for i in range(n):
        reader.read_frame()
        if i == 0:
            time_delta.append(0)
        else:
            time_delta.append(last_time - reader.last_frame['Timestamp'])
        last_time = reader.last_frame['Timestamp']

    return time_delta


def time_delta_plot(reader, n=10):
    td = time_delta_eval(reader, n)
    plt.plot(td, "ro")
    plt.xlabel("Frame")
    plt.ylabel("Time Difference")
    plt.savefig("time_delta_eval"+str(n)+".png")
    plt.clf()


def threshold_statistic_plot(reader, threshold, filter_mask, n=10):
    td = threshold_statistic_analyze(reader, threshold, filter_mask, n)

    horiz_line_data = [threshold for i in range(len(td))]
    plt.plot(horiz_line_data, 'b-')

    plt.plot(td, "ro")
    plt.xlabel("Data Frame")
    plt.ylabel("Level")
    plt.savefig("threshold_statistic"+str(n)+".png")
    plt.clf()


def threshold_statistic_analyze(reader, threshold, filter_mask, n=10):
    result = []
    for i in range(n):
        reader.read_frame()
        # vals = list(reader.last_frame['Data'].values())
        # keys = list(reader.last_frame['Data'].keys())
        # max_val = max(vals)
        # max_idx = vals.index(max_val)
        # print(max_val, keys[max_idx])
        avg = 0
        for filter_val in filter_mask:
            avg += reader.last_frame['Data'][filter_val]
        avg = avg/len(filter_mask)
        result.append(avg)
    return result

if __name__ == '__main__':
    reader = FSVRReader("252MKS_001.DAT")

    threshold = -75
    filter_mask = [2433075000.0]
    data_points = 50

    # read DAT file header
    reader.read_header()
    # print(reader.header, reader.next_line)
    # 35
    # 39 empty
    # evaluate time difference
    # time_delta_plot(data_points)
    # reader.plot_frame()
    threshold_statistic_plot(reader, threshold, filter_mask, data_points)