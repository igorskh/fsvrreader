# README #

This python modules are developed for analysing dump files of spectrum analyser R&D FSVR

### Important notice for reader class ###

If you would like to change reader class for another device, important to know that *header* variable is used by analysis class, it is a dictionary, all values of *header* are lists, the following keys are used:
* header['Frames'][0] - available number of time frames
* header['x-Unit'][0] - unit of x axis
* header['SWT'][0] - sweep time