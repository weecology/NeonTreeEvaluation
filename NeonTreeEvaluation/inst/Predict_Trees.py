## Prediction of Trees from local model
import utilities
import cv2
import matplotlib.pyplot as plt  
import pandas as pd
import glob

class Tree_Model:
    
    def __init__(self, model_path):
        self.model_path = model_path
        
        #read and load models
        self.read_config()
        self.load_model()
    
    def read_config(self):
        self.config = utilities.read_config()
        
    def load_model(self):
        self.model = utilities.read_model(self.model_path, self.config)
        self.model._make_predict_function()
        
    def predict_image(self, image):
        print("Image shape is {}".format(image.shape))
        prediction = utilities.predict_image(model= self.model,raw_image= image)
        
        #return in RGB order
        prediction = prediction[:,:,::-1]
        
        return prediction

if __name__=="__main__":
    config = utilities.read_config()  
    model = utilities.read_model(config["model_path"], config) 
    
    #gather images
    glob.glob("../../**/**/*.tif")
    
    csv_path = utilities.prediction_wrapper(image_path="/Users/ben/Downloads/gettyimages-908-47-640x640.jpg")
    image = predict_image(image_path="/Users/ben/Downloads/gettyimages-908-47-640x640.jpg",model=model,return_plot=True)

#test_predict()
raw_image = cv2.imread("/Users/ben/Downloads/gettyimages-908-47-640x640.jpg")
print("raw image shape".format(raw_image.shape))
boxes = pd.read_csv(csv_path)
print(boxes)
    