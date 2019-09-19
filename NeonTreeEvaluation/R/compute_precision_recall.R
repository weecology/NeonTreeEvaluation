#' Compute precision and recall statistics between predicted tree boxes and ground truth data
#' @details The numeric identity of the crown is stored in a column named crown_ID. An error will be raised if this column does not exist.
#' @param ground_truth SpatialPolygonDataFrame of ground truth polygons
#' @param predictions SpatialPolygonDataFrame of prediction polygons
#' @param threshold Intersection over Union threshold. default is 0.5
#' @return recall and precision scores for the plot
#' @export
#'
compute_precision_recall<-function(ground_truth,predictions,threshold=0.5){

  #check for
  if(!"crown_id" %in% colnames(predictions@data)){
    stop("Crown IDs need to be stored in a numeric index named 'crown_id'")
  }

  assignment<-assign_trees(ground_truth=ground_truth,predictions=predictions)
  statdf<-calc_jaccard(assignment=assignment,ground_truth = ground_truth, predictions=predictions)
  true_positives = statdf$IoU > threshold
  recall <- round(sum(true_positives,na.rm=T)/nrow(ground_truth),3)
  precision <- round(sum(true_positives,na.rm=T)/nrow(predictions),3)
  data.frame(recall,precision)
}

