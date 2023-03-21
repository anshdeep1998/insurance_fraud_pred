from wsgiref import simple_server
from flask import Flask, request, render_template
from flask import Response
import os
from flask_cors import CORS, cross_origin
from prediction_Validation_Insertion import pred_validation
from trainingModel import trainModel
from training_Validation_Insertion import train_validation
import flask_monitoringdashboard as dashboard
from predictFromModel import prediction

os.putenv('LANG', 'en_US.UTF-8')
os.putenv('LC_ALL', 'en_US.UTF-8')


# folderPath = r"C:\Users\Anshdeep\OneDrive\Desktop\Ineuron\Full stack data science course\Python projects\fraudDetection\Training_Batch_Files"
#
# train_valObj = train_validation(folderPath)
# train_valObj.train_validation()
#
# trainModelObj = trainModel()
# trainModelObj.trainingModel()

prediction_folder_path = r"C:\Users\Anshdeep\OneDrive\Desktop\Ineuron\Full stack data science course\Python projects\fraudDetection\Prediction_Batch_files"

pred_val = pred_validation(prediction_folder_path)
pred_val.prediction_validation()

pred = prediction(prediction_folder_path)
pred.predictionFromModel()


# path = pred.predictionFromModel()
# print("Prediction file created at this path: ", path)
