''''
Bounding box post-processing
After neural network predicts a rectangular box, overlay it on the point cloud and assign points for instance based detections
Create a polygon from final tree to use for evaluation
'''
import os
import pyfor
import numpy as np
import geopandas as gp
from shapely import geometry
import pyfor
import xmltodict
import rasterio
import pandas as pd
import laspy
import tempfile

#Load .laz
def load_lidar(laz_path, normalize=True):
    """
    Load lidar tile from file based on path name
    laz_path: A string of the file path of the lidar tile
    normalize: Perform ground normalization (slow)
    return: A pyfor point cloud
    """
    
    try:
        pc = pyfor.cloud.Cloud(laz_path)
        pc.extension = ".las"
        
    except FileNotFoundError:
        print("Failed loading path: %s" %(laz_path))
        
    #normalize and filter
    if normalize:
        try: 
            pc.normalize(0.33)
        except:
            print("No vertical objects in image, skipping normalization")
    
    #Quick filter for unreasonable points.
    pc.filter(min = -1, max = 100 , dim = "z")    
    
    #Check dim
    #assert (not pc.data.points.shape[0] == 0), "Lidar tile is empty!"
    
    return pc

def drape_boxes(boxes, pc, bounds=[]):
    '''
    boxes: predictions from retinanet
    pc: Optional point cloud from memory, on the fly generation
    bounds: optional utm bounds to restrict utm box
    '''
    
    #reset user_data column
    pc.data.points.user_data =  np.nan
        
    tree_counter = 1
    for box in boxes:

        #Find utm coordinates
        xmin, xmax, ymin, ymax = find_utm_coords(box = box, pc = pc, bounds=bounds)
        
        #Update points
        pc.data.points.loc[(pc.data.points.x > xmin) & (pc.data.points.x < xmax)  & (pc.data.points.y > ymin)   & (pc.data.points.y < ymax),"user_data"] = tree_counter
        
        #update counter
        tree_counter +=1 
        
    #remove ground points    
    pc.data.points.loc[pc.data.points.z < 2, "user_data"] = np.nan
    
    return pc    
    
def find_utm_coords(box, pc, rgb_res = 0.1, bounds = []):
    
    """
    Turn cartesian coordinates back to projected utm
    bounds: an optional offset for finding the position of a window within the data
    """
    xmin = box[0]
    ymin = box[1]
    xmax = box[2]
    ymax = box[3]
    
    #add offset if needed
    if len(bounds) > 0:
        tile_xmin, _ , _ , tile_ymax = bounds   
    else:
        tile_xmin = pc.data.points.x.min()
        tile_ymax = pc.data.points.y.max()
        
    window_utm_xmin = xmin * rgb_res + tile_xmin
    window_utm_xmax = xmax * rgb_res + tile_xmin
    window_utm_ymin = tile_ymax - (ymax * rgb_res)
    window_utm_ymax= tile_ymax - (ymin* rgb_res)     
        
    return(window_utm_xmin, window_utm_xmax, window_utm_ymin, window_utm_ymax)

def cloud_to_box(pc, bounds=[]):
    ''''
    pc: a pyfor point cloud with labeled tree data in the 'user_data' column.
    Turn a point cloud with a "user_data" attribute into a numpy array of boxes
    '''
    tree_boxes = [ ]
    
    tree_ids = pc.data.points.user_data.dropna().unique()
    
    #Try to follow order of input boxes, start at Tree 1.
    tree_ids.sort()
    
    #For each tree, get the bounding box
    for tree_id in tree_ids:
        
        #Select points
        points = pc.data.points.loc[pc.data.points.user_data == tree_id,["x","y"]]
        
        #turn utm to cartesian, subtract min x and max y value, divide by cell size. Max y because numpy 0,0 origin is top left. utm N is top. 
        #FIND UTM coords here
        if len(bounds) > 0:
            tile_xmin, _ , _ , tile_ymax = bounds     
            points.x = points.x - tile_xmin
            points.y = tile_ymax - points.y 
        else:
            points.x = points.x - pc.data.points.x.min()
            points.y = pc.data.points.y.max() - points.y 
        
            points =  points/ 0.1
        
        s = gp.GeoSeries(map(geometry.Point, zip(points.x, points.y)))
        point_collection = geometry.MultiPoint(list(s))        
        point_bounds = point_collection.bounds
        
        #if no area, remove treeID, just a single lidar point.
        if point_bounds[0] == point_bounds[2]:
            continue
        
        tree_boxes.append(point_bounds)
        
    #pass as numpy array
    tree_boxes =np.array(tree_boxes)
    
    return tree_boxes
    
