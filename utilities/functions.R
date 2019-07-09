## Utility functions to read rectlabel Tree XMLs into a dataframe
#Read all xml files
readTreeXML<-function(path){
  f<-list.files(path,pattern=".xml",full.names = T,recursive = T)
  dat<-bind_rows(lapply(f,parser))
  return(dat)
}

#Parse xml file to dataframe
parser<-function(fil){
  pg <- read_xml(fil)

  # get all the <record>s
  recs <- xml_find_all(pg, "//name")
  names <- trimws(xml_text(recs))

  recs <- xml_find_all(pg, "//xmin")

  # extract and clean all the columns
  xmin <- trimws(xml_text(recs))

  # get all the <record>s
  recs <- xml_find_all(pg, "//ymin")

  # extract and clean all the columns
  ymin <- trimws(xml_text(recs))

  # get all the <record>s
  recs <- xml_find_all(pg, "//ymax")

  # extract and clean all the columns
  ymax <- trimws(xml_text(recs))

  # get all the <record>s
  recs <- xml_find_all(pg, "//xmax")

  # extract and clean all the columns
  xmax <- trimws(xml_text(recs))

  recs <- xml_find_all(pg, "//filename")
  filename <- trimws(xml_text(recs))

  df<-data.frame(filename=filename,xmin=as.numeric(xmin)*0.1,xmax=as.numeric(xmax)*0.1,ymin=as.numeric(ymin)*0.1,ymax=as.numeric(ymax)*0.1,name=names)
  
  #characters not factors
  df$filename<-as.character(df$filename)
  df$name<-as.character(df$name)
  
  return(df)
}

#xml_data is a xml object returned by the parser above, raster_object is the projected RGB image
xml_to_spatial_polygons<-function(xml_data,raster_object){
  
  #Project 
  projection_extent<-extent(raster_object)
  
  projected_polygons<-list()
  for(x in 1:nrow(xml_data)){
    
    e<-extent( projection_extent@xmin + xml_data$xmin[x],
               projection_extent@xmin + xml_data$xmax[x], 
               (projection_extent@ymax - xml_data$ymax[x]),
               (projection_extent@ymax - xml_data$ymax[x]) + (xml_data$ymax[x] - xml_data$ymin[x]) )
    projected_polygons[[x]]<-as(e, 'SpatialPolygons')
    projected_polygons[[x]]@polygons[[1]]@ID<-as.character(x)
  }
  
  projected_polygons <- as(SpatialPolygons(lapply(projected_polygons,
                                            function(x) slot(x, "polygons")[[1]])),"SpatialPolygonsDataFrame")
  
  projected_polygons@data$crown_id=1:nrow(projected_polygons)
  
  proj4string(projected_polygons)<-projection(rgb)
  return(projected_polygons)
}
