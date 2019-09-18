#' Parse xml tree annotations from an XML file
#'
#' @param fil "Character" filename of the .xml file
#' @return a dataframe of tree annotations in the format xmin, xmax, ymin, ymax
#' @export
#' @import xml2
#'
#Parse xml file to dataframe
xml_parse<-function(fil){
  pg <- read_xml(fil)

  # get all the <record>s
  recs <- xml_find_all(pg, "//name")
  names <- trimws(xml_text(recs))

  recs <- xml_find_all(pg, "//xmin")

  # extract and clean all the columns
  xmin <- trimws(xml_text(recs))

  # get all the <record>s
  recs <- xml_find_all(pg, "//ymin")

  # extract and clean all the columns
  ymin <- trimws(xml_text(recs))

  # get all the <record>s
  recs <- xml_find_all(pg, "//ymax")

  # extract and clean all the columns
  ymax <- trimws(xml_text(recs))

  # get all the <record>s
  recs <- xml_find_all(pg, "//xmax")

  # extract and clean all the columns
  xmax <- trimws(xml_text(recs))

  recs <- xml_find_all(pg, "//filename")
  filename <- trimws(xml_text(recs))

  df<-data.frame(filename=filename,xmin=as.numeric(xmin),xmax=as.numeric(xmax),ymin=as.numeric(ymin),ymax=as.numeric(ymax),name=names)

  #characters not factors
  df$filename<-as.character(df$filename)
  df$name<-as.character(df$name)

  return(df)
}
