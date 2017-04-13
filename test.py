"""
Author: Igor Kim
E-mail: igor.skh@gmail.com

Reader module for R&S FSVR Signal Analyzer DAT files
"""
from FSVRAnalysis import FSVRAnalysis

if __name__ == '__main__':
    data_points = 10
    analyzer = FSVRAnalysis("252MKS_001.DAT")
    analyzer.threshold = -75
    analyzer.filter_mask = [2433075000.0]
    analyzer.frame_plot(data_points)
    analyzer.filtering_statistic_plot(data_points)
    analyzer.time_delta_plot(data_points)