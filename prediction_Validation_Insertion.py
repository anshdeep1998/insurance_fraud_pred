from datetime import datetime
from Prediction_Raw_Data_Validation.predictionDataValidation import Prediction_Data_validation
from DataTypeValidation_Insertion_Prediction.DataTypeValidationPrediction import dBOperation
from DataTransformation_Prediction.DataTransformationPrediction import dataTransformPredict
from application_logging import logger

class pred_validation:
    """ This is similar to the code in the training_Validation_Insertion.py file, there we had done validation
        and some initial preprocessings for the incoming data from client but that was training data."""

    """So explanation won't be repeated here again, just refer training_Validation_Insertion.py in root dir
       for any understanding needed."""

    # Basic summary for below code is:

    # data in sent in batches from client in the Prediction_Batch_files folder
    # First of all file names of all that is validated ie. each batch file here for prediction such that
    # name of file is in correct format.
    # then, no. of columns validated, "" converted to '' to make it insertable in database.
    # Then insert into database so that all prediction batch files are aggregated together.
    # Then all aggregated data exported as csv into the Prediction_FileFromDB folder as InputFilecsv.


    def __init__(self,path):
                        #ctrl+click
        self.raw_data = Prediction_Data_validation(path) # Prediction_Data_validation class imported from
                                                # predictionDataValidation.py file in the Predicition_Raw_Data_Validation
                                                # folder in root directory which has all methods for data validation called
                                                # below

        self.dataTransform = dataTransformPredict()# imported from DataTransformation_Prediction.DataTransformationPrediction
                                             # This is used below for initial preprocessing for validation.

        self.dBOperation = dBOperation() #  object of class dBOperation in the DataTypeValidationPrediction.py in
                                         # the DataTypeValidation_Insertion_Prediction folder.
                                     #This class dBOperation shall be used for handling all the SQL operations.
        self.file_object = open("Prediction_Logs/Prediction_Log.txt", 'a+')
        self.log_writer = logger.App_Logger()

    def prediction_validation(self):

        """just refer the training counterpart of this file i.e. training_Validation_Insertion.py in root dir
           for any understanding needed."""

        try:

            self.log_writer.log(self.file_object,'Start of Validation on files for prediction!!')
            #extracting values from prediction schema
            LengthOfDateStampInFile,LengthOfTimeStampInFile,column_names,noofcolumns = self.raw_data.valuesFromSchema()
            #getting the regex defined to validate filename
            regex = self.raw_data.manualRegexCreation()
            #validating filename of prediction files
            self.raw_data.validationFileNameRaw(regex,LengthOfDateStampInFile,LengthOfTimeStampInFile)
            #validating column length in the file
            self.raw_data.validateColumnLength(noofcolumns)
            #validating if any column has all values missing
            self.raw_data.validateMissingValuesInWholeColumn()
            self.log_writer.log(self.file_object,"Raw Data Validation Complete!!")

            self.log_writer.log(self.file_object,("Starting Data Transforamtion!!"))


            # replacing blanks in the csv file with "Null" values to insert in table
            # This is imported from the DataTransformationPrediction.py in the DataTransformation_Prediction folder in root dir.
            # and this is exactly same as it's training data counterpart i.e. DataTransformation.py in DataTransform_Training
            # folder.
            self.dataTransform.replaceMissingWithNull()

            self.log_writer.log(self.file_object,"DataTransformation Completed!!!")

            self.log_writer.log(self.file_object,"Creating Prediction_Database and tables on the basis of given schema!!!")
            #create database with given name, if present open the connection! Create table with columns given in schema
            self.dBOperation.createTableDb('Prediction',column_names)
            self.log_writer.log(self.file_object,"Table creation Completed!!")
            self.log_writer.log(self.file_object,"Insertion of Data into Table started!!!!")
            #insert csv files in the table
            self.dBOperation.insertIntoTableGoodData('Prediction')
            self.log_writer.log(self.file_object,"Insertion in Table completed!!!")
            self.log_writer.log(self.file_object,"Deleting Good Data Folder!!!")
            #Delete the good data folder after loading files in table
            self.raw_data.deleteExistingGoodDataTrainingFolder()
            self.log_writer.log(self.file_object,"Good_Data folder deleted!!!")
            self.log_writer.log(self.file_object,"Moving bad files to Archive and deleting Bad_Data folder!!!")
            #Move the bad files to archive folder
            self.raw_data.moveBadFilesToArchiveBad()
            self.log_writer.log(self.file_object,"Bad files moved to archive!! Bad folder Deleted!!")
            self.log_writer.log(self.file_object,"Validation Operation completed!!")
            self.log_writer.log(self.file_object,"Extracting csv file from table")
            #export data in table to csvfile
            self.dBOperation.selectingDatafromtableintocsv('Prediction')

        except Exception as e:
            raise e









