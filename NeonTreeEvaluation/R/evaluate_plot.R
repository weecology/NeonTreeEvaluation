#' Compute evaluation statistics for one plot
#'
#' @param submission A five column dataframe in the order plot_name, xmin, xmax, ymin, ymax. Each row is a predicted bounding box.
#' @return recall and precision scores for the plot
#' @export
#'
evaluate_plot<-function(submission, show=TRUE){

  #find ground truth file
  plot_name <- unique(submission$plot_name)
  if(!length(plot_name)==1){
    stop(paste("There are",length(plot_name),"plot names. Please submit one plot of annotations to this function"))
  }

  ground_truth<-load_ground_truth(plot_name,show = FALSE)
  if(is.null(ground_truth)){
    return(data.frame(NULL))
  }

  #Read RGB image as projected raster
  siteID = stringr::str_match(plot_name,"(\\w+)_")[,2]

  #TODO deal with relative paths
  path_to_rgb = paste("/Users/Ben/Documents/NeonTreeEvaluation/",siteID,"/plots/",plot_name,".tif",sep="")
  print(path_to_rgb)
  rgb<-raster::stack(path_to_rgb)

  #project boxes
  predictions <- boxes_to_spatial_polygons(submission,rgb)

  if(show){
    raster::plotRGB(rgb)
    sp::plot(ground_truth,border="black",add=T)
    sp::plot(predictions,border="red",add=T)
  }

  #Create spatial polygons objects
  result<-compute_precision_recall(ground_truth,predictions)
  return(result)
}

