## For each annotated RGB image, crop the corresponding CHM and HSI data. For LiDAR data see crop_training_lidar.R
import Hyperspectral
import glob
import os 
import re
import rasterio as rio
from rasterio.mask import mask
from shapely.geometry import box

### Zenodo upload
import requests
import glob
import os

def upload(path):
    """Upload an item to zenodo"""
    
    token = os.environ.get('ZENODO_TOKEN')
    
     # Get the deposition id from the already created record
    deposition_id = "4746605"
    data = {'name': os.path.basename(path)}
    files = {'file': open(path, 'rb')}
    r = requests.post('https://zenodo.org/api/deposit/depositions/%s/files' % deposition_id,
                      params={'access_token': token}, data=data, files=files)
    print("request of path {} returns {}".format(path, r.json()))
    
    
def year_from_path(path):
    #TODO FIX
    basename = os.path.splitext(os.path.basename(path))[0]
    year = basename.split("_")[0]
    
    return year

def find_sensor_path(rgb_path, lookup_pool):
    """Find a hyperspec path based on the shapefile using NEONs schema
    Args:
        lookup_pool: glob string to search for matching HSI files 
    Returns:
        year_match: full path to sensor tile
    """

    #Get file metadata from name string
    basename = os.path.splitext(os.path.basename(rgb_path))[0]
    geo_index = re.search("(\d+_\d+)_image", basename).group(1)
    match = [x for x in lookup_pool if geo_index in x]
    if len(match) == 0:
        raise ValueError("Cannot find HSI match for RGB {}".format(rgb_path))
    
    year = year_from_path(rgb_path)        
    HSI_path = [x for x in match if year in x][0]
        
    return HSI_path


def convert_h5(hyperspectral_h5_path, rgb_path, savedir):
    tif_basename = os.path.splitext(os.path.basename(rgb_path))[0] + "_hyperspectral.tif"
    tif_path = "{}/{}".format(savedir, tif_basename)

    if not os.path.exists(tif_path):
        Hyperspectral.generate_raster(h5_path=hyperspectral_h5_path,
                                      rgb_filename=rgb_path,
                                      bands="All",
                                      save_dir=savedir)

    return tif_path


def lookup_and_convert(rgb_path, hyperspectral_pool, tif_savedir):
    hyperspectral_h5_path = find_sensor_path(rgb_path, lookup_pool=hyperspectral_pool)

    #convert .h5 hyperspec tile if needed
    tif_basename = os.path.splitext(os.path.basename(rgb_path))[0] + "_hyperspectral.tif"
    tif_path = "{}/{}".format(tif_savedir, tif_basename)

    if not os.path.exists(tif_path):
        print("Converting {}".format(tif_path))
        tif_path = convert_h5(hyperspectral_h5_path, rgb_path, tif_savedir)

    return tif_path


def crop_HSI(path, hyperspectral_pool, savedir, tif_savedir):
    """Read a RGB file, find the corresponding HSI and crop it"""
    HSI_sensor_path = lookup_and_convert(path, hyperspectral_pool=hyperspectral_pool, tif_savedir=tif_savedir)
    RGB_src = rio.open(path)
    left, bottom, right, top = RGB_src.bounds
    
    HSI_src = rio.open(HSI_sensor_path)
    outImage, outTransform = mask(HSI_src, [box(left, bottom, right, top)], crop=True)
    
    out_meta = HSI_src.meta.copy()
    out_meta.update({"driver": "GTiff",
                     "height": outImage.shape[1],
                     "width": outImage.shape[2],
                     "transform": outTransform})
    
    fname = "{}/{}_hyperspectral.tif".format(savedir,os.path.splitext(os.path.basename(path))[0])
    with rio.open(fname, "w", **out_meta) as dest:
        dest.write(outImage)
    
    return fname

def crop_CHM(path,CHM_pool, savedir):
    """Lookup CHM path based on RGB data and crop"""
    basename = os.path.splitext(os.path.basename(path))[0]
    geo_index = re.search("(\d+_\d+)_image", basename).group(1)
    match = [x for x in CHM_pool if geo_index in x]
    
    if len(match) == 0:
        raise ValueError("Cannot find CHM match for RGB {}".format(path))

    year = year_from_path(path)        
    CHM_path = [x for x in match if year in x][0]

    RGB_src = rio.open(path)
    left, bottom, right, top = RGB_src.bounds
    
    CHM_src = rio.open(CHM_path)
    outImage, outTransform = rio.mask.mask(CHM_src, [box(left, bottom, right, top)], crop=True)
    
    out_meta = CHM_src.meta.copy()
    out_meta.update({"driver": "GTiff",
                     "height": outImage.shape[1],
                     "width": outImage.shape[2],
                     "transform": outTransform})
    
    fname = "{}/{}_CHM.tif".format(savedir,os.path.splitext(os.path.basename(path))[0])
    with rio.open(fname, "w", **out_meta) as dest:
        dest.write(outImage)
        
    return fname
        
