#Rename and filter the HSI bands from the competition to match the rest of the benchmark data
library(stringr)
library(raster)

f<-list.files("/Users/ben/Dropbox/Weecology/competition/IDTREES_competition_train/RemoteSensing/HSI",full.names=T)
save_dir = "/Users/ben/Documents/NeonTreeEvaluation/evaluation/Hyperspectral/"
for(i in f){
  r<-stack(i)
}
