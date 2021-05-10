library(sf)
library(NeonTreeEvaluation)

lst <- lapply(1:nrow(submission), function(x){
  ## create a matrix of coordinates that also 'close' the polygon
  res <- matrix(c(submission[x, 'xmin'], submission[x, 'ymin'],
                  submission[x, 'xmin'], submission[x, 'ymax'],
                  submission[x, 'xmax'], submission[x, 'ymax'],
                  submission[x, 'xmax'], submission[x, 'ymin'],
                  submission[x, 'xmin'], submission[x, 'ymin'])  ## need to close the polygon
                , ncol =2, byrow = T
  )
  ## create polygon objects
  st_polygon(list(res))

})


sfdf <- st_sf(submission, st_sfc(lst))
plot(sfdf[1,"label"])
write_sf(sfdf, "/Users/Ben/Documents/neontreeevaluation_python/data/submission.shp")
submission_polygons<-sfdf
use_data(submission_polygons,overwrite = T )
