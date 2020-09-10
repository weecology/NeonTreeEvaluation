library(stringr)
library(raster)
a<-list.files("/Users/ben/Downloads/competition/sarah_test_plots/mage", full.names = T)
for(i in a){
  img = stack(i)
  x = str_replace(i,"(\\w+).tif",paste("\\1_competition"))
  writeRaster(img,x,datatype='INT1U',overwrite=T)
}

a<-list.files("/Users/ben/Downloads/competition/sarah_test_plots/hsi", full.names = T)
for(i in a){
  x = str_replace(i,"(\\w+).tif",paste("\\1_competition_hyperspectral"))
  file.rename(i, x)
}

a<-list.files("/Users/ben/Downloads/competition/sarah_test_plots/las", full.names = T)
for(i in a){
  x = str_replace(i,"las/(\\w+).tif",paste("las/\\1_competition"))
  file.rename(i, x)
}

a<-list.files("/Users/ben/Downloads/competition/sarah_test_plots/_chm", full.names = T)
for(i in a){
  x = str_replace(i,"_chm/(\\w+).tif",paste("_chm/\\1_competition"))
  file.rename(i, x)
}


