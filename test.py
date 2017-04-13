"""
Author: Igor Kim
E-mail: igor.skh@gmail.com

Reader module for R&S FSVR Signal Analyzer DAT files

April 2017
"""
from FSVRAnalysis import FSVRAnalysis

analyzer = FSVRAnalysis("../dat/252MKS_001.DAT")
analyzer.data_points = 100
analyzer.threshold = -75
analyzer.get_info()
analyzer.avg_values_plot()
