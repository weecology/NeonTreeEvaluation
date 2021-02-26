library(stringr)
data_dir<-"/Users/benweinstein/Downloads/temporal/2018/"
fils<-list.files(paste(data_dir,"Camera/",sep=""),full.names = T)

year = "2018"

#get sites
for(x in fils){

  new_name = str_replace(x, ".tif", paste("_",year,".tif",sep=""))
  file.rename(x, new_name)

  #get basename
  basename <- str_match(x,"(\\w+).tif")[,2]

  #rename laz
  old_filename <- paste(data_dir,"LiDAR/",basename,".laz",sep="")
  new_filename <-paste(data_dir,"LiDAR/",basename,"_",year,".laz",sep="")
  file.rename(old_filename, new_filename)

  old_filename <- paste(data_dir,"CHM/",basename,"_CHM.tif",sep="")
  new_filename <-paste(data_dir,"CHM/",basename,"_",year,"_CHM.tif",sep="")
  file.rename(old_filename, new_filename)


  old_filename <- paste(data_dir,"Hyperspectral/",basename,"_hyperspectral.tif",sep="")
  new_filename <-paste(data_dir,"Hyperspectral/",basename,"_",year,"_hyperspectral.tif",sep="")
  file.rename(old_filename, new_filename)
}
