# README #

This python modules are developed for analysing dump files of spectrum analyser R&D FSVR
### If you would like to change reader class for another device, important to know that *header* variable is used by FSVRAnalysis class, it is a dictionary, all values of *header* are lists, the following keys are used: ###
* header['Frames'][0] - available number of time frames
* header['x-Unit'][0] - unit of x axis
* header['SWT'][0] - sweep time
### Following methods are used as well: ### 
* reopen_file() - resets pointer in the text file
* read_frame() - reads the next time frame
###  Following keys of *last_frame* variable are used: ### 
* last_frame['Timestamp'] - timestamp of the last timeframe
* last_frame['Data'] - contains dictionary, where keys are frequencies and values are levels {f1:l1, f2:l2, f3: l3}
### If something is missing, it is recommended to create an empty variable. However, if *header['Frames'][0]* is less than 2, *header['SWT'][0]* is not necessary. ###