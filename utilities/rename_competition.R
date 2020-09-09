library(stringr)
library(raster)
a<-list.files("/Users/ben/Dropbox/Weecology/competition/mage/", full.names = T)
#f<-a[stringr::str_detect(a,"MLBS")]

for(i in a){
  img = stack(i)
  i = str_replace(i,"(\\w+).tif",paste("\\1_competition.tif"))
  writeRaster(img,i,datatype='INT1U',overwrite=T)
}

a<-list.files("/Users/ben/Dropbox/Weecology/competition/hsi/", full.names = T)

for(i in a){
  img = stack(i)
  i = str_replace(i,"(\\w+).tif",paste("\\1_hyperspectral_competition.tif"))
  writeRaster(img,i,overwrite=T)
}

a<-list.files("/Users/ben/Dropbox/Weecology/competition/hsi/", full.names = T)
for(i in a){
  x = str_replace(i,"(\\w+).tif",paste("\\1_competition_hyperspectral.tif"))
  file.rename(i, x)
}

a<-list.files("/Users/ben/Dropbox/Weecology/competition/las", full.names = T)
for(i in a){
  x = str_replace(i,"competition/las/(\\w+).las",paste("competition/las/\\1_competition.las"))
  file.rename(i, x)
}

a<-list.files("/Users/ben/Dropbox/Weecology/competition/_chm", full.names = T)
for(i in a){
  x = str_replace(i,"competition/_chm/(\\w+).tif",paste("competition/_chm/\\1_competition.tif"))
  file.rename(i, x)
}

a<-list.files("/Users/ben/Dropbox/Weecology/competition/_chm", full.names = T)
for(i in a){
  x = str_replace(i,"(\\w+).tif","\\1_CHM.tif")
  file.rename(i, x)
}

