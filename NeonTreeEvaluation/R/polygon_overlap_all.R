#' Find area of overlap among all sets of polygons
#'
#' @param ground_truth A ground truth polygon
#' @param predictions prediction polygons
#' @return A data frame with the crown ID, the prediction ID and the area of overlap.
#' @export

polygon_overlap_all<-function(ground_truth,predictions){
  results<-list()
  for(x in 1:nrow(ground_truth)){
    results[[x]]<-polygon_overlap(pol=ground_truth[x,],predictions=predictions)
  }
  return(dplyr::bind_rows(results))
}
