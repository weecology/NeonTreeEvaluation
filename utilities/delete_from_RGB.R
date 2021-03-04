library(stringr)
rgb_dir<-"/Users/benweinstein/Documents/NeonTreeEvaluation/evaluation/RGB/"
fils<-list.files("/Users/benweinstein/Documents/NeonTreeEvaluation/evaluation/Hyperspectral/",full.names=T)
fils<-fils[!str_detect(fils,"competition")]
fils<-fils[!str_detect(fils,"unnamed")]
fils<-fils[!str_detect(fils,"las")]

for(x in fils){
  basename <- str_match(x,"(\\w+)_hyperspectral.tif")[,2]
  if(!file.exists(paste(rgb_dir,basename,".tif",sep=""))){
    file.remove(x)
  }
}
