"""
On the fly generator. Crop out portions of a large image, and pass boxes and annotations. This follows the csv_generator template. Satifies the format in generator.py
"""
import pandas as pd
import h5py

from keras_retinanet.preprocessing.generator import Generator
from keras_retinanet.utils.image import read_image_bgr
from keras_retinanet.utils.visualization import draw_annotations

import numpy as np
from PIL import Image
from six import raise_from
import random

import csv
import sys
import os.path

import cv2
import slidingwindow as sw
import itertools

from DeepForest.utils import image_utils

class H5Generator(Generator):
    """ Generate data for a custom h5 dataset.
    """

    def __init__(
        self,
        data,
        DeepForest_config,
        group_method="none",
        name=None,
        **kwargs
    ):
        """ Initialize a data generator.

        """
        self.image_names = []
        self.image_data  = {}
        self.name = name
        self.windowdf = data
        self.DeepForest_config = DeepForest_config
        
        #Holder for the group order, after shuffling we can still recover loss -> window
        self.group_order = {}
        self.group_method=group_method
        
        #Holder for image path, keep from reloading same image to save time.
        self.previous_image_path=None
        
        #Turn off lidar checking during prediction for training sets.
        self.with_lidar=False
        
        #Read classes
        self.classes={"Tree": 0}
        
        #Create label dict
        self.labels = {}
        for key, value in self.classes.items():
            self.labels[value] = key        
        
        #Set groups at first order.
        self.define_groups(shuffle=False)
        
        #report total number of annotations
        self.total_trees = self.total_annotations()
                
        super(H5Generator, self).__init__(**kwargs)
                        
    def __len__(self):
        """Number of batches for generator"""
        return len(self.groups)
         
    def size(self):
        """ Size of the dataset.
        """
        image_data= self.windowdf.to_dict("index")
        image_names = list(image_data.keys())
        
        return len(image_names)

    def num_classes(self):
        """ Number of classes in the dataset.
        """
        return max(self.classes.values()) + 1

    def name_to_label(self, name):
        """ Map name to label.
        """
        return self.classes[name]

    def label_to_name(self, label):
        """ Map label to name.
        """
        return self.labels[label]

    def total_annotations(self):
        """ Find the total number of annotations for the dataset
        """
        #Find matching annotations        
        tiles = self.windowdf[["tile","site"]].drop_duplicates()
        total_annotations = 0
                
        #Select annotations 
        #Optionally multiple h5 dirs
        for index, row in tiles.iterrows():
            h5_dir = self.DeepForest_config[row["site"]]["h5"]        
            tilename = row["tile"]
            csv_name = os.path.join(h5_dir, os.path.splitext(tilename)[0]+'.csv')
            
            try:
                annotations = pd.read_csv(csv_name)
            except Exception as e:
                print(e)
                print("The csv named {} from tilename {} encountered an error when counting annotations".format(csv_name, tilename))
                continue
            
            selected_annotations = pd.merge(self.windowdf, annotations)
            total_annotations += len(selected_annotations)        
        
        print("There are a total of {} tree annotations in the {} generator".format(total_annotations, self.name))       
        
        return(total_annotations)
    
    def define_groups(self, shuffle=False):
        '''
        Define image data and names based on grouping of tiles for computational efficiency 
        '''
        #group by tile
        print(self.windowdf.tile.unique()[0:5])        
        
        if shuffle:
            groups = [df for _, df in self.windowdf.groupby('tile')]
            
            #Shuffle order of windows within a tile
            groups = [x.sample(frac=1) for x in groups]      
            
            #Shuffle order of tiles
            random.shuffle(groups)
            newdf = pd.concat(groups,sort=False,ignore_index=True)
        else:
            newdf = self.windowdf
        
        #Bring pandas frame back together
        image_data = newdf.to_dict("index")
        image_names = list(image_data.keys())
        
        return(image_data, image_names)
    
    def load_image(self, image_index):
        """ Load an image at the image_index.
        """
        #Select sliding window and tile
        try:
            image_name = self.image_names[image_index]
        except Exception as e:
            print("Failed on image index {}".format(image_index))
            print("There are {} names in the image names object".format(len(self.image_names)))
        
        self.row = self.image_data[image_name]
        
        #Open image to crop
        ##Check if tile the is same as previous draw from generator, this will save time.
        if not self.row["tile"] == self.previous_image_path:
            
            #Set directory based on site
            h5_dir = self.DeepForest_config[self.row["site"]]["h5"]
            
            #tilename for h5 and csv files
            tilename = os.path.split(self.row["tile"])[-1]
            tilename = os.path.splitext(tilename)[0]                        
            h5_name = os.path.join(h5_dir, tilename+'.h5')
            csv_name = os.path.join(h5_dir, tilename+'.csv')
            
            #Read h5 
            self.hf = h5py.File(h5_name, 'r')
            
            #Read corresponding csv labels
            self.annotations = pd.read_csv(csv_name)
            
        #read image from h5
        window = self.row["window"]
        image = self.hf["train_imgs"][window,...]
        
        #Save image path for next evaluation to check
        self.previous_image_path = self.row["tile"]
            
        return image
    
    def load_annotations(self, image_index):
        '''
        Load annotations from csv file
        '''
        #Select sliding window and tile
        image_name = self.image_names[image_index]        
        self.row = self.image_data[image_name]
       
        #Find annotations
        annotations = self.annotations.loc[(self.annotations["tile"] == self.row["tile"]) & (self.annotations["window"] == self.row["window"])]
            
        return annotations[["0","1","2","3","4"]].values
    
    def compute_windows(self):
        ''''
        Create a sliding window object for reference
        '''
        #Load tile
        site = self.annotation_list.site.unique()[0]
        base_dir = self.DeepForest_config[site][self.name]["RGB"]        
        image = os.path.join(base_dir, self.annotation_list.rgb_path.unique()[0])
        im = Image.open(image)
        numpy_image = np.array(im)    
        
        #Generate sliding windows
        windows = sw.generate(numpy_image, sw.DimOrder.HeightWidthChannel,  self.DeepForest_config["patch_size"], self.DeepForest_config["patch_overlap"])
        
        return(windows)
        