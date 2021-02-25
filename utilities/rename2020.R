library(stringr)
images<-list.files("/Users/benweinstein/Downloads/temporal/Camera/",full.names = T)
for(x in images){
  plotid<-str_match(x,"(\\w+).tif")[,2]
  # new_name<-str_replace(x,plotid,replacement = paste(plotid,"_2020",sep=""))
  # file.rename(x,new_name)
  
  #Lookup LiDAR
  lidar_file<-paste("/Users/benweinstein/Downloads/temporal/CHM/",plotid,"_CHM.tif",sep="")
  new_lidar_file<-paste("/Users/benweinstein/Downloads/temporal/CHM/",plotid,"_CHM_2020.tif",sep="")
  file.rename(lidar_file,new_lidar_file)
  # 
  # lidar_file<-paste("/Users/benweinstein/Downloads/temporal/Lidar/",plotid,".laz",sep="")
  # new_lidar_file<-paste("/Users/benweinstein/Downloads/temporal/Lidar/",plotid,"_2020.laz",sep="")
  # file.rename(lidar_file,new_lidar_file)
  # 
  # lidar_file<-paste("/Users/benweinstein/Downloads/temporal/hyperspectral/",plotid,"_hyperspectral.tif",sep="")
  # new_lidar_file<-paste("/Users/benweinstein/Downloads/temporal/hyperspectral/",plotid,"_hyperspectral_2020.tif",sep="")
  # file.rename(lidar_file,new_lidar_file)
}

#remove any non 2020
fils<-list.files("/Users/benweinstein/Downloads/temporal/",full.names = T,recursive = T)
for(f in fils){
  if(!str_detect(f,"2020")){
    file.remove(f)
  }
}
