#DeepForest 19 site model
import deepforest

##Pretrain deepforest on Silva annotations
deepforest_model = deepforest.deepforest()
deepforest_model.train("pretraining/crops/pretraining_annotations.csv")
    
#retrain model based on hand annotation crops, assign the weights from pretraining model
deepforest_model.training_model.save_weights("snapshots/pretraining_weights.h5")
deepforest_model.config["weights"] = "snapshots/pretraining_weights.h5"
deepforest_model.train("hand_annotations/crops/hand_annotations.csv")