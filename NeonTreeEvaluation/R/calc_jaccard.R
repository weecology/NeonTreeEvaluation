#' Collect jaccard statistic for ground truth and prediction polygons
#'
#' \code{calc_jaccard} finds the jaccard statistic for two input polygons, defined as the area of intersection over the area of union.
#' @param assignment A dataframe that connects ground truth and prediction poylgons see \code{\link{assign_trees}} SpatialPolygonDataFrame of length 1
#' @param ground_truth A SpatialPolygonDataFrame of ground truth polygons
#' @param prediction A SpatialPolygonDataFrame of ground truth polygons
#' @return dataframe of the jaccard overlap among polygon pairs
#' @export
calc_jaccard<-function(assignment,ground_truth,predictions){
  jaccard_stat<-list()
  for(i in 1:nrow(predictions)){
    polygon_row<-predictions[i,]
    y<-predictions[predictions$crown_id==polygon_row$crown_id,]

    #check assignment
    polygon_assignment <-assignment[assignment$prediction_id==polygon_row$crown_id,"crown_id"]
    if(length(polygon_assignment)==0){
      jaccard_stat[[i]]<-data.frame(crown_id=as.character(polygon_row$crown_id),prediction_id=NA,IoU=NA)
    } else{
    x<-ground_truth[ground_truth$crown_id==polygon_assignment,]
    #find interesection over union
    jaccard_stat[[i]]<-data.frame(crown_id=as.character(polygon_assignment),prediction_id=as.character(polygon_row$crown_id),IoU=IoU(x,y))
  }}

  statdf<-dplyr::bind_rows(jaccard_stat)
  return(statdf)
}
