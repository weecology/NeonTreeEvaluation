#create test data file
library(sf)
library(dplyr)
lookup<-read.csv("/Users/ben/Documents/NeonTreeEvaluation/utilities/field_lookup.csv")
OSBS_test<-read_sf("/Users/ben/Dropbox/Weecology/competition/IDTREES_competition_test_v2/task2/ITC/test_OSBS.shp") %>% select(indvdID)
OSBS_ground<-read.csv("/Users/ben/Dropbox/Weecology/Benchmark/OSBS_ground.csv")
OSBS_sf<-st_as_sfc(OSBS_ground$WKT)
OSBS_sf<-st_sf(geometry=OSBS_sf) 
OSBS_sf$indvdID<-OSBS_ground$id
st_crs(OSBS_sf)<-st_crs(OSBS_test)

OSBS<-do.call(rbind, list(OSBS_test, OSBS_sf))
devtools::use_data(OSBS,overwrite = T)

MLBS_test<-read_sf("/Users/ben/Dropbox/Weecology/competition/IDTREES_competition_test_v2/task2/ITC/test_MLBS.shp") %>% select(indvdID)
MLBS_ground<-read.csv("/Users/ben/Dropbox/Weecology/Benchmark/MLBS_ground.csv")
MLBS_sf<-st_as_sfc(MLBS_ground$WKT)
MLBS_sf<-st_sf(geometry=MLBS_sf) 
MLBS_sf$indvdID<-MLBS_ground$id
st_crs(MLBS_sf)<-st_crs(MLBS_test)

MLBS<-do.call(rbind, list(MLBS_test, MLBS_sf))
devtools::use_data(MLBS,overwrite = T)


crowns<-do.call(rbind,list(MLBS,OSBS))
devtools::use_data(MLBS,overwrite = T)

devtools::use_data(crowns,overwrite = T)

write_sf(crowns, "/Users/ben/Dropbox/Weecology/Benchmark/field_crowns.shp")

