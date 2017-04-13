# -*- coding: utf-8 -*-
"""
Author: Igor Kim
E-mail: igor.skh@gmail.com

Reader module for R&S FSVR Signal Analyzer DAT files

April 2017
"""
from FSVRAnalysis import FSVRAnalysis

analyzer = FSVRAnalysis("../dat/252MKS_001.DAT")
analyzer.set_data_points(34)
analyzer.set_threshold(-75)
analyzer.get_info()
analyzer.last_frame_plot()
analyzer.avg_values_plot()