import glob
import os
import Lidar
import laspy
        
def write_label(point_cloud, path):
    
    #Create laspy object
    inFile = laspy.file.File("/Users/Ben/Desktop/test.laz", header=point_cloud.data.header, mode="w")    
    for dim in point_cloud.data.points:
        setattr(inFile, dim, point_cloud.data.points[dim])
    
    #Create second laspy object
    outFile1 = laspy.file.File(path, mode = "w",header = inFile.header)

    outFile1.define_new_dimension(
        name="label",
        data_type=5,
        description = "Integer Tree Label"
     )
    
    # copy fields 
    for dimension in inFile.point_format:
        dat = inFile.reader.get_dimension(dimension.name)
        outFile1.writer.set_dimension(dimension.name, dat)
        
    outFile1.label = point_cloud.data.points.user_data
    outFile1.close()
    
#Training tiles
def annotate_tile(laz_path, path_to_rgb, xml_path):
    annotations= Lidar.load_xml(xml_path, path_to_rgb, res=0.1)
    
    point_cloud = Lidar.load_lidar(laz_path)
    
    #Create boxes
    boxes = Lidar.create_boxes(annotations)

    #Drape RGB bounding boxes over the point cloud
    point_cloud = Lidar.drape_boxes(boxes, point_cloud)
        
    #Write Laz with label info
    write_label(point_cloud, laz_path)
    
#annotate_tile(laz_path="../SJER/training/NEON_D17_SJER_DP1_258000_4106000_classified_point_cloud_colorized.laz",
              #path_to_rgb="../SJER/training/", 
              #xml_path= "../SJER/annotations/2018_SJER_3_258000_4106000_image.xml")
    
def annotate_eval_plots(site):
    path_to_rgb = "../" + site +"/plots/"
    path_to_laz = path_to_rgb
    path_to_annotations = "../" + site +"/annotations/"
    
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
        write_label(point_cloud, laz)

sites = ["SJER","NIWO","TEAK","MLBS"]

for site in sites:
    annotate_eval_plots(site)