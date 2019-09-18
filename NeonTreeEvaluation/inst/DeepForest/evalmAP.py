"""
Evaluation of mAP script - soruce modified from keras-retinanet by FizyR
"""

from __future__ import print_function

from keras_retinanet.utils.anchors import compute_overlap
from keras_retinanet.utils.visualization import draw_detections, draw_annotations

import keras
import numpy as np
import os
import cv2
from matplotlib import pyplot as plt
from DeepForest import postprocessing, Lidar
import copy

def _compute_ap(recall, precision):
    """ Compute the average precision, given the recall and precision curves.

    Code originally from https://github.com/rbgirshick/py-faster-rcnn.

    # Arguments
        recall:    The recall curve (list).
        precision: The precision curve (list).
    # Returns
        The average precision as computed in py-faster-rcnn.
    """
    # correct AP calculation
    # first append sentinel values at the end
    mrec = np.concatenate(([0.], recall, [1.]))
    mpre = np.concatenate(([0.], precision, [0.]))

    # compute the precision envelope
    for i in range(mpre.size - 1, 0, -1):
        mpre[i - 1] = np.maximum(mpre[i - 1], mpre[i])

    # to calculate area under PR curve, look for points
    # where X axis (recall) changes value
    i = np.where(mrec[1:] != mrec[:-1])[0]

    # and sum (\Delta recall) * prec
    ap = np.sum((mrec[i + 1] - mrec[i]) * mpre[i + 1])
    return ap


def _get_detections(generator, model, score_threshold=0.05, max_detections=300, save_path=None, experiment=None, postprocess= False):
    """ Get the detections from the model using the generator.

    The result is a list of lists such that the size is:
        all_detections[num_images][num_classes] = detections[num_detections, 4 + num_classes]

    # Arguments
        generator       : The generator used to run images through the model.
        model           : The model to run on the images.
        score_threshold : The score confidence threshold to use.
        max_detections  : The maximum number of detections to use per image.
        save_path       : The path to save the images with visualized detections to.
        experiment    : Comet ML experiment
    # Returns
        A list of lists containing the detections for each image in the generator.
    """
    all_detections = [[None for i in range(generator.num_classes())] for j in range(generator.size())]

    for i in range(generator.size()):
        raw_image    = generator.load_image(i)        
        plot_image = copy.deepcopy(raw_image)

        #Format name and save
        image_name = generator.image_names[i]        
        row = generator.image_data[image_name]             
        lfname = os.path.splitext(row["tile"])[0] + "_" + str(row["window"]) +"raw_image"              
        
        #Skip if missing a component data source
        if raw_image is False:
            print("Empty image, skipping")
            continue
        
        #Store plotting images
        plot_rgb = plot_image[:,:,:3].copy()
        
        #predict
        image        = generator.preprocess_image(raw_image)
        image, scale = generator.resize_image(image)

        if keras.backend.image_data_format() == 'channels_first':
            image = image.transpose((2, 0, 1))

        # run network
        boxes, scores, labels = model.predict_on_batch(np.expand_dims(image, axis=0))[:3]

        # correct boxes for image scale
        boxes /= scale

        # select indices which have a score above the threshold
        indices = np.where(scores[0, :] > score_threshold)[0]

        # select those scores
        scores = scores[0][indices]

        # find the order with which to sort the scores
        scores_sort = np.argsort(-scores)[:max_detections]

        # select detections
        image_boxes      = boxes[0, indices[scores_sort], :]
        image_scores     = scores[scores_sort]
        image_labels     = labels[0, indices[scores_sort]]
        image_detections = np.concatenate([image_boxes, np.expand_dims(image_scores, axis=1), np.expand_dims(image_labels, axis=1)], axis=1)
        
        #name image
        image_name = generator.image_names[i]        
        row = generator.image_data[image_name]             
        fname = os.path.splitext(row["tile"])[0] + "_" + str(row["window"])
        
        #drape boxes if they exist
        if len(image_boxes) > 0:
            #get lidar cloud if a new tile, or if not the same tile as previous image.
            if generator.with_lidar:
                if i == 0:
                    generator.load_lidar_tile()
                elif not generator.image_data[i]["tile"] == generator.image_data[i-1]["tile"]:
                    generator.load_lidar_tile()
            
            #The tile could be the full tile, so let's check just the 400 pixel crop we are interested    
            #Not the best structure, but the on-the-fly generator always has 0 bounds
            if hasattr(generator, 'hf'):
                bounds = generator.hf["utm_coords"][generator.row["window"]]    
            else:
                bounds=[]
            
        if save_path is not None:
            draw_annotations(plot_rgb, generator.load_annotations(i), label_to_name=generator.label_to_name)
            draw_detections(plot_rgb, image_boxes, image_scores, image_labels, label_to_name=generator.label_to_name,score_threshold=score_threshold)
        
            #name image
            image_name=generator.image_names[i]        
            row=generator.image_data[image_name]             
            fname=os.path.splitext(row["tile"])[0] + "_" + str(row["window"])
        
            #Write RGB
            cv2.imwrite(os.path.join(save_path, '{}.png'.format(fname)), plot_rgb)
            
            if experiment:
                experiment.log_image(os.path.join(save_path, '{}.png'.format(fname)),name=fname)      

        # copy detections to all_detections
        for label in range(generator.num_classes()):
            all_detections[i][label] = image_detections[image_detections[:, -1] == label, :-1]

    return all_detections


