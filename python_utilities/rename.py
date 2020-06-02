import glob
from shutil import copyfile
import os

#RGB
paths = glob.glob("/Users/ben/Documents/NeonTreeEvaluation/evaluation/2018/RGB/*.tif")
for path in paths:
    basename = os.path.splitext(path)[0]
    year="2018"
    dst =  "{basename}_{year}.tif".format(basename=basename,year=year)
    os.rename(src=path, dst=dst)

#CHM
paths = glob.glob("/Users/ben/Documents/NeonTreeEvaluation/evaluation/2019/CHM/*.tif")
for path in paths:
    basename = path.split("_CHM")[0]
    year="2019"
    dst =  "{basename}_{year}_CHM.tif".format(basename=basename,year=year)
    os.rename(src=path, dst=dst)
    
#Annotations
paths = glob.glob("/Users/ben/Documents/NeonTreeEvaluation/annotations/*.xml")
for path in paths:
    basename = os.path.splitext(path)[0]    
    
    dst =  "{basename}_{year}.xml".format(basename=basename,year="2019")
    copyfile(path, dst)
    
    dst =  "{basename}_{year}.xml".format(basename=basename,year="2018")    
    copyfile(path, dst)

#Competition rename

#RGB
paths = glob.glob("/Users/ben/Dropbox/Weecology/competition/test_original/RemoteSensing/RGB/MLBS*.tif")
for path in paths:
    basename = os.path.splitext(path)[0]
    dst =  "{basename}_competition.tif".format(basename=basename)
    os.rename(src=path, dst=dst)
    
#CHM
paths = glob.glob("/Users/ben/Dropbox/Weecology/competition/test_original/RemoteSensing/CHM/MLBS*.tif")
for path in paths:
    basename = path.split("_CHM")[0]
    dst =  "{basename}_competition_CHM.tif".format(basename=basename)
    os.rename(src=path, dst=dst)