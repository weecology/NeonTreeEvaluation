#' Convert xml annotations into projected bounding boxes.
#' In order to plot the annotations, they need to be projected and overlayed on RGB data
#'
#' @param xml_data a dataframe returned from readTreeXML
#' @param raster_object a rgb raster::stack to overlay annotations
#' @return SpatialPolygons object of annotations
#' @import raster xml2
#' @export
#'
#'
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
