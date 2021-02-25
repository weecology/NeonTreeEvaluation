#Gather and label NEON polygons.
#Download and unzip NEON trait sampling zip
library(dplyr)
library(stringr)
library(sf)

NEON_dir = "/Users/benweinstein/Downloads/NEON_traits-foliar/"
site_folders <- list.dirs(NEON_dir,recursive = F)
#ignore itself
site_folders = site_folders[2:length(site_folders)]

results<-list()
for(site_folder in site_folders){
  #Get download link to shapefile
  #make a dir to hold out 
  sites_files <-list.files(site_folder,full.names=T)  
  shp_filename<-sites_files[str_detect(sites_files,"shapefile")]
  if(!length(shp_filename)==0){
    shapefile_csv<-read.csv(shp_filename)
  } else{
    next
  }
  savedir = paste(NEON_dir,shapefile_csv$siteID,sep="")
  dir.create(savedir)
  download.file(shapefile_csv$downloadFileUrl, destfile = paste(savedir,"/polygons.zip",sep=""))
  
  #Open downloaded shapefiles
  unzip(paste(savedir,"/polygons.zip",sep=""), exdir = paste(savedir,"/polygons/",sep=""))
  shp<-list.files(paste(savedir,"/polygons/",sep=""),pattern=".shp",recursive = T,full.names = T)
  shp <- read_sf(shp)
  
  #Project to lat long?
  shp <- st_transform(shp,4326)
  shp$crownPolygonID<-shp$crownPolyg
  #Load sampling information to connect IDs
  field_data<-read.csv(sites_files[str_detect(sites_files,"fieldData")])
  shp<-merge(shp,field_data,"crownPolygonID")
  
  #formatting
  shp$tagID<-as.character(shp$tagID)
  shp <- shp[colnames(shp) %in% c("crownPolygonID","plotID","siteID","taxonID","canopyPosition")]
  results[[shapefile_csv$siteID]]<-shp
}

results <- bind_rows(results)
st_write(results,paste(NEON_dir,"/NEON_trait_polygons.shp",sep=""),append = F)
