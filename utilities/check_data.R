#Check data, each plot should have an RGB, HSI, LiDAR and CHM file.
library(NeonTreeEvaluation)
library(stringr)

rgb<-list_rgb()
for(r in rgb){
  #get plot name
  plot_name <- str_match(r, "(\\w+).tif")[,2]
  #CHM
  CHM <- file.exists(get_data(plot_name, "chm"))
  if(!CHM){paste(plot_name, "missing CHM")}

  hsi <- file.exists(get_data(plot_name, "hyperspectral"))
  if(!hsi){paste(plot_name, "missing hsi")}

  lidar <- file.exists(get_data(plot_name, "lidar"))
  if(!lidar){paste(plot_name, "missing lidar")}
}

#check annotations
annotations <-list_annotations()

for(x in annotations){
  xml<-get_data(x,"annotations")
  dataframe<-xml_parse(xml)
  plotID<-unique(str_match(dataframe$filename,"(\\w+).tif")[,2])
  if(!plotID==x){print(x)}
  if(!file.exists(get_data(plotID,"rgb"))){print(x)}
}

