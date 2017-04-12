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


def time_delta_plot(n=10):
    td = time_delta_eval(reader, 35)
    plt.plot(td, "ro")
    plt.xlabel("Frame")
    plt.ylabel("Time Difference")
    plt.savefig("time_delta_eval"+str(n)+".png")
    plt.clf()

if __name__ == '__main__':
    reader = FSVRReader("252MKS_001.DAT")
    reader.threshold = -75

    # read DAT file header
    reader.read_header()
    # print(reader.header, reader.next_line)
    # 35
    # 39 empty
    # evaluate time difference
    time_delta_plot(35)
    reader.plot_frame()