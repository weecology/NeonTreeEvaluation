import os
import glob
import pandas as pd
from DeepForest.onthefly_generator import OnTheFlyGenerator
from DeepForest.preprocess import NEON_annotations, load_csvs, split_training
from DeepForest import Generate
from DeepForest.h5_generator import H5Generator
from DeepForest.utils import image_utils

def load_retraining_data(DeepForest_config):
    """
    Overall function to find training data based on config file
    mode: retrain
    """    
    #for each hand_annotation tile, check if its been generated.
    for site in DeepForest_config["hand_annotation_site"]:
        RGB_dir = DeepForest_config[site]["hand_annotations"]["RGB"]
        h5_dirname = os.path.join(DeepForest_config[site]["h5"], "hand_annotations")
        
        #Check if hand annotations have been generated. If not create H5 files.
        path_to_handannotations = []
        if os.path.isdir(RGB_dir):
            tilenames = glob.glob(os.path.join(RGB_dir,"*.tif"))
            #remove any false color tiles
            tilenames = [x for x in tilenames if not "false_color" in x]

        else:
            tilenames = [os.path.splitext(os.path.basename(RGB_dir))[0]]
            
        for x in tilenames:
            tilename = os.path.splitext(os.path.basename(x))[0]                
            tilename = os.path.join(h5_dirname, tilename) + ".csv"
            path_to_handannotations.append(os.path.join(RGB_dir, tilename))            
         
        #for each annotation, check if exists in h5 dir
        for index, path in enumerate(path_to_handannotations):
            if not os.path.exists(path):
                
                #Generate xml name, assumes annotations are one dir up from rgb dir
                annotation_dir = os.path.join(os.path.dirname(os.path.dirname(RGB_dir)),"annotations")
                annotation_xmls = os.path.splitext(os.path.basename(tilenames[index]))[0] + ".xml"
                full_xml_path = os.path.join(annotation_dir, annotation_xmls )
                
                print("Generating h5 for hand annotated data from tile {}".format(path))                
                Generate.run(tile_xml = full_xml_path, mode="retrain", site = site, DeepForest_config=DeepForest_config)
        
    #combine data across sites        
    dataframes = []
    for site in DeepForest_config["hand_annotation_site"]:
        h5_dirname = os.path.join(DeepForest_config[site]["h5"], "hand_annotations")
        df = load_csvs(h5_dirname)
        df["site"] = site
        dataframes.append(df)
    data = pd.concat(dataframes, ignore_index=True)      
    
    return data

def load_training_data(DeepForest_config):
    """
    Overall function to find training data based on config file
    mode: train
    """
    #For each training directory (optionally more than one site)
    dataframes = []
    for site in DeepForest_config["pretraining_site"]:
        h5_dirname = DeepForest_config[site]["h5"]
        df = load_csvs(h5_dirname)
        df["site"] = site
        dataframes.append(df)
        
    #Create a dict assigning the tiles to the h5 dir
    data = pd.concat(dataframes, sort=False).reset_index(drop=True)         
    return data
    
    
def create_NEON_generator(batch_size, DeepForest_config, name="evaluation"):
    """ Create generators for training and validation.
    """
    annotations, windows = NEON_annotations(DeepForest_config)

    #Training Generator
    generator =  OnTheFlyGenerator(
        annotations,
        windows,
        batch_size = batch_size,
        DeepForest_config = DeepForest_config,
        group_method="none",
        name=name,
        preprocess_image=image_utils.preprocess
    )
    
    return(generator)

def create_h5_generators(data, DeepForest_config):
    """ Create generators for training and validation.
    """
    #Split training and test data
    train, test = split_training(data, DeepForest_config, experiment=None)

    #Write out for debug
    if DeepForest_config["save_image_path"]:
        train.to_csv(os.path.join(DeepForest_config["save_image_path"],'training_dict.csv'), header=False)         
    
    if DeepForest_config["spatial_filter"]:
        train = spatial_filter(train, DeepForest_config)
        
    #Training Generator
    train_generator = H5Generator(train, 
                                  batch_size = DeepForest_config["batch_size"], 
                                  DeepForest_config = DeepForest_config, 
                                  name = "training",
                                  preprocess_image=image_utils.preprocess)

    #Validation Generator, check that it exists
    if test is not None:
        validation_generator = H5Generator(test, 
                                           batch_size = DeepForest_config["batch_size"], 
                                           DeepForest_config = DeepForest_config, 
                                           name = "training",
                                           preprocess_image=image_utils.preprocess)
    else:
        validation_generator = None
        
    return train_generator, validation_generator

def spatial_filter(train, DeepForest_config):
    """
    Remove any 1km tiles from pretraining data that contain evaluation plots
    """
    
    print("Train shape before spatial filtering {}".format(train.shape))
    annotations, windows = NEON_annotations(DeepForest_config)      
    
    #load plot data
    field_data = pd.read_csv(DeepForest_config["field_data_path"])
    
    #unique site windows
    plotID = windows.tile.values
    plotID = [os.path.splitext(x)[0] for x in plotID ]
    
    for plot_name in plotID:
        plot_data = field_data[field_data.plotID == plot_name][["siteID","plotID","easting","northing"]].drop_duplicates().dropna()
        
        if plot_data.shape[0] ==0:
            print("{} has no point records".format(plot_name))
            continue
            
        #find geoindex
        easting = int('%.0f' % (plot_data.easting.iloc[0]/1000) )* 1000
        northing = int('%.0f' % (plot_data.northing.iloc[0]/1000) )* 1000
        
        geo_index = "{}_{}".format(easting,northing)
        
        #lookup matching tiles by site and remove
        print("plot {} intersects with {} annotations".format(plot_name,sum(train.tile.str.contains(geo_index))))
        train = train[~train.tile.str.contains(geo_index)]
    
    print("Train shape after spatial filtering {}".format(train.shape))
    return train