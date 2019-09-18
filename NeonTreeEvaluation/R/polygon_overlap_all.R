#' Find area of overlap among sets of polygons
#'
#' \code{convex_hull} is a wrapper function to iterate through a SpatialPolygonsDataFrame
#' @param pol A ground truth polygon
#' @param prediction prediction polygons
#' @return A data frame with the crown ID, the prediction ID and the area of overlap.
#' @examples
#'
#' @export

polygon_overlap<-function(pol,predictions){
  overlap_area<-c()
  for(x in 1:nrow(predictions)){
    pred_poly<-predictions[x,]
    intersect_poly<-suppressWarnings(raster::intersect(pol,pred_poly))
    if(!is.null(intersect_poly)){
      overlap_area[x]<-intersect_poly@polygons[[1]]@area
    } else{
      overlap_area[x]<-0
    }
  }
  data.frame(crown_id=pol@data$crown_id,prediction_id=predictions@data$treeID,area=overlap_area)
}

polygon_overlap_all<-function(ground_truth,predictions){
  results<-list()
  for(x in 1:nrow(ground_truth)){
    results[[x]]<-polygon_overlap(pol=ground_truth[x,],predictions=predictions)
  }
  return(dplyr::bind_rows(results))
}

