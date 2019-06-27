import glob
import os
import Lidar
import laspy

#Training tiles
def annotate_tile(laz_path, path_to_rgb, xml_path):
    annotations= Lidar.load_xml(xml_path, path_to_rgb, res=0.1)
    
    point_cloud = Lidar.load_lidar(laz_path)
    
    #Create boxes
    boxes = Lidar.create_boxes(annotations)

    #Drape RGB bounding boxes over the point cloud
    point_cloud = Lidar.drape_boxes(boxes, point_cloud)
        
    #Write Laz
    point_cloud.write(laz_path)
    
    #write csv for merge
    csv_path = os.path.splitext(os.path.basename(laz_path))[0] + ".csv"
    point_cloud.data.points[["x","y","z","user_data"]].to_csv(csv_path)
    
annotate_tile(laz_path="../TEAK/training/NEON_D17_TEAK_DP1_315000_4094000_classified_point_cloud_colorized_crop.laz",
              path_to_rgb="../TEAK/training/", 
              xml_path= "../TEAK/annotations/2018_TEAK_3_315000_4094000_image_crop.xml")
    
def annotate_eval_plots(site):
    path_to_rgb = "../" + site +"/plots/"
    path_to_laz = path_to_rgb
    path_to_annotations = "../NIWO/annotations/"
    
    #For each .laz file in directory.
    laz_files = glob.glob(path_to_laz+"*.laz")
    
    for laz in laz_files:
        print(laz)
        #Load laz
        point_cloud = Lidar.load_lidar(laz)
        
        #Find annotations
        basename = os.path.basename(laz)
        basename = os.path.splitext(basename)[0]
        xml_path = os.path.join(path_to_annotations,basename + ".xml")
        
        if (os.path.exists(xml_path)):
            #Load annotations and get utm bounds from tif image
            annotations= Lidar.load_xml(xml_path, path_to_rgb, res=0.1)
        else:
            print("{} does not exist, skipping image".format(xml_path))
            continue
        
        #Create boxes
        boxes = Lidar.create_boxes(annotations)
    
        #Drape RGB bounding boxes over the point cloud
        point_cloud = Lidar.drape_boxes(boxes, point_cloud)
            
        #Write Laz
        point_cloud.write(laz)
