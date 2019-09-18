#' Load and overlay ground truth annotations for single plot evaluation
#'
#' @param plot_name The name of plot as given by the filename (e.g "SJER_021.tif" -> SJER_021)
#' @param show Logical. Whether to show a plot of the ground truth data overlayed on the RGB image
#' @return SpatialPolygonsDataFrame of ground truth boxes
#' @export
#'
load_ground_truth<-function(plot_name,show=TRUE){

  #Load xml of annotations
  siteID = stringr::str_match(plot_name,"(\\w+)_")[,2]
  path_to_xml = paste("/Users/Ben/Documents/NeonTreeEvaluation/",siteID,"/annotations/",plot_name,".xml",sep="")
  if(!file.exists(path_to_xml)){
    print(paste("There are no annotations for file",path_to_xml,"skipping..."))
    return(NULL)
  }
  xmls <- xml_parse(path_to_xml)

  #load rgb
  path_to_rgb = paste("/Users/Ben/Documents/NeonTreeEvaluation/",siteID,"/plots/",plot_name,".tif",sep="")

  #Read RGB image as projected raster
  rgb<-raster::stack(path_to_rgb)

  #View one plot's annotations as polygons, project into UTM
  #copy project utm zone (epsg), xml has no native projection metadata
  ground_truth <- boxes_to_spatial_polygons(xmls,rgb)

  if(show){
    raster::plotRGB(rgb)
    plot(ground_truth,add=T)
  }
  return(ground_truth)
}

