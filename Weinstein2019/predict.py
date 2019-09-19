## Prediction of Trees from local model
import cv2
import matplotlib.pyplot as plt  
import pandas as pd
import glob
import os
import utilities

if __name__=="__main__":
    config = utilities.read_config()  
    model = utilities.read_model(config["model_path"], config) 
    
    #gather images with annotations images
    files = glob.glob("../**/**/*.tif")
    
    #rgb only
    files = [x for x in files if not "hyperspectral" in x]
    files = [x for x in files if not "depth" in x]
    files = [x for x in files if not "training" in x]
    files = [x for x in files if not "false_color" in x]
    
    #which images have annotations
    images_with_annotations = glob.glob("../../*/annotations/*")
    images_with_annotations = [os.path.basename(x) for x in images_with_annotations]
    images_with_annotations = [os.path.splitext(x)[0] for x in images_with_annotations]
    
    #filter rgb images
    files = [x for x in files if any(w in x for w in images_with_annotations)]
    
    boxes_output = [ ]
    for f in files:
        print(f)
        #predict plot image
        boxes = utilities.predict_image(image_path=f, model=model, return_plot=False)
        box_df = pd.DataFrame(boxes)
        
        #plot name
        plot_name = os.path.splitext(os.path.basename(f))[0]
        box_df["plot_name"] = plot_name
        boxes_output.append(box_df)
        
    boxes_output = pd.concat(boxes_output)
    
    #name columns and add to submissions folder
    boxes_output.columns = ["xmin","ymin","xmax","ymax","plot_name"]
    boxes_output = boxes_output.reindex(columns= ["plot_name","xmin","ymin","xmax","ymax"])    
    boxes_output.to_csv("../submissions/Weinstein2019.csv",index=False)

    