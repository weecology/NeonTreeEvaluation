#' Extract bounding box coordinates from SpatialPolygons object
#'
#' @param fil "Character" filename of the .xml file
#' @return a dataframe of tree annotations in the format xmin, xmax, ymin, ymax
#' @export
#'
extract_coordinates<-function(x){
  b<-bbox(x)
  data.frame(xmin=b[1,1],ymin=b[2,1],xmax=b[1,2],ymax=b[2,2])
}
