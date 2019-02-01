---
title: "Loading the dataset in R"
author: "Ben Weinstein"
date: "2/1/2019"
output: 
  html_document: 
    keep_md: yes
---

How to read and view xml annotations from the NEONTreeEvaluation benchmark dataset




```r
#Path to dataset
xmls<-readTreeXML(path="../")

#View one plot's annotations as polygons
xml_polygons <- xml_to_spatial_polygons(xmls[xmls$filename %in% "TEAK_062.tif",])
plot(xml_polygons)
```

![](ExampleR_files/figure-html/unnamed-chunk-1-1.png)<!-- -->
# Overlay on imagery

# Open LAS

# View annotations
