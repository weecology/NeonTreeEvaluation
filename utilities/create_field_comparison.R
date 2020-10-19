#Create a figure of matching IoU interesections
library(sf)
library(raster)
library(NeonTreeEvaluation)
predictions<-read_sf("/Users/ben/Dropbox/Weecology/Benchmark/NEON_field_polygons/MLBS_crops/2.shp")
rgb<-stack("/Users/ben/Dropbox/Weecology/Benchmark/NEON_field_polygons/MLBS_crops/2.tif")
ground_truth<-st_crop(crowns,extent(rgb))
plotRGB(rgb)
plot(st_geometry(ground_truth),add=T,lwd=4)
plot(st_geometry(predictions),add=T,border="red",lwd=1)


write_sf(ground_truth,"/Users/Ben/Dropbox/Weecology/Benchmark/Figures/matched_field_crowns.shp")
write_sf(predictions,"/Users/Ben/Dropbox/Weecology/Benchmark/Figures/field_comparison.shp")

