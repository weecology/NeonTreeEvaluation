#' Read tree annotations for a NEON site from a set of XML files
#'
#' @param siteID NEON site abbreviation (e.g. "HARV")
#' @return a dataframe of tree annotations in the format xmin, xmax, ymin, ymax
#' @export
#'
readTreeXML<-function(siteID){
  f<-list.files(siteID,pattern=".xml",full.names = T,recursive = T)
  dat<-bind_rows(lapply(f,xml_parse))
  return(dat)
}
