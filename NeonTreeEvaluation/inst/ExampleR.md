---
title: "Loading the dataset in R"
author: "Ben Weinstein"
date: "2/1/2019"
output: 
  html_document: 
    keep_md: yes
editor_options: 
  chunk_output_type: console
---

How to read and view xml annotations from the NEONTreeEvaluation benchmark dataset



# LiDAR


```r
point_cloud<-readLAS("../SJER/plots/SJER_052.laz")
```
Tree annotations are stored in the UserData column. Each tree has a unique numeric ID


```r
plot(point_cloud)
plot(point_cloud,color="label")
tree_only<-lasfilter(point_cloud,!point_cloud@data$label==0)
plot(tree_only,color="label")
```

## Compute Height Model


```r
chm <- lidR::grid_canopy(point_cloud, res = 0.5, lidR::pitfree(c(0,2,5,10,15), c(0, 1.5)))
plot(chm)
```

![](ExampleR_files/figure-html/unnamed-chunk-4-1.png)<!-- -->

## Predict trees

Using the lidR R package, we can perform individual tree prediction. Below we demonstrate how to predict trees and format the data for evaluation against the benchmark annotations.


```r
ttops <- tree_detection(chm, lmf(4, 2))
point_cloud   <- lastrees(point_cloud, silva2016(chm, ttops,max_cr_factor = 0.9,exclusion = 0.4))
```

The lidR package adds predicted labels into the treeID column

```r
plot(point_cloud,color="treeID")
```

## Format predictions

The benchmark dataset evaluates annotations as bounding boxes, since LiDAR is only one of several ways to look at the task. Let's turn the point cloud annotations into boxes.


```r
bboxes<-tree_hulls(point_cloud,"bbox")
plotRGB(rgb)
plot(bboxes,add=T)
```

![](ExampleR_files/figure-html/unnamed-chunk-7-1.png)<!-- -->
