#' Convert xml annotations into projected bounding boxes.
#' In order to plot the annotations, they need to be projected and overlayed on RGB boxes
#'
#' @param boxes a boxesframe with xmin, xmax, ymin, ymax columns. Each row is a tree bounding box
#' @param raster_object a rgb raster::stack to overlay annotations
#' @return SpatialPolygons object of annotations
#' @export
#'
#'
#boxes is a xml object returned by the parser above, raster_object is the projected RGB image
boxes_to_spatial_polygons<-function(boxes,raster_object){

  #scale by pixel resolution
  pixel_size = raster::res(raster_object)[1]
  boxes$xmin = boxes$xmin * pixel_size
  boxes$xmax = boxes$xmax * pixel_size
  boxes$ymin = boxes$ymin* pixel_size
  boxes$ymax = boxes$ymax * pixel_size

  #Project
  projection_extent<-raster::extent(raster_object)

  projected_polygons<-list()
  for(x in 1:nrow(boxes)){

    e<-raster::extent( projection_extent@xmin + boxes$xmin[x],
               projection_extent@xmin + boxes$xmax[x],
               (projection_extent@ymax - boxes$ymax[x]),
               (projection_extent@ymax - boxes$ymax[x]) + (boxes$ymax[x] - boxes$ymin[x]) )
    projected_polygons[[x]]<-as(e, 'SpatialPolygons')
    projected_polygons[[x]]@polygons[[1]]@ID<-as.character(x)
  }

  projected_polygons <- as(sp::SpatialPolygons(lapply(projected_polygons,
                                                  function(x) slot(x, "polygons")[[1]])),"SpatialPolygonsDataFrame")

  projected_polygons@data$crown_id=1:nrow(projected_polygons)
  sp::proj4string(projected_polygons)<-raster::projection(raster_object)
  return(projected_polygons)
}
