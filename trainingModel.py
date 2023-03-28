"""
This is the Entry point for Training the Machine Learning Model.



"""


# Doing the necessary imports
from sklearn.model_selection import train_test_split
from data_ingestion import data_loader
from data_preprocessing import preprocessing
from data_preprocessing import clustering
from best_model_finder import tuner
from file_operations import file_methods
from application_logging import logger
import numpy as np
import pandas as pd

#Creating the common Logging object


class trainModel:

    def __init__(self):
        self.log_writer = logger.App_Logger()
        self.file_object = open("Training_Logs/ModelTrainingLog.txt", 'a+')
    def trainingModel(self):
        # Logging the start of Training
        self.log_writer.log(self.file_object, 'Start of Training')
        try:
            # Getting the data from the source
            # data_loader.py file was imported above which has Data_Getter class which has only 1 method
            # i.e. get_data() which does nothing but simply reads csv file at the path 'Training_FileFromDB/InputFile.csv'.
            # along with logging it.
            # and this csv file os nothing but the complete clubbed data exported as csv from database.

            # ANd why it specifically reads 'Training_FileFromDB/InputFile.csv' bcoz this file contains all aggregated data
            # downloaded from the database.

            data_getter=data_loader.Data_Getter(self.file_object,self.log_writer)
            data=data_getter.get_data()


            """doing the data preprocessing"""
            # preprocessing represents the preprocessing.py file in the data_preprocessing folder in the root dir of this proj.
            # preprocessing.py file contains Preprocessor class which takes 2 arguements i.e. file_object and logger_object
            # file_object takes input as open() called on logger file in which we will log
            # logger_object takes input as above logger.App_Logger() i.e. write() in the logger file acc to date, time.
            preprocessor=preprocessing.Preprocessor(self.file_object,self.log_writer)

            # Also Preprocessor class has 8 functions to preprocess the data, they are used below.
            # below remove_columns() function simply drops the list of columns passed from the passed data.
            # why these specific columns dropped in explained well in the jupyter file in EDA folder.
            data=preprocessor.remove_columns(data,['policy_number','policy_bind_date','policy_state','insured_zip','incident_location','incident_date','incident_state','incident_city','insured_hobbies','auto_make','auto_model','auto_year','age','total_claim_amount'])

            # All missing values in the data have "?" which are replaced with np.NaN
            data.replace('?',np.NaN,inplace=True) # replacing '?' with NaN values for imputation

            # check if missing values are present in the dataset.
            # Go through ctrl+click explanation.
            # This function returns is_null_present as True if there is even 1 Null value and names of all columns
            # having null values.



            is_null_present, cols_with_missing_values = preprocessor.is_null_present(data)
            data.to_csv(r'C:\Users\Anshdeep\OneDrive\Desktop\Ineuron\Full stack data science course\Python projects\fraudDetection\models_for_missing_values\data_to_fill_missing.csv')
            # if missing values are there, replace them appropriately.
            if (is_null_present): # i.e. is_null_present == True returned by above preprocessor.is_null_present() function.
                             # ctrl+click
                data = preprocessor.impute_missing_values(data, cols_with_missing_values)  # missing value imputation

            # print(data)
            # print(data.isnull().sum())
            #print(data.dtypes)

