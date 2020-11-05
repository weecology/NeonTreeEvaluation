library(sf)
library(dplyr)
OSBS<-read_sf("/Users/ben/Dropbox/Weecology/Benchmark/Benchmark_polygons/OSBS_field_polygons_2019_final.shp")
MLBS<-read_sf("/Users/ben/Dropbox/Weecology/Benchmark/Benchmark_polygons/MLBS_field_polygons_2018_final.shp")
crown_polygons<-do.call(rbind,list(MLBS,OSBS))

lookup_table<-read.csv("/Users/ben/Documents/NeonTreeEvaluation/utilities/field_lookup.csv")
lookup = sf::st_as_sf(lookup_table, coords=c( "plotEasting", "plotNorthing" ), crs=32617)
lookup = sf::st_buffer(lookup, 20) %>% select(plotID, siteID, utmZone)
lookup["plotEasting"] = lookup_table["plotEasting"]
lookup["plotNorthing"] = lookup_table["plotNorthing"]

get_field_plots = sf::st_join(crown_polygons, lookup, left = T, join = st_within) %>% unique
sum(is.na(get_field_plots$plotID))

#automatically assign plot only for crowns previously not in data
get_missing = get_field_plots %>% filter(!indvdID %in% lookup_table$indvdID) %>%
  group_by(indvdID) %>% slice(1)
get_not_missing = left_join(lookup_table, get_field_plots)
get_not_missing = get_not_missing %>% select(colnames(get_missing))
final_set = rbind.data.frame(get_missing, get_not_missing)

write_sf(final_set, "/Users/ben/Dropbox/Weecology/Benchmark/Benchmark_polygons/polygons.shp")

crown_polygons<-final_set %>% ungroup()
devtools::use_data(crown_polygons,overwrite = T)