def cloud_to_polygons(pc):
    ''''
    Turn a point cloud with a "Tree" attribute into 2d polygons for calculating IoU
    returns a geopandas frame of convex hulls
    '''
        
    hulls = [ ]
    
    tree_ids = pc.data.points.user_data.dropna().unique()
    
    for treeid in tree_ids:
        
        points = pc.data.points.loc[pc.data.points.user_data == treeid,["x","y"]].values
        s = gp.GeoSeries(map(geometry.Point, zip(points[:,0], points[:,1])))
        point_collection = geometry.MultiPoint(list(s))
        convex_hull = point_collection.convex_hull
        hulls.append(convex_hull)
        
    hulldf = gp.GeoSeries(hulls)
    
    return hulldf

def load_xml(path, dirname, res):
    """
    Load a single .xml annotations
    """
    #parse
    with open(path) as fd:
        doc = xmltodict.parse(fd.read())
    
    #grab xml objects
    tile_xml=doc["annotation"]["object"]
    
    xmin=[]
    xmax=[]
    ymin=[]
    ymax=[]
    label=[]
    
    if type(tile_xml) == list:
        
        treeID=np.arange(len(tile_xml))
        
        #Construct frame if multiple trees
        for tree in tile_xml:
            xmin.append(tree["bndbox"]["xmin"])
            xmax.append(tree["bndbox"]["xmax"])
            ymin.append(tree["bndbox"]["ymin"])
            ymax.append(tree["bndbox"]["ymax"])
            label.append(tree['name'])
    else:
        #One tree
        treeID=0
        
        xmin.append(tile_xml["bndbox"]["xmin"])
        xmax.append(tile_xml["bndbox"]["xmax"])
        ymin.append(tile_xml["bndbox"]["ymin"])
        ymax.append(tile_xml["bndbox"]["ymax"])
        label.append(tile_xml['name'])        
        
    rgb_path=doc["annotation"]["filename"]
    
    #bounds
    #read in tile to get dimensions
    full_path=os.path.join(dirname, rgb_path)

    try:
        with rasterio.open(full_path) as dataset:
            bounds=dataset.bounds
    except:
        raise("Cannot open {}".format(full_path))
        
    frame=pd.DataFrame({"treeID":treeID,
                        "xmin":xmin,"xmax":xmax,
                        "ymin":ymin,"ymax":ymax,
                        "rgb_path":rgb_path,
                        "label":label,
                        "numeric_label":0,
                        "tile_xmin":bounds.left,
                        "tile_xmax":bounds.right,
                        "tile_ymin":bounds.bottom,
                        "tile_ymax":bounds.top}
                       )

    #Modify indices, which came from R, zero indexed in python
    frame=frame.set_index(frame.index.values)

    ##Match expectations of naming, no computation needed for hand annotations
    frame['origin_xmin'] = frame["xmin"].astype(float)
    frame['origin_xmax'] = frame["xmax"].astype(float)
    frame['origin_ymin'] = frame["ymin"].astype(float)
    frame['origin_ymax'] = frame["ymax"].astype(float)
    
    return(frame)

def create_boxes(annotations):
    """
    input: annotation list
    returns xmin, ymin, xmax, ymax as a numpy array
    """
    
    boxes = annotations[["xmin","ymin","xmax","ymax"]].values.astype("float")
    
    return boxes

def write_label(point_cloud, path):
    
    #Create laspy object
    inFile = laspy.file.File("dummy.laz", header=point_cloud.data.header, mode="w")    
    for dim in point_cloud.data.points:
        setattr(inFile, dim, point_cloud.data.points[dim])
    
    #Create second laspy object (TEMP)
    outFile1 = laspy.file.File(path, mode = "w",header = inFile.header)

    #look for label name
    colnames = []
    for dimension in inFile.point_format:
        colnames.append(dimension.name)
    
    if not "label" in colnames:
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