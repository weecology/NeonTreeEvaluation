#Generate data for model training
#DeepForest 19 site model
from deepforest import utilities
from deepforest import preprocess
import pandas as pd
import glob

## Pretraining ## Annotations from Silva et al. 2016 from TreeSegmentation R package:
##Gather annotation files into a single file
#data_paths = glob.glob("pretraining/*.csv")
#dataframes = (pd.read_csv(f, index_col=None) for f in data_paths)
#annotations = pd.concat(dataframes, ignore_index=True)      
#annotations.to_csv("pretraining/crops/pretraining_annotations.csv")

##Find training tiles and crop into overlapping windows for detection
##TODO dask here
#raster_list = glob.glob("pretraining/*.tif")
#for rasters in raster_list:
    #preprocess.split_training_tile(base_dir="pretraining/crops")

#convert hand annotations from xml into retinanet format
xmls = glob.glob("hand_annotations/*.xml")
annotation_list = []
for xml in xmls:
    annotation = utilities.xml_to_annotations(xml, "hand_annotations/")
    annotation_list.append(annotation)
    
#Collect hand annotations
annotations = pd.concat(annotation_list, ignore_index=True)      
annotations.to_csv("hand_annotations/hand_annotations.csv",header=None)

#TODO dask here
raster_list = glob.glob("hand_annotations/*.tif")
for raster in raster_list:
    preprocess.split_training_raster(raster, "hand_annotations/hand_annotations.csv", base_dir="hand_annotations/crops/",patch_size=400,patch_overlap=0.05)

##Gather annotation files into a single file
data_paths = glob.glob("hand_annotations/crops/*.csv")
dataframes = (pd.read_csv(f, index_col=None) for f in data_paths)
annotations = pd.concat(dataframes, ignore_index=True)      
annotations.to_csv("hand_annotations/crops/hand_annotations.csv")
print(annotations.head())