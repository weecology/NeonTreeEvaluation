#' Find matches between predicted and ground truth tree based on maximum area of overlap.
#'
#' \code{assign_trees} implements the hungarian algorithm in \code{\link[clue]{solve_LSAP}} to match sets of trees
#' @param ground_truth A ground truth polygon in SpatialPolygonsDataFrame
#' @param prediction prediction polygons in SpatialPolygonsDataFrame
#' @return A data frame with the crown ID matched to the prediction ID.
#' @examples
#'
#' @export
assign_trees<-function(ground_truth,predictions){

  #Find overlap among polygons
  overlap<-polygon_overlap_all(ground_truth, predictions)

  #Create adjacency matrix
  adj_matrix_overlap<-reshape2::acast(overlap,crown_id ~ prediction_id)

  assignment<-clue::solve_LSAP(adj_matrix_overlap,maximum = T)
  assignmentdf<-data.frame(crown_id=rownames(adj_matrix_overlap),prediction_id=as.integer(assignment))
  return(assignmentdf)
}