######################################################################################
            # encode categorical data
            # go to ctrl+click.
            data = preprocessor.encode_categorical_columns(data)
            # print(data)
            # print(data.isnull().sum())

            # # below separate_label_feature divides data into independent input features and target dependent feature.
            X,Y=preprocessor.separate_label_feature(data,label_column_name='fraud_reported')


            """ Applying the clustering approach"""
            # ctrl+click on KmeansClustering() takes us to clustering.py file which has class KMeansClustering()
            # which takes same 2 arguements as above class Preprocessor() took.
            kmeans=clustering.KMeansClustering(self.file_object,self.log_writer) # object initialization.
            # elbow_plot() is function of this class.
            # ctrl+click to understand detail.
            # below function saves PNG of elbow plot and returns optimal K.
            number_of_clusters=kmeans.elbow_plot(X)  #  using the elbow plot to find the number of optimum clusters

            # This below function Divides the data into clusters and no. of clusters were computed by the above
            # function .elbow_plot() which are passed in the below function as arguement.
            # ctrl+click for explanation for below function create_clusters() which saves kmeans model
            # in the in the subfolders of models folder in root dir and returns the data which has additional
            # column named Clusters which has cluster no. of each row

            """We are saving the clustered data and model bcoz later on when new data records from client comes to us,
               model will help us classify that new records/rows into clusters we made just now so that we can apply
               specific model to these clusters."""

            # Calling this below function create_clusters() not only trains a Kmeans model and divides our data into clusters
            # but also saves the same Kmeans model in the models folder in the root directory.



            # number_of_clusters in which we will divide data will be selected as per elbow method which is our e.g. is 2.
            # below function .create_clusters() takes input X i.e. all independent input features which are to be clustered
            # and number_of_clusters in which the Kmeans model will divide the whole data into.

            X = preprocessor.scale_numerical_columns(X)
            X = kmeans.create_clusters(X, number_of_clusters)

            # add the target column to the clustered data as target column was dropped above
            X['Labels'] = Y

            # getting the name of each unique cluster from our dataset
            list_of_clusters = X['Cluster'].unique()


            """parsing all the clusters and looking for the best ML algorithm to fit on individual cluster"""

            for i in list_of_clusters: # list_of_clusters computed above.

                cluster_data=X[X['Cluster'] == i] # cluster_data represents data for each cluster "i".

                # Prepare the feature and Label columns

                # This is the input data for each cluster consisting of all input independent features.
                # target columns and cluster no. column not included in input data.
                cluster_features=cluster_data.drop(['Labels','Cluster'],axis=1)

                # target column for each cluster's data.
                cluster_label = cluster_data['Labels']



                # splitting the data into training and test set for each cluster one by one
                # cluster_features and cluster_label represent input columns and output columns respectively.
                x_train, x_test, y_train, y_test = train_test_split(cluster_features, cluster_label, test_size=1 / 3, random_state=355)


                # Proceeding with more data pre-processing steps
                # preprocessor object initialized above is object of Preprocessor class.
                # ctrl+click for details of scale_numerical_columns feature.

                # This is done wrt. each cluster within this respective for loop of clusters.
                # x_train = preprocessor.scale_numerical_columns(x_train)
                # x_test = preprocessor.scale_numerical_columns(x_test)

                # tuner.py file imported above from best_model_finder folder in root directory.
                # Model_Finder class imported from tuner.py takes the below 2 arguements which were passed
                # which were passed in objects of other classes above too.
                # Same logging done in "Training_Logs/ModelTrainingLog.txt".

                # This is done wrt. each cluster within this respective for loop of clusters.
                model_finder=tuner.Model_Finder(self.file_object,self.log_writer) # object initialization

                # getting the best model for each of the clusters
                # go through below function get_best_model() by ctrl+click.
                # best model along with it's name is returned.

                # This is done wrt. each cluster within this respective for loop of clusters.
                # It finds best model for each cluster
                best_model_name, best_model, best_model_score = model_finder.get_best_model(x_train,y_train,x_test,y_test)

                # saving the best model for each cluster to the directory.
                # File_Operation() class imported from file_methods.py file in the file_operations folder in root dir.
                file_op = file_methods.File_Operation(self.file_object,self.log_writer)

                # using save_model() function of File_Operation class, we save this model in the models folder
                # in the models folder of root directory and the path to this models folder is passed in that class itslef
                # in the file_methods.py file.

                # So we save model for each cluster inside different sub-folders of models folder in root dir and names
                # of those sub-folders is name of model + str(cluster no.)
                # As of now for our current data, we have got only 2 clusters 0 and 1.
                # We will be saving model selected for each cluster as explained below.
                # e.g. SVM1 means SVM model selected
                # for 1st cluster, XGBoost0 means XGBoost model was selected for 0th cluster.
                # code for the same written below as best_model_name+str(i).

                save_model = file_op.save_model(best_model, best_model_name+str(i))

                print(f"Best model selected is {best_model_name} with an accuracy of {100*best_model_score} %")



            # logging the successful Training
            self.log_writer.log(self.file_object, 'Successful End of Training')
            self.file_object.close()

        except Exception as e:
            # logging the unsuccessful Training
            self.log_writer.log(self.file_object, 'Unsuccessful End of Training')
            self.file_object.close()
            raise Exception