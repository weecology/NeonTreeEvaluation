import Hyperspectral
import argparse
import sys
import rasterio

def parse_args(args):
    parser = argparse.ArgumentParser(description='Generate .tif file for a cropped h5 reflectance raster')
    parser.add_argument('--rgb_filename',    help='path to rgb.tif filename to get geospatial metadata')
    parser.add_argument('--h5_path',    help='path to h5 NEON hyperspectral tile')
    parser.add_argument('--save_dir',    help='directory to save output raster ')
    parser.add_argument('--bands',    help='All or "false_color" bands', default="false_color")
    args = parser.parse_args(args)
    
    return args

if __name__ == "__main__":
    
    #Parse args
    args = parse_args(sys.argv[1:])
    #Crop and create raster
    status = Hyperspectral.generate_raster(h5_path = args.h5_path, rgb_filename=args.rgb_filename, bands=args.bands, save_dir=args.save_dir)
    print("{} : {}".format(args.rgb_filename,status))
    
    