def _get_annotations(generator):
    """ Get the ground truth annotations from the generator.

    The result is a list of lists such that the size is:
        all_detections[num_images][num_classes] = annotations[num_detections, 5]

    # Arguments
        generator : The generator used to retrieve ground truth annotations.
    # Returns
        A list of lists containing the annotations for each image in the generator.
    """
    all_annotations = [[None for i in range(generator.num_classes())] for j in range(generator.size())]

    for i in range(generator.size()):
        # load the annotations
        annotations = generator.load_annotations(i)

        # copy detections to all_annotations
        for label in range(generator.num_classes()):
            all_annotations[i][label] = annotations[annotations[:, 4] == label, :4].copy()

    return all_annotations

def evaluate_pr(
    generator,
    model,
    iou_threshold=0.5,
    score_threshold=0.05,
    max_detections=200,
    save_path=None,
    experiment=None
):
    """ Evaluate the precision and recall for given dataset using a given model at a given threshold

    # Arguments
        generator       : The generator that represents the dataset to evaluate.
        model           : The model to evaluate.
        iou_threshold   : The threshold used to consider when a detection is positive or negative.
        score_threshold : The score confidence threshold to use for detections.
        max_detections  : The maximum number of detections to use per image.
        save_path       : The path to save images with visualized detections to.
        experiment     : Comet ml experiment to evaluate
    # Returns
        A tuple of recall and precision
    """

    # gather all detections and annotations
    all_detections     = _get_detections(generator, model, score_threshold=score_threshold, max_detections=max_detections, save_path=save_path, experiment=experiment)
    all_annotations    = _get_annotations(generator)
    average_precisions = {}

    # all_detections = pickle.load(open('all_detections.pkl', 'rb'))
    # all_annotations = pickle.load(open('all_annotations.pkl', 'rb'))
    # pickle.dump(all_detections, open('all_detections.pkl', 'wb'))
    # pickle.dump(all_annotations, open('all_annotations.pkl', 'wb'))

    # process detections and annotations
    for label in range(generator.num_classes()):
        false_positives = np.zeros((0,))
        true_positives  = np.zeros((0,))
        scores          = np.zeros((0,))
        num_annotations = 0.0

        for i in range(generator.size()):
            detections           = all_detections[i][label]
            annotations          = all_annotations[i][label]
            num_annotations     += annotations.shape[0]
            detected_annotations = []

            try:
                _ = len(detections)
            except:
                print("No detections")
                continue
            
            for d in detections:
                scores = np.append(scores, d[4])

                if annotations.shape[0] == 0:
                    false_positives = np.append(false_positives, 1)
                    true_positives  = np.append(true_positives, 0)
                    continue

                overlaps            = compute_overlap(np.expand_dims(d, axis=0), annotations)
                assigned_annotation = np.argmax(overlaps, axis=1)
                max_overlap         = overlaps[0, assigned_annotation]

                if max_overlap >= iou_threshold and assigned_annotation not in detected_annotations:
                    false_positives = np.append(false_positives, 0)
                    true_positives  = np.append(true_positives, 1)
                    detected_annotations.append(assigned_annotation)
                else:
                    false_positives = np.append(false_positives, 1)
                    true_positives  = np.append(true_positives, 0)

        # no annotations -> AP for this class is 0 (is this correct?)
        if num_annotations == 0:
            average_precisions[label] = 0, 0
            continue

        # sort by score
        indices         = np.argsort(-scores)
        false_positives = false_positives[indices]
        true_positives  = true_positives[indices]

        # compute false positives and true positives
        false_positives = np.cumsum(false_positives)
        true_positives  = np.cumsum(true_positives)

        # compute recall and precision
        recall    = true_positives / num_annotations
        precision = true_positives / np.maximum(true_positives + false_positives, np.finfo(np.float64).eps)
        
        if len(recall) > 0:
            print(f"At score threshold {score_threshold}, the IoU recall is {recall[-1]} and precision is {precision[-1]}")
            if experiment:
                experiment.log_metric("IoU_Recall",recall[-1])
                experiment.log_metric("IoU_Precision",precision[-1])
            
        else:
            print("None of the annotations exceeded score threshold")
            recall = [0]
            precision = [0]

    return [recall[-1], precision[-1]]

