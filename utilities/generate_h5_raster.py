import numpy as np
import Hyperspectral
import rasterio
import os

#Load RGB raster and get bounds
h5_path = "/Users/ben/Downloads/2018 2/FullSite/D07/2018_MLBS_3/L3/Spectrometer/Reflectance/NEON_D07_MLBS_DP3_541000_4140000_reflectance.h5"
rgb_filename = "../MLBS/training/2018_MLBS_3_541000_4140000_image_crop.tif"
with rasterio.open(rgb_filename) as dataset:
    rgb_bounds = dataset.bounds   
    
#Load h5 hyperspectral tile and extractr epsg from rgb, epsg as string.
epsg = str(dataset.crs).split(":")[-1]
#Get numpy array and metadata
refl_md, refl = Hyperspectral.h5refl2array(h5_path, epsg = epsg)

#Delete water absorption bands
#rgb = np.r_[0:425]
#rgb = np.delete(rgb, np.r_[419:425])
#rgb = np.delete(rgb, np.r_[283:315])
#rgb = np.delete(rgb, np.r_[192:210])

#Select nanometers RGB see NeonTreeEvaluation/utilities/neon_aop_bands.csv
rgb = [16, 54,112]

#print(itc_id, itc_xmin, itc_xmax, itc_ymin, itc_ymax, epsg)
xmin, xmax, ymin, ymax = refl_md['extent']
print(xmin, xmax, ymin, ymax)

#Set extent in utm
clipExtent = {}
clipExtent['xMin'] = rgb_bounds.left
clipExtent['xMax'] = rgb_bounds.right
clipExtent['yMin'] = rgb_bounds.bottom
clipExtent['yMax'] = rgb_bounds.top
print(clipExtent)

#Get hyperspectral array extent with respect to the pixel index
subInd = Hyperspectral.calc_clip_index(clipExtent, refl_md['ext_dict'])
subInd['xMax'] = int(subInd['xMax'])
subInd['xMin'] = int(subInd['xMin'])
subInd['yMax'] = int(subInd['yMax'])
subInd['yMin'] = int(subInd['yMin'])
print(subInd)

#Index numpy array of hyperspec reflectance
refl = refl[(subInd['yMin']):subInd['yMax'], (subInd['xMin']):subInd['xMax'], :]
refl.shape
print(refl.shape)

#Create raster object from numpy array
hyperspec_raster = Hyperspectral.create_raster(subInd, rgb, refl)
sub_meta = refl_md

#Create new filepath
tilename = os.path.splitext(os.path.basename(rgb_filename))[0] + "_false_color.tif"

#Working_dir
wd = "../MLBS/training/"

#Save georeference crop to file 
Hyperspectral.array2raster(tilename, hyperspec_raster, sub_meta, clipExtent, wd)