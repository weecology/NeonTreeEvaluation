import glob
import os

import Lidar
          
#Training tiles
def annotate_tile(laz_path, path_to_rgb, xml_path):
    annotations= Lidar.load_xml(xml_path, path_to_rgb, res=0.1)
    
    point_cloud = Lidar.load_lidar(laz_path)
    
    #Create boxes
    boxes = Lidar.create_boxes(annotations)

    #Drape RGB bounding boxes over the point cloud
    point_cloud = Lidar.drape_boxes(boxes, point_cloud)
        
    #Write Laz with label info
    Lidar.write_label(point_cloud, laz_path)
    
def annotate_eval_plots():
    path_to_rgb = "../evaluation/RGB/"
    path_to_laz = "../evaluation/LiDAR/"
    path_to_annotations = "../annotations/"
    
    #For each .laz file in directory.
    laz_files = glob.glob(path_to_laz+"*.laz")
    
    for laz in laz_files:
        print(laz)
        #Load laz
        point_cloud = Lidar.load_lidar(laz, normalize=True)
        
        #Find annotations
        basename = os.path.basename(laz)
        basename = os.path.splitext(basename)[0]
        xml_path = os.path.join(path_to_annotations,basename + ".xml")
        
        if (os.path.exists(xml_path)):
            #Load annotations and get utm bounds from tif image
            try:
                annotations= Lidar.load_xml(xml_path, path_to_rgb, res=0.1)
            except Exception as e:
                print(e)
                continue
        else:
            print("{} does not exist, skipping image".format(xml_path))
            continue
        
        #Create boxes
        boxes = Lidar.create_boxes(annotations)
    
        #Drape RGB bounding boxes over the point cloud
        point_cloud = Lidar.drape_boxes(boxes, point_cloud)
            
        #Write Laz
        Lidar.write_label(point_cloud, laz)

if __name__ == "__main__":
    #annotate_tile(laz_path="../SJER/training/NEON_D17_SJER_DP1_258000_4106000_classified_point_cloud_colorized.laz",
        #path_to_rgb="../SJER/training/", 
        #xml_path= "../SJER/annotations/2018_SJER_3_258000_4106000_image.xml")    
    
    annotate_eval_plots()