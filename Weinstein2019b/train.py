#DeepForest 19 site model
import deepforest
import pandas as pd
import glob

## Pretraining ## Annotations from Silva et al. 2016 from TreeSegmentation R package:
#Gather annotation files into a single file
data_paths = glob.glob("pretraining/*.csv")
dataframes = (pd.read_csv(f, index_col=None) for f in data_paths)
annotations = pd.concat(dataframes, ignore_index=True)      
annotations.to_csv("pretraining/crops/pretraining_annotations.csv")

#Find training tiles and crop into overlapping windows for detection
#TODO dask here
raster_list = glob.glob("pretraining/*.tif")
for rasters in raster_list:
    deepforest.preprocess.split_training_tile(base_dir="pretraining/crops")
    
#Pretrain deepforest on Silva annotations
deepforest_model = deepforest.deepforest()
deepforest_model.train("pretraining/crops/pretraining_annotations.csv")

#convert hand annotations from xml into retinanet format
for xml in xmls:
    deepforest.utilities.xml_to_annotations(xml)

#Collect hand annotations
data_paths = glob.glob("hand_annotations/*.csv")
dataframes = (pd.read_csv(f, index_col=None) for f in data_paths)
annotations = pd.concat(dataframes, ignore_index=True)      
annotations.to_csv("hand_annotations/crops/hand_annotations.csv")

#TODO dask here
raster_list = glob.glob("hand_annotations/*.tif")
for rasters in raster_list:
    deepforest.preprocess.split_training_tile(base_dir="hand_annotations/crops")
    
#retrain model based on hand annotation crops, assign the weights from pretraining model
deepforest_model.training_model.save_weights("snapshots/pretraining_weights.h5")
deepforest_model.config["weights"] = "snapshots/pretraining_weights.h5"
deepforest_model.train("hand_annotations/crops/hand_annotations.csv")


    
