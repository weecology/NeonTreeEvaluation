#create test data file
library(sf)
#OSBS_train<-read_sf("/Users/ben/Dropbox/Weecology/competition/train/ITC/train_OSBS.shp")
OSBS<-read_sf("/Users/ben/Dropbox/Weecology/competition/IDTREES_competition_test_v2/task2/ITC/test_OSBS.shp")

#Lookup plot ID spatially.TODO

#OSBS<-do.call(rbind, list(OSBS_train,OSBS_test))
OSBS<-OSBS_test
devtools::use_data(OSBS,overwrite = T)

MLBS<-read_sf("/Users/ben/Dropbox/Weecology/competition/IDTREES_competition_test_v2/task2/ITC/test_MLBS.shp")

#Lookup plot ID spatially.
#OSBS<-do.call(rbind, list(OSBS_train,OSBS_test))
devtools::use_data(MLBS,overwrite = T)
