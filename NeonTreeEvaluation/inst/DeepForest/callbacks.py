'''
Callback for evaluation. Modified in part from keras-retinanet by FizyR. 
'''
import keras
from .evaluation import neonRecall
from .evalmAP import evaluate         

class Evaluate(keras.callbacks.Callback):
    """ Evaluation callback for arbitrary datasets.
    """

    def __init__(self, generator, iou_threshold=0.5, score_threshold=0.05, max_detections=300, suppression_threshold=0.2,save_path=None, weighted_average=False, verbose=1,experiment=None,DeepForest_config=None):
        """ Evaluate a given dataset using a given model at the end of every epoch during training.

        # Arguments
            generator       : The generator that represents the dataset to evaluate.
            iou_threshold   : The threshold used to consider when a detection is positive or negative.
            score_threshold : The score confidence threshold to use for detections.
            max_detections  : The maximum number of detections to use per image.
            suppression_threshold:  Percent overlap allowed among boxes
            save_path       : The path to save images with visualized detections to.
            verbose         : Set the verbosity level, by default this is set to 1.
            Experiment   : Comet ml experiment for online logging
        """
        self.generator       = generator
        self.iou_threshold   = iou_threshold
        self.score_threshold = score_threshold
        self.max_detections  = max_detections
        self.suppression_threshold=suppression_threshold
        self.save_path       = save_path
        self.weighted_average = weighted_average
        self.verbose         = verbose
        self.experiment = experiment
        self.DeepForest_config = DeepForest_config

        super(Evaluate, self).__init__()

    def on_epoch_end(self, epoch, logs=None):
        logs = logs or {}

        # run evaluation
        average_precisions = evaluate(
            self.generator,
            self.model,
            iou_threshold=self.iou_threshold,
            score_threshold=self.score_threshold,
            max_detections=self.max_detections,
            save_path=self.save_path,
            experiment=self.experiment
        )

        # compute per class average precision
        total_instances = []
        precisions = []
        for label, (average_precision, num_annotations ) in average_precisions.items():
            if self.verbose == 1:
                print('{:.0f} instances of class'.format(num_annotations),
                      self.generator.label_to_name(label), 'with average precision: {:.3f}'.format(average_precision))
            total_instances.append(num_annotations)
            precisions.append(average_precision)
        if self.weighted_average:
            self.mean_ap = sum([a * b for a, b in zip(total_instances, precisions)]) / sum(total_instances)
        else:
            self.mean_ap = sum(precisions) / sum(x > 0 for x in total_instances)
        
        logs['mAP'] = self.mean_ap

        if self.verbose == 1:
            print('mAP: {:.3f}'.format(self.mean_ap))             
        
        self.experiment.log_metric("mAP", self.mean_ap)       
            
# Neon Recall 
class recallCallback(keras.callbacks.Callback):
    """ Evaluation callback for NEON stem maps
    """
    def __init__(self, generator=None, score_threshold=0.05, max_detections=300, suppression_threshold=0.2,save_path=None, weighted_average=False, verbose=1,experiment=None, sites=None):
        """ Evaluate a given dataset using a given model at the end of every epoch during training.

        # Arguments
            generator       : The generator that represents the dataset to evaluate.
            iou_threshold   : The threshold used to consider when a detection is positive or negative.
            score_threshold : The score confidence threshold to use for detections.
            max_detections  : The maximum number of detections to use per image.
            suppression_threshold:  Percent overlap allowed among boxes
            save_path       : The path to save images with visualized detections to.
            verbose         : Set the verbosity level, by default this is set to 1.
            Experiment   : Comet ml experiment for online logging
        """
        self.generator       = generator
        self.score_threshold = score_threshold
        self.max_detections  = max_detections
        self.suppression_threshold=suppression_threshold
        self.save_path       = save_path
        self.weighted_average = weighted_average
        self.verbose         = verbose
        self.experiment = experiment
        self.sites = sites

        super(recallCallback, self).__init__()
        
    def on_epoch_end(self, epoch, logs=None):
        logs = logs or {}
        
        recall=neonRecall(
            self.sites,
            self.generator,
            self.model,            
            score_threshold=self.score_threshold,
            save_path=self.save_path,
            max_detections=self.max_detections,
            experiment=self.experiment,
        )
        
        print("Recall is {}".format(recall))
        
        self.experiment.log_metric("Recall", recall)       

#Hand annotated mAP
class NEONmAP(keras.callbacks.Callback):
    """ Evaluation callback for arbitrary datasets.
    """

    def __init__(self, generator, iou_threshold=0.5, score_threshold=0.05, max_detections=300, save_path=None, weighted_average=False, verbose=1, experiment=None, DeepForest_config=None):
        """ Evaluate a given dataset using a given model at the end of every epoch during training.

        # Arguments
            generator       : The generator that represents the dataset to evaluate.
            iou_threshold   : The threshold used to consider when a detection is positive or negative.
            score_threshold : The score confidence threshold to use for detections.
            max_detections  : The maximum number of detections to use per image.
            save_path       : The path to save images with visualized detections to.
            verbose         : Set the verbosity level, by default this is set to 1.
            Experiment   : Comet ml experiment for online logging
        """
        self.generator       = generator
        self.iou_threshold   = iou_threshold
        self.score_threshold = score_threshold
        self.max_detections  = max_detections
        self.save_path       = save_path
        self.weighted_average = weighted_average
        self.verbose         = verbose
        self.experiment = experiment
        self.DeepForest_config = DeepForest_config

        super(NEONmAP, self).__init__()
            
    def on_epoch_end(self, epoch, logs=None):
        logs = logs or {}

        print("computing NEON mAP scores")
        
        # run evaluation
        average_precisions = evaluate(
            self.generator,
            self.model,
            iou_threshold=self.iou_threshold,
            score_threshold=self.score_threshold,
            max_detections=self.max_detections,
            save_path=self.save_path,
            experiment=self.experiment
        )

        # print evaluation
        # compute per class average precision
        total_instances = []
        precisions = []
        for label, (average_precision, num_annotations ) in average_precisions.items():
            if self.verbose == 1:
                print('{:.0f} instances of class'.format(num_annotations),
                      self.generator.label_to_name(label), 'with average precision: {:.3f}'.format(average_precision))
            total_instances.append(num_annotations)
            precisions.append(average_precision)
        if self.weighted_average:
            self.NEON_map = sum([a * b for a, b in zip(total_instances, precisions)]) / sum(total_instances)
        else:
            self.NEON_map = sum(precisions) / sum(x > 0 for x in total_instances)
        
        logs['NEON_mAP'] = self.NEON_map
        
        print('Neon mAP: {:.3f}'.format(self.NEON_map))
        self.experiment.log_metric("Neon mAP", self.NEON_map)          
        
class shuffle_inputs(keras.callbacks.Callback):
    """Randomize order of tiles and windows
    """

    def __init__(self, generator):
        """ 
        # Arguments
            generator       : The generator that represents the dataset to evaluate.
        """
        self.generator       = generator
        super(shuffle_inputs, self).__init__()
        
    #Before epoch, randomize tile order
    def on_epoch_begin(self,epoch,logs=None):
            self.generator.image_data, self.generator.image_names =self.generator.define_groups(self.generator.windowdf,shuffle=True)
            self.generator.group_images()
