#' Parse xml tree annotations from an XML file
#'
#' @param ground_truth SpatialPolygonDataFrame of ground truth polygons
#' @param predictions SpatialPolygonDataFrame of prediction polygons
#' @param threshold Intersection over Union threshold. default is 0.5
#' @return recall and precision scores for the plot
#' @export
#'
evaluate_plot<-function(predictions){

  #find ground truth file
  ground_truth<-load_ground_truth()

  #Create spatial polygons objects

  compute_precision_recall(ground_truth,predicted_polygons)
}

