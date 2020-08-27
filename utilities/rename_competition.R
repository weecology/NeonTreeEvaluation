library(stringr)
library(raster)
a<-list.files("/Users/ben/Documents/NeonTreeEvaluation/evaluation/RGB/",pattern = "competition")
f<-a[stringr::str_detect(a,"MLBS")]

for(i in f){
  img = stack(i)
  writeRaster(img,i,datatype='INT1U',overwrite=T)
}
