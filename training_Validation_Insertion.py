from datetime import datetime
from Training_Raw_data_validation.rawValidation import Raw_Data_validation
from DataTypeValidation_Insertion_Training.DataTypeValidation import dBOperation
from DataTransform_Training.DataTransformation import dataTransform
from application_logging import logger # from application_logging folder, we have imported logger.py

class train_validation:
    def __init__(self,path): # Here the path of folder Training_Batch_Files will be passed bcoz this class is for data validation
                             # to check no. of columns, their datatypes and names of each batch file sent by client, if any batch
                             # fails the validation is sent to bad data folder and deleted or else if batch file passes the validation,
                             # it is sent to database for all data aggregation.

        self.raw_data = Raw_Data_validation(path) # Raw_Data_validation is a class in rawValidation.py file
                                                 # in the Training_Raw_data_validation folder. This class is used
                              # for handling all the validation done on the Raw Training Data!!.


        self.dataTransform = dataTransform() # imported from DataTransform_Training.DataTransformation
                                             # This is used below for initial preprocessing for validation.

        self.dBOperation = dBOperation() #  object of class dBOperation in the DataTypeValidation.py in
                                         # the DataTypeValidation_Insertion_Training folder.
                                     #This class dBOperation shall be used for handling all the SQL operations.
        self.file_object = open("Training_Logs/Training_Main_Log.txt", 'a+')#Training_Main_Log.txt is a log file in the
                                                                       #Training_logs folder.
        self.log_writer = logger.App_Logger()#App_Logger is class inside logger.py whose object initialized as self.log_writer

    def train_validation(self):
        try:
            # App_Logger() class takes 2 arguements i.e. open() object of log file in which we are logging currently
            # and the message to log in that file. Currently we are logging in Training_Main_Log.txt which is in the
            # Training_logs folder. Just have a look at all other log files inside this same folder to have better understanding.
            self.log_writer.log(self.file_object, 'Start of Validation on files for Training!!')
            # extracting values from schema_training.json, this file contains values of all 4 variables written below.
            # self.raw_data initialized above is an object of Raw_Data_validation class explained well above.
            # valuesFromSchema() is the method of this class which returns these 4 values returned below through dictionary
            #parsing, and that function is well explained in this class itself in the rawValidation.py file and can be
            #accessed through ctrl+click.
            LengthOfDateStampInFile, LengthOfTimeStampInFile, column_names, noofcolumns = self.raw_data.valuesFromSchema()


            # getting the regex defined to validate filename
            # self.raw_data is an object of Raw_Data_validation class as explained above.
            # This function manualRegexCreation() of this class is used to validate the name of csv files which are the
            # data sent by client in batches e.g. fraudDetection_021119920_010222.csv Just ctrl+click to go through this
            # function.
            regex = self.raw_data.manualRegexCreation()
            # Now we have validated file's name format i.e. fraudDetection_numeric_numeric.csv,
            # e.g. fraudDetection_021119920_010222.csv where 021119920 is length of datestamp and 010222 is length of timestamp.
            # so just fraudDetection_numeric_numeric.csv is not enough bcoz a file named fraudDetection_234_456.csv also rejected.
            # datestamp and timestamp should be of length specified by schema in schema_training.json.
            # length of datestamp and timestamp is nothing but LengthOfDateStampInFile, LengthOfTimeStampInFile which are
            # imported above and their values are as it is written in the schema file.
            # validating filename of prediction files
            # now go through validationFileNameRaw() of this same above object by ctrl+click, well explained there.
            self.raw_data.validationFileNameRaw(regex, LengthOfDateStampInFile, LengthOfTimeStampInFile)


            # validating no. of columns  in the file, go ctrl+click for explain.
            self.raw_data.validateColumnLength(noofcolumns)

            # validating if any column has all values missing, which is a useless column and of no use and is irrelevant column
            # any column out of all columns having all missing values is irrelevant. Any data having even 1 such column
            # with all Nan's, that whole data sent to bad folder.
            # Go through ctrl+click explaination.
            self.raw_data.validateMissingValuesInWholeColumn()
            self.log_writer.log(self.file_object, "Raw Data Validation Complete!!")

            # Now we need some transformation/preprocessing of data bcoz the way python understands our data
            # and the way database understands our data is different. so before insertion into database, we need
            # some transformation or preprocessing like replacing blanks/NaN's in the csv file with "Null" values
            # and replacing single quotes '' with double quotes i.e. "". Both these things have been done in
            # the replaceMissingWithNull() function, do ctrl+click for details.
            self.log_writer.log(self.file_object, "Starting Data Transforamtion!!")


            # The below function replaceMissingWithNull() has been imported from DataTransformation.py in the
            # DataTransform_Training folder in root.
            self.dataTransform.replaceMissingWithNull() #this function just replaces '' with "" to identify python string
                                                        #as varchar in the database.
            # but in this function replaceMissingWithNull(),  we just replace quotes and don't replace NaN's with Null string
            # bocz in dataset batches csv, all missing values are having "?" instead of empty missing, and replacing those
            # will be done in the data preprocessing stage of ML.

            self.log_writer.log(self.file_object, "DataTransformation Completed!!!")

            self.log_writer.log(self.file_object,
                                "Creating Training_Database and tables on the basis of given schema!!!")

            # create database with given name, if present open the connection! Create table with columns given in schema
            # ctrl+click for explanation in DataTypeValidation.py
            self.dBOperation.createTableDb('Training', column_names)

            self.log_writer.log(self.file_object, "Table creation Completed!!")
            self.log_writer.log(self.file_object, "Insertion of Data into Table started!!!!")

            # insert batch csv files(good raw data) in the database table created above using createTableDb() function above.
            # ctrl+click for explanation in DataTypeValidation.py
            self.dBOperation.insertIntoTableGoodData('Training')
            self.log_writer.log(self.file_object, "Insertion in Table completed!!!")
            self.log_writer.log(self.file_object, "Deleting Good Data Folder!!!")


            # Delete the good data folder after loading files in database table
            # ctrl+click for explanation in rawValidation.py
            self.raw_data.deleteExistingGoodDataTrainingFolder()
            self.log_writer.log(self.file_object, "Good_Data folder deleted!!!")
            self.log_writer.log(self.file_object, "Moving bad files to Archive and deleting Bad_Data folder!!!")


            # Move the bad files to archive folder which are to be sent back to client bcoz of invalid data issue.
            # so bad data deleted from it's original path and moved to archieve folder i.e. TrainingArchieveBadData folder.
            # unlike good data which is deleted permanently and moved nowhere.
            # ctrl+click for explanation in rawValidation.py
            self.raw_data.moveBadFilesToArchiveBad()
            self.log_writer.log(self.file_object, "Bad files moved to archive!! Bad folder Deleted!!")
            self.log_writer.log(self.file_object, "Validation Operation completed!!")
            self.log_writer.log(self.file_object, "Extracting csv file from table")


            # export data in table to csvfile and all that clubbed data from database saved into the InputFile.csv file
            # inside the Training_FileFromDB folder inside the root directory.
            self.dBOperation.selectingDatafromtableintocsv('Training')
            # ctrl+click for explanation in DataTypeValidation.py
            self.file_object.close()

        except Exception as e:
            raise e









