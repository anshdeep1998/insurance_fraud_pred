import pandas as pd
import numpy as np
from file_operations import file_methods
from data_preprocessing import preprocessing
from data_ingestion import data_loader
from data_ingestion import data_loader_prediction
from application_logging import logger
from Prediction_Raw_Data_Validation.predictionDataValidation import Prediction_Data_validation

# This class has been made to handle the data coming from client on which predictions are to be done.
"""It includes data preprocessing for the prediction data, then making different clusters out of that whole data,
   load the already saved models, do predictions and save predictions as csv in the Prediction_Output_File
   folder in the root dir.
"""

# This file is the prediction counterpart of the trainingModel.py file in the root directory.

class prediction:
    def __init__(self,path):
        self.file_object = open("Prediction_Logs/Prediction_Log.txt", 'a+')
        self.log_writer = logger.App_Logger()
                             # This is the object of Prediction_Data_validation class from predictionDataValidation.py
                             # file in the Prediction_Raw_Data_Validation folder in root dir.
                             # which takes input as path of prediction data location.

                             # ctrl+click for explanation.

        self.pred_data_val = Prediction_Data_validation(path)
                              # Prediction_Data_validation class imported from
                              # predictionDataValidation.py file in the Predicition_Raw_Data_Validation
                              # folder in root directory which has all methods for data validation called
                              # below. But here we will be using it's 1 function only i.e.deletePredictionFile()


    def predictionFromModel(self):

        try:
            self.pred_data_val.deletePredictionFile() # deletes the existing prediction file from last run!
                                                      # bcoz everytime we save new csv for prediction, old to be deleted.
            self.log_writer.log(self.file_object, 'Start of Prediction')

            # data_loader_prediction.py file imported above from the data_ingestion folder in root dir
            # which has Data_Getter_Pred class
            # having only 1 function get_data() and it does nothing just loads data from the InputFile.csv in
            # Prediction_FileFromDB folder.

            # similarly in it's training counterpart, we had data_loader.py in data_ingestion folder in root dir.
            # Similarly we have data_loader_prediction.py in the data_ingestion folder as prediction couterpart.
            # # This loads data for prediction to be done on models i.e.
            #   the InputFile.csv in the Prediction_FileFromDB folder in root dir which contains
            #   all the aggregated prediction data
            data_getter=data_loader_prediction.Data_Getter_Pred(self.file_object,self.log_writer)
            data=data_getter.get_data() # loads csv data from 'Prediction_FileFromDB/InputFile.csv'.

            """This below training data i.e. InputFile.csv from Training_FileFromDB folder in in root dir imported here bcoz
                Kmeans model for clustering data was trained on this model and using that model we need to cluster for
                 the above prediction data too, but though the columns/features of both training and prediction data is same
                 but order of all columns is different in prediction data as a result Kmeans model not able to identify,
                 so we will change the order of all columns prediction data making it same as training data's order of columns."""
            training_data_getter = data_loader.Data_Getter(self.file_object,self.log_writer)
            training_data = training_data_getter.get_data()
            training_data = training_data.drop(['fraud_reported'],axis=1)

            columns_training_data = list(training_data.columns)
            #print(columns_training_data)
            # order of columns of prediction data made same as order of columns of training_data.

            # data = data[columns_training_data]
            # print(data.columns)
            # print("HI Bye Lie: ",list(data.columns) == list(training_data.columns))
            # preprocessing file imported from Data_Preprocessing folder which was used in trainingModel.py file also.
            preprocessor = preprocessing.Preprocessor(self.file_object, self.log_writer)

            # drops the features as per features we selected.
            # why these specific columns dropped in explained well
            # in the jupyter file in EDA folder.
            data = preprocessor.remove_columns(data,
                                               ['policy_number', 'policy_bind_date', 'policy_state', 'insured_zip',
                                                'incident_location', 'incident_date', 'incident_state', 'incident_city',
                                                'insured_hobbies', 'auto_make', 'auto_model', 'auto_year', 'age',
                                                'total_claim_amount'])  # remove the column as it doesn't contribute to prediction.
            data.replace('?', np.NaN, inplace=True)  # replacing '?' with NaN values for imputation



            # check if missing values are present in the dataset
            # explained well in preprocessing.py file, ctrl+click.
            # is_null_present is True or False if null values present or not and cols_with_missing_values gives
            # all columns with missing values.
            is_null_present, cols_with_missing_values = preprocessor.is_null_present(data)

            # if missing values are there, replace them appropriately.
            # impute_missing_values replaces null with most frequent occurring values.
            # ctrl + click for explain in preprocessing.py
            if (is_null_present): # is_null_present == True means at least some nulls present in data.
                data = preprocessor.impute_missing_values(data, cols_with_missing_values)  # missing value imputation


            # encode categorical data

            # ctrl+click for explain both below methods, it selects categorical columns out of whole data and encodes.
            data = preprocessor.encode_categorical_columns(data)

            data.to_csv(
                r"C:\Users\Anshdeep\OneDrive\Desktop\Ineuron\Full stack data science course\Python projects\fraudDetection\EDA\trials\df_preprocessed_pred_3.csv")

            #data = preprocessor.scale_numerical_columns(data)

            # # File_Operation class in file_methods.py file_operations folder in root dir has all methods
            # # to load, save models or function to select best model for each cluster as per cluster no.
            # # path of models\ folder in root dir already passed in that class itself.
            #
            # """Just recall that this file predictFromModel.py is the prediction counterpart of trainingModel.py file in the root
            #    directory of this project. In that file, KMeansClustering class was imported from clustering.py file which is in
            #    the data_preprocessing folder in the root dir and that KmeansClustering class methods were used to create Kmeans
            #    model which divided whole data into clusters and on each cluster, separate models like XGboost and SVC were trained.
            #
            #    In the methods of that KmeansClustering class, we not only divided data into clusters, but also saved the Kmeans
            #    clustering model into the models folder in the root dir.
            #
            #    So we are calling that already trained and saved Kmeans clustering model below.
            #    """
            # file_loader=file_methods.File_Operation(self.file_object,self.log_writer)
            # kmeans=file_loader.load_model('KMeans')
            #
            # data.to_csv(r"C:\Users\Anshdeep\OneDrive\Desktop\Ineuron\Full stack data science course\Python projects\fraudDetection\EDA\Kmeans_pediction_input.csv")
            # ## Code changed
            #
            # clusters=kmeans.predict(data) # it predicts cluster no. of each row/record.
            # data['clusters']=clusters # new column for cluster no. of each row/record is made.
            # clusters=data['clusters'].unique()
            # predictions=[] # empty list for predictions initialized.
            # for i in clusters:
            #     cluster_data= data[data['clusters']==i] # filtered dataframe of each and every cluster
            #     cluster_data = cluster_data.drop(['clusters'],axis=1) # drop cluster no. column as we will send this data
            #                                                           # for prediction.
            #     # file_loader was object of File_Operation class in file_methods.py in file_operations folder
            #     # as was initialized above. it selects the correct model based on cluster number.
            #     # e.g. is cluster no. is 0, it fetches model saved inside XGBoost0 and if cluster no. is 1,
            #     # it fetches model saved inside XGBoost1.
            #
            #     model_name = file_loader.find_correct_model_file(i)
            #     model = file_loader.load_model(model_name) # we load the selected model.
            #
            #     result=(model.predict(cluster_data)) # for binary classif, we have 0 and 1
            #     for res in result:
            #         if res==0:
            #             predictions.append('N') # 0 means not fraud "N".
            #         else:
            #             predictions.append('Y') # else yes fraud "Y".
            #
            # # a dataframe of predictions saved in Prediction_Output_File in root dir
            # # this csv has only row index no. and Y or N, but we can save Y and N predicted target row by concatenating them
            # # with all columns also, but that is done according to client requirements or not.
            # final= pd.DataFrame(list(zip(predictions)),columns=['Predictions'])
            # path="Prediction_Output_File/Predictions.csv"
            # final.to_csv("Prediction_Output_File/Predictions.csv",header=True,mode='a+') #appends result to prediction file
            # self.log_writer.log(self.file_object,'End of Prediction')
        except Exception as ex:
            self.log_writer.log(self.file_object, 'Error occured while running the prediction!! Error:: %s' % ex)
            raise ex
        #return path




