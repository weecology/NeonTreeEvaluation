library(stringr)
data_dir = "/Users/benweinstein/Documents/NeonTreeEvaluation/evaluation/"
rgb_plots<-list.files("/Users/benweinstein/Documents/NeonTreeEvaluation/evaluation/RGB", full.names = F)
#just get completed plots
rgb_plots<-rgb_plots[str_detect(rgb_plots,"2019|2018|2020")]
rgb_plots<-rgb_plots[!grepl("^2018*",rgb_plots)]
rgb_plots <- rgb_plots[str_detect(rgb_plots,"HARV")]

#get sites
for(x in rgb_plots){
  #get basename
  basename <- str_match(x,"(\\w+)_\\d+.tif")[,2]
  new_name <- str_match(x,"(\\w+).tif")[,2]

  #rename laz
  old_filename <- paste(data_dir,"LiDAR/",basename,"_2019.laz",sep="")
  new_filename <-paste(data_dir,"LiDAR/",new_name,".laz",sep="")
  file.rename(old_filename, new_filename)

  old_filename <- paste(data_dir,"CHM/",basename,"2019_CHM.tif",sep="")
  new_filename <-paste(data_dir,"CHM/",new_name,"_CHM.tif",sep="")
  file.rename(old_filename, new_filename)


  old_filename <- paste(data_dir,"Hyperspectral/",basename,"2019_hyperspectral.tif",sep="")
  new_filename <-paste(data_dir,"Hyperspectral/",new_name,"_hyperspectral.tif",sep="")
  file.rename(old_filename, new_filename)
}

#some of the older data is misnamed
f<-list.files(paste(data_dir,"CHM/",sep=""),full.names = T)
f<-f[str_detect(f,"2020")]

for(a in f){
  b<-str_match(a,"(\\w+).tif")[2]
  b<-str_split(b,"_")
  newbasename <- paste(b[[1]][1],b[[1]][2],b[[1]][4],b[[1]][3],sep="_")
  newbasename<-paste(newbasename,".tif",sep="")
  newname <- paste(paste(data_dir,"CHM/",sep=""), newbasename,sep="")
  file.rename(a,newname)
}
