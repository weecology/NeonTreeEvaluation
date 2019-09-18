#normalize lidar layers
library(lidR)
library(stringr)
library(TreeSegmentation)
laz_files<-list.files(pattern=".laz",recursive = T,full.names = T)
laz_files<-laz_files[str_detect(laz_files,"plots")]
for(f in laz_files){
  print(f)
  tile<-readLAS(f,"-drop_z_below 0")
  tile=ground_model(tile)
  #remove very high points
  tile<-lasfilter(tile,Z<50)
  writeLAS(tile,f)
  chm<-canopy_model(tile)
  plot(chm)
}