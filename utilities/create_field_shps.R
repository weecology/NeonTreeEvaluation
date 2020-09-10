#create test data file
library(sf)
library(dplyr)
lookup<-read.csv("/Users/ben/Documents/NeonTreeEvaluation/utilities/benchmark_Sarah.csv")
OSBS_train<-read_sf("/Users/ben/Dropbox/Weecology/competition/train/ITC/train_OSBS.shp")
OSBS_test<-read_sf("/Users/ben/Dropbox/Weecology/competition/IDTREES_competition_test_v2/task2/ITC/test_OSBS.shp")

OSBS_train<-OSBS_train%>% inner_join(lookup, "indvdID") %>%  mutate(plotID = as.character(plotID))
OSBS_test<-OSBS_test %>% dplyr::select(-plotID) %>% inner_join(lookup, "indvdID") %>%  mutate(plotID = as.character(plotID))
OSBS<-do.call(rbind, list(OSBS_train,OSBS_test))
devtools::use_data(OSBS,overwrite = T)

MLBS_train<-read_sf("/Users/ben/Dropbox/Weecology/competition/train/ITC/train_MLBS.shp")
MLBS_test<-read_sf("/Users/ben/Dropbox/Weecology/competition/IDTREES_competition_test_v2/task2/ITC/test_MLBS.shp")
MLBS_train<-MLBS_train %>% inner_join(lookup, "indvdID") %>%  mutate(plotID = as.character(plotID))
MLBS_test<-MLBS_test %>% dplyr::select(-plotID) %>% inner_join(lookup, "indvdID") %>% mutate(plotID = as.character(plotID))
MLBS<-do.call(rbind, list(MLBS_train,MLBS_test))
devtools::use_data(MLBS,overwrite = T)

