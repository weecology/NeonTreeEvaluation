import glob
import os
import Lidar

path_to_rgb = "../NIWO/plots/"
path_to_laz = "../NIWO/plots/"
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
