#!/usr/bin/env python

"""
Helper functions and classes will be placed here.
"""

import os
import tarfile
import six.moves.urllib as urllib

import numpy as np

from tf_server.msg import DetectedObjectArray,DetectedObject






def download_model(\
    download_base='http://download.tensorflow.org/models/object_detection/', \
    model_name='ssd_mobilenet_v1_coco_11_06_2017'\
    ):
    """
    Downloads the detection model from tensorflow servers

    Args:
    download_base: base url where the object detection model is downloaded from

    model_name: name of the object detection model

    Returns:

    """

    # add tar gz to the end of file name
    model_file = model_name + '.tar.gz'

    try:
        opener = urllib.request.URLopener()
        opener.retrieve(download_base + model_file, \
            model_file)
        tar_file = tarfile.open(model_file)
        for f in tar_file.getmembers():
            file_name = os.path.basename(f.name)
            if 'frozen_inference_graph.pb' in file_name:
                tar_file.extract(f, os.getcwd())
    except Exception as e:
        raise



def create_detection_aw_msg(im, output_dict, category_index, bridge):
    print 'create_detection_aw_msg'

    boxes = output_dict["detection_boxes"]
    scores = output_dict["detection_scores"]
    classes = output_dict["detection_classes"]


    msg = DetectedObjectArray()

    msg.header = im.header

    scores_above_threshold = np.where(scores > 0.5)[0]

    KK=0
    for s in scores_above_threshold:
        # Get the properties
        KK=KK+1

        bb = boxes[s,:]
        sc = scores[s]
        cl = classes[s]

        # Create the detection message
        detection = DetectedObject()
        detection.header = im.header
        detection.label = category_index[int(cl)]['name']
        detection.score = sc

        detection.color.r = 1.0
        detection.color.g = 1.0
        detection.color.b = 1.0
        detection.color.a = 1.0

        detection.image_frame = im.header.frame_id;
        detection.x = int((im.width-1) * bb[1])
        detection.y = int((im.height-1) * bb[0])
        detection.width = int((im.width-1) * (bb[3]-bb[1]))
        detection.height = int((im.height-1) * (bb[2]-bb[0]))



        msg.objects.append(detection)

    return msg,KK