def run(rgb_tile,savedir,CHM_glob, hyperspectral_glob, tif_savedir, zenodo_record=None):
    """Crop data based on annotated RGB .tif"""
    hyperspectral_pool = glob.glob(hyperspectral_glob, recursive=True)
    CHM_pool = glob.glob(CHM_glob, recursive=True)
    
    HSI_path = crop_HSI(rgb_tile, hyperspectral_pool, savedir, tif_savedir)
    CHM_path = crop_CHM(rgb_tile, CHM_pool, savedir)
    
    if zenodo_record:
        upload(rgb_tile)
        upload(HSI_path)
        upload(CHM_path)
    
if __name__ == "__main__":
    training_tiles = [
    "/orange/ewhite/b.weinstein/NeonTreeEvaluation/hand_annotations/2018_BART_4_322000_4882000_image_crop.tif",
    "/orange/ewhite/b.weinstein/NeonTreeEvaluation/hand_annotations/2018_HARV_5_733000_4698000_image_crop.tif",
    "/orange/ewhite/b.weinstein/NeonTreeEvaluation/hand_annotations/2018_JERC_4_742000_3451000_image_crop.tif",
    "/orange/ewhite/b.weinstein/NeonTreeEvaluation/hand_annotations/2018_MLBS_3_541000_4140000_image_crop2.tif",
    "/orange/ewhite/b.weinstein/NeonTreeEvaluation/hand_annotations/2018_MLBS_3_541000_4140000_image_crop.tif",
    "/orange/ewhite/b.weinstein/NeonTreeEvaluation/hand_annotations/2018_NIWO_2_450000_4426000_image_crop.tif",
    "/orange/ewhite/b.weinstein/NeonTreeEvaluation/hand_annotations/2018_OSBS_4_405000_3286000_image.tif",
    "/orange/ewhite/b.weinstein/NeonTreeEvaluation/hand_annotations/2018_SJER_3_258000_4106000_image.tif",
    "/orange/ewhite/b.weinstein/NeonTreeEvaluation/hand_annotations/2018_SJER_3_259000_4110000_image.tif",
    "/orange/ewhite/b.weinstein/NeonTreeEvaluation/hand_annotations/2018_TEAK_3_315000_4094000_image_crop.tif",
    "/orange/ewhite/b.weinstein/NeonTreeEvaluation/hand_annotations/2019_DELA_5_423000_3601000_image_crop.tif",
    "/orange/ewhite/b.weinstein/NeonTreeEvaluation/hand_annotations/2019_DSNY_5_452000_3113000_image_crop.tif",
    "/orange/ewhite/b.weinstein/NeonTreeEvaluation/hand_annotations/2019_LENO_5_383000_3523000_image_crop.tif",
    "/orange/ewhite/b.weinstein/NeonTreeEvaluation/hand_annotations/2019_ONAQ_2_367000_4449000_image_crop.tif",
    "/orange/ewhite/b.weinstein/NeonTreeEvaluation/hand_annotations/2019_OSBS_5_405000_3287000_image2.tif",
    "/orange/ewhite/b.weinstein/NeonTreeEvaluation/hand_annotations/2019_OSBS_5_405000_3287000_image_crop2.tif",
    "/orange/ewhite/b.weinstein/NeonTreeEvaluation/hand_annotations/2019_OSBS_5_405000_3287000_image_crop.tif",
    "/orange/ewhite/b.weinstein/NeonTreeEvaluation/hand_annotations/2019_SJER_4_251000_4103000_image.tif",
    "/orange/ewhite/b.weinstein/NeonTreeEvaluation/hand_annotations/2019_TOOL_3_403000_7617000_image.tif",
    "/orange/ewhite/b.weinstein/NeonTreeEvaluation/hand_annotations/2019_YELL_2_528000_4978000_image_crop2.tif",
    "/orange/ewhite/b.weinstein/NeonTreeEvaluation/hand_annotations/2019_YELL_2_541000_4977000_image_crop.tif"]
    
    for tile in training_tiles[:1]:
        
        try:
            print(tile)
            run(
            rgb_tile=tile,
            savedir="/orange/idtrees-collab/zenodo/training",
            CHM_glob="/orange/ewhite/NeonData/**/CanopyHeightModelGtif/*.tif",
            hyperspectral_glob="/orange/ewhite/NeonData/**/Reflectance/*.h5",
            tif_savedir="/orange/idtrees-collab/Hyperspectral_tifs", zenodo_record=4746605)
        except Exception as e:
            print(e)
        
