#create test data file
library(sf)
shps<-list.files("/Users/ben/Dropbox/Weecology/competition/IDTREES_competition_test 2/task2/ITC/", pattern=".shp", full.names = T)
shps<-lapply(shps,read_sf)
do.call(rbind, shps)
