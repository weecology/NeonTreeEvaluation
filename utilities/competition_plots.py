import rasterio
import geopandas

def run(file):
    crowns = geopandas.read_file(file)
    grouped = crowns.group_by(plotID)
    for name, group in grouped:
        crop_rgb(group)
        crop_hyperspectral(group)
        crop_lidar(group)
        crop_CHM(group)
    
        