def evaluate(
    generator,
    model,
    iou_threshold=0.5,
    score_threshold=0.05,
    max_detections=200,
    save_path=None,
    experiment=None
):
    """ Evaluate the mAP for given dataset using a given model.

    # Arguments
        generator       : The generator that represents the dataset to evaluate.
        model           : The model to evaluate.
        iou_threshold   : The threshold used to consider when a detection is positive or negative.
        score_threshold : The score confidence threshold to use for detections.
        max_detections  : The maximum number of detections to use per image.
        save_path       : The path to save images with visualized detections to.
        experiment     : Comet ml experiment to evaluate
    # Returns
        A dict mapping class names to mAP scores.
    """

    # gather all detections and annotations
    all_detections     = _get_detections(generator, model, score_threshold=score_threshold, max_detections=max_detections, save_path=save_path, experiment=experiment)
    all_annotations    = _get_annotations(generator)
    average_precisions = {}

    # all_detections = pickle.load(open('all_detections.pkl', 'rb'))
    # all_annotations = pickle.load(open('all_annotations.pkl', 'rb'))
    # pickle.dump(all_detections, open('all_detections.pkl', 'wb'))
    # pickle.dump(all_annotations, open('all_annotations.pkl', 'wb'))

    # process detections and annotations
    for label in range(generator.num_classes()):
        false_positives = np.zeros((0,))
        true_positives  = np.zeros((0,))
        scores          = np.zeros((0,))
        num_annotations = 0.0

        for i in range(generator.size()):
            detections           = all_detections[i][label]
            annotations          = all_annotations[i][label]
            num_annotations     += annotations.shape[0]
            detected_annotations = []

            try:
                _ = len(detections)
            except:
                print("No detections")
                continue
            
            for d in detections:
                scores = np.append(scores, d[4])

                if annotations.shape[0] == 0:
                    false_positives = np.append(false_positives, 1)
                    true_positives  = np.append(true_positives, 0)
                    continue

                overlaps            = compute_overlap(np.expand_dims(d, axis=0), annotations)
                assigned_annotation = np.argmax(overlaps, axis=1)
                max_overlap         = overlaps[0, assigned_annotation]

                if max_overlap >= iou_threshold and assigned_annotation not in detected_annotations:
                    false_positives = np.append(false_positives, 0)
                    true_positives  = np.append(true_positives, 1)
                    detected_annotations.append(assigned_annotation)
                else:
                    false_positives = np.append(false_positives, 1)
                    true_positives  = np.append(true_positives, 0)

        # no annotations -> AP for this class is 0 (is this correct?)
        if num_annotations == 0:
            average_precisions[label] = 0, 0
            continue

        # sort by score
        indices         = np.argsort(-scores)
        false_positives = false_positives[indices]
        true_positives  = true_positives[indices]

        # compute false positives and true positives
        false_positives = np.cumsum(false_positives)
        true_positives  = np.cumsum(true_positives)

        # compute recall and precision
        recall    = true_positives / num_annotations
        precision = true_positives / np.maximum(true_positives + false_positives, np.finfo(np.float64).eps)
        
        if len(recall) > 0:
            print(f"At score threshold {score_threshold}, the IoU recall is {recall[-1]} and precision is {precision[-1]}")
        else:
            print("None of the annotations exceeded score threshold")
            
        # compute average precision
        average_precision  = _compute_ap(recall, precision)
        average_precisions[label] = average_precision, num_annotations

    return average_precisions


