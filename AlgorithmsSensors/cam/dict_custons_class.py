import cv2
from AlgorithmsSensors.cam.DetectObjClasses import *

{
    'tracker':{
        'tld': cv2.TrackerTLD,
        'boosting': cv2.TrackerBoosting,
        'kcf': cv2.TrackerKCF,
        'csrt': cv2.TrackerCSRT,
        'mil': cv2.TrackerMIL
    },
    'detect':{
        'mog':{'class':DetectMog,'file':null,'param':null},
        'svm':{'class':DetectML,'file':'svm','param':null},
        'neural':{'class':DetectML,'file':'neural','param':null},
    },
    'prep_data':{
        'pca':{'class':null,'file':null,'param':null}
    }
}