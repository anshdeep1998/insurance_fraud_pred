import sqlite3
from datetime import datetime
from os import listdir
import os
import re
import json
import shutil
import pandas as pd
from application_logging.logger import App_Logger





class Raw_Data_validation:

    """
             This class shall be used for handling all the validation done on the Raw Training Data!!.



             """

    def __init__(self,path):
        self.Batch_Directory = path
        self.schema_path = 'schema_training.json'
        self.logger = App_Logger()


    def valuesFromSchema(self):
        """
                        Method Name: valuesFromSchema
                        Description: This method extracts all the relevant information from the pre-defined "Schema" file.
                        Output: LengthOfDateStampInFile, LengthOfTimeStampInFile, column_names, Number of Columns
                        On Failure: Raise ValueError,KeyError,Exception


                                """
        try:
            with open(self.schema_path, 'r') as f:       #All the dictionary data from schema json file is loaded
                dic = json.load(f)                   #using json.loads to convert into proper dict format.
                f.close()
            pattern = dic['SampleFileName']
            LengthOfDateStampInFile = dic['LengthOfDateStampInFile'] #These are 4 details are simply parsed through dictionary
            LengthOfTimeStampInFile = dic['LengthOfTimeStampInFile'] #extracted above from the imported dictionary.
            column_names = dic['ColName']
            NumberofColumns = dic['NumberofColumns']

            file = open("Training_Logs/valuesfromSchemaValidationLog.txt", 'a+')#This part is logged inside the folder named
                                                          # valuesfromSchemaValidationLog.txt log file in that same old
                                                         #folder named Training_Logs where all logs related to training done.
            message ="LengthOfDateStampInFile:: %s" %LengthOfDateStampInFile + "\t" + "LengthOfTimeStampInFile:: %s" % LengthOfTimeStampInFile +"\t " + "NumberofColumns:: %s" % NumberofColumns + "\n"
            self.logger.log(file,message)

            file.close()


      # 3 possible exceptions below, better skip directly to the 3rd exception Exception as e instead of 1st 2.
        except ValueError:
            file = open("Training_Logs/valuesfromSchemaValidationLog.txt", 'a+')
            self.logger.log(file,"ValueError:Value not found inside schema_training.json")
            file.close()
            raise ValueError

        except KeyError:
            file = open("Training_Logs/valuesfromSchemaValidationLog.txt", 'a+')
            self.logger.log(file, "KeyError:Key value error incorrect key passed")
            file.close()
            raise KeyError

        except Exception as e:
            file = open("Training_Logs/valuesfromSchemaValidationLog.txt", 'a+')
            self.logger.log(file, str(e))
            file.close()
            raise e

        return LengthOfDateStampInFile, LengthOfTimeStampInFile, column_names, NumberofColumns


    def manualRegexCreation(self):
        """
                                Method Name: manualRegexCreation
                                Description: This method contains a manually defined regex based on the "FileName" given in "Schema" file.
                                            This Regex is used to validate the filename of the training data.
                                Output: Regex pattern
                                On Failure: None


                                        """
        regex = "['fraudDetection']+['\_'']+[\d_]+[\d]+\.csv"
        # used to validate the name of csv files which are the  data sent by client in batches
        # e.g. fraudDetection_021119920_010222.csv, this should be in same format with name starting from fraudDetection,
        # then followed by _numeric_numeric.csv, so if name of batch file not in this format or even as xlsx and not csv,
        # the data gets straight away rejected and sent to Bad folder.
        return regex

    def createDirectoryForGoodBadRawData(self):

        """
                                      Method Name: createDirectoryForGoodBadRawData
                                      Description: This method creates empty directories to store the Good Data and Bad Data
                                                    after validating the training data.

                                      Output: None
                                      On Failure: OSError



                                              """

        try:
            path = os.path.join("Training_Raw_files_validated/", "Good_Raw/")
            if not os.path.isdir(path):
                os.makedirs(path)
            path = os.path.join("Training_Raw_files_validated/", "Bad_Raw/")
            if not os.path.isdir(path):
                os.makedirs(path)

        except OSError as ex:
            file = open("Training_Logs/GeneralLog.txt", 'a+')
            self.logger.log(file,"Error while creating Directory %s:" % ex)
            file.close()
            raise OSError

    def deleteExistingGoodDataTrainingFolder(self):

        """
                                            Method Name: deleteExistingGoodDataTrainingFolder
                                            Description: This method deletes the directory made  to store the Good Data
                                                          after loading the data in the table. Once the good files are
                                                          loaded in the DB,deleting the directory ensures space optimization.
                                            Output: None
                                            On Failure: OSError



                                                    """

        try:
            path = 'Training_Raw_files_validated/' # This path folder contains good and bad validated data
            # if os.path.isdir("ids/" + userName):
            # if os.path.isdir(path + 'Bad_Raw/'):
            #     shutil.rmtree(path + 'Bad_Raw/')
            if os.path.isdir(path + 'Good_Raw/'):   # path combinations are done to make path to good data inside above folder.
                shutil.rmtree(path + 'Good_Raw/')    # This line deletes files.
                file = open("Training_Logs/GeneralLog.txt", 'a+')
                self.logger.log(file,"GoodRaw directory deleted successfully!!!")
                file.close()
        except OSError as s: # Normal loggings are done.
            file = open("Training_Logs/GeneralLog.txt", 'a+')
            self.logger.log(file,"Error while Deleting Directory : %s" %s)
            file.close()
            raise OSError

    def deleteExistingBadDataTrainingFolder(self):

        """
                                            Method Name: deleteExistingBadDataTrainingFolder
                                            Description: This method deletes the directory made to store the bad Data.
                                            Output: None
                                            On Failure: OSError
                                                    """
        try:
            path = 'Training_Raw_files_validated/' # This path folder contains good and bad validated data
            if os.path.isdir(path + 'Bad_Raw/'): # path combinations are done to make path to good data inside above folder.
                shutil.rmtree(path + 'Bad_Raw/') # This line deletes files.
                file = open("Training_Logs/GeneralLog.txt", 'a+')
                self.logger.log(file,"BadRaw directory deleted before starting validation!!!")
                file.close()
        except OSError as s: # Normal loggings are done.
            file = open("Training_Logs/GeneralLog.txt", 'a+')
            self.logger.log(file,"Error while Deleting Directory : %s" %s)
            file.close()
            raise OSError

    def moveBadFilesToArchiveBad(self):
        # so bad data deleted from it's original path and moved to archieve folder i.e. TrainingArchieveBadData folder.
        # unlike good data which is deleted permanently and moved nowhere.

        """
                                            Method Name: moveBadFilesToArchiveBad
                                            Description: This method deletes the directory made  to store the Bad Data
                                                          after moving the data in an archive folder. We archive the bad
                                                          files to send them back to the client for invalid data issue.
                                            Output: None
                                            On Failure: OSError
                                                    """
        now = datetime.now()
        date = now.date()                # current date and time.
        time = now.strftime("%H%M%S")
        try:

            source = 'Training_Raw_files_validated/Bad_Raw/' # This is the path of Bad_Raw data inside Training_Raw_files_validated
                                                               # in the root directory of this project which contains all the good
                                                # and bad validated data in the Good_Raw and Bad_Raw folders in this
                                               #Training_Raw_files_validated folder. THis folder was explained many times in the
                                               # DataTypeValidation.py file's dBOperation class also.
                                                                # folder in root directory and this folder mentioned many times.
            if os.path.isdir(source):# condition if the source path above i.e. 'Training_Raw_files_validated/Bad_Raw/' exists.
                                    # only then we carry forward with the below process of moving data from this source path
                                    # i.e. 'Training_Raw_files_validated/Bad_Raw/'
                        # we are checking the condition of existence of Bad_Raw folder bcoz we delete the Good_Raw and Bad_Raw
                        # folders inside this Training_Raw_files_validated after insertion of good data into database and
                        # after shifting bad data into archive folder
                    # That is why when we mostly open "TrainingArchiveBadData", we find it empty.
                path = "TrainingArchiveBadData"
                if not os.path.isdir(path): # inside above source path, if TrainingArchiveBadData doesn't exist by default,
                    os.makedirs(path) # then make this path.

                # inside the above path of TrainingArchiveBadData folder in root directory, we make new folders each
                # with the name BadData_ + current date in string format + current date in string format.
                # each folder with name has unique date and time when bad data was being moved to archieve folder to
                # return it back to the client.
                dest = 'TrainingArchiveBadData/BadData_' + str(date)+"_"+str(time)
                if not os.path.isdir(dest):
                    os.makedirs(dest)        # make this dest path if doesn't exist


                files = os.listdir(source) # this is the source path defined above of 'Training_Raw_files_validated/Bad_Raw/'
                                      # and all bad data to be shifted from this path to archive.
                for f in files: # f will contain names of all bad files from this folder.
                    if f not in os.listdir(dest): # if those files already not in the destination folder i.e. bad archive data,
                        shutil.move(source + f, dest) # then move it to the bad archive data folder.

                file = open("Training_Logs/GeneralLog.txt", 'a+')
                self.logger.log(file,"Bad files moved to archive") #logging process as before.

                # after moving all data from 'Training_Raw_files_validated/' to bad archive folfer i.e. TrainingArchiveBadData,
                # we delete this whole folder of Bad_Raw inside Training_Raw_files_validated folder in root directory
                # using the shutil.rmtree() command.

                """That is why the Training_Raw_files_validated folder in root dir of this project is empty bcoz we delete
                   the content inside it."""
                path = 'Training_Raw_files_validated/'
                if os.path.isdir(path + 'Bad_Raw/'): # if this folder Bad_Raw already exists inside the
                                                    # 'Training_Raw_files_validated/' path, we delete it
                    shutil.rmtree(path + 'Bad_Raw/')
                self.logger.log(file,"Bad Raw Data Folder Deleted successfully!!")
                file.close()
        except Exception as e:
            file = open("Training_Logs/GeneralLog.txt", 'a+')
            self.logger.log(file, "Error while moving bad files to archive:: %s" % e)
            file.close()
            raise e




    def validationFileNameRaw(self,regex,LengthOfDateStampInFile,LengthOfTimeStampInFile):
        """
                    Method Name: validationFileNameRaw
                    Description: This function validates the name of the training csv files as per given name in the schema!
                                 Regex pattern is used to do the validation.If name format do not match the file is moved
                                 to Bad Raw Data folder else in Good raw data.
                    Output: None
                    On Failure: Exception

                """


        # Good and bad raw data folders are temporary folders bcoz we are using them only till insertion in database
        # and deleting them there and then after.
        # These 2 below functions called are simple functions made above in this same class to delete the existing
        # good and bad folders.
        self.deleteExistingBadDataTrainingFolder()
        self.deleteExistingGoodDataTrainingFolder()
        # below function createDirectoryForGoodBadRawData() is of this same class and it just creates new empty
        # directories/folders for the new good and bad data after deletion of previous as done above.
        self.createDirectoryForGoodBadRawData()

        # self.Batch_Directory is path initialized above and it represents the path of Training_Batch_files folder which
        # contains all data sent by client in different batches.
        onlyfiles = [f for f in listdir(self.Batch_Directory)] # we are traversing through all those files and listing them
                                                                  # out as a list stored in variable named onlyfiles.
        try:
            f = open("Training_Logs/nameValidationLog.txt", 'a+') # for logging, we have this file in that old same
            for filename in onlyfiles:              # folder Training_Logs
                # if below regex condition matched, only then flow goes to below regex validation, or else
                # flow jumps to else at bottom where data moved to bad data folder after failing validation.
                if (re.match(regex, filename)): # regex arguement passed above in this function, we are just matching
                                               # names of all files in Training_Batch_Files folder with regex condition
                                               # whether they match or not.
                                               # regex arguement computed using above function manualRegexCreation()
                                               # which was called in the training_Validation_Insertion.py file

                    # e.g. if file name = fraudDetection_021119920_010222.csv ,then 1st we get list as shown below.
                    splitAtDot = re.split('.csv', filename) # ['fraudDetection_021119920_010222','csv']
                    splitAtDot = (re.split('_', splitAtDot[0]))# splitAtDot[0] for above list is 'fraudDetection_021119920_010222'
                    #and splitting 'fraudDetection_021119920_010222' on basis of "_", we get the following list:
                    # splitAtDot = ['fraudDetection', '021119920', '010222']
                    # 1st we check length of datestamp, if it is equal to one in schema, then only check length
                    # of the timestamp, or else move to bad folder. Same process while checking length of timestamp too.
                    if len(splitAtDot[1]) == LengthOfDateStampInFile:# splitAtDot[1] is '021119920' in this case.
                        if len(splitAtDot[2]) == LengthOfTimeStampInFile:# '010222'
                            shutil.copy("Training_Batch_Files/" + filename, "Training_Raw_files_validated/Good_Raw")
                            self.logger.log(f,"Valid File name!! File moved to GoodRaw Folder :: %s" % filename)

                        else:
                            shutil.copy("Training_Batch_Files/" + filename, "Training_Raw_files_validated/Bad_Raw")
                            self.logger.log(f,"Invalid File Name!! File moved to Bad Raw Folder :: %s" % filename)
                    else:
                        shutil.copy("Training_Batch_Files/" + filename, "Training_Raw_files_validated/Bad_Raw")
                        self.logger.log(f,"Invalid File Name!! File moved to Bad Raw Folder :: %s" % filename)
                else:
                    shutil.copy("Training_Batch_Files/" + filename, "Training_Raw_files_validated/Bad_Raw")
                    self.logger.log(f, "Invalid File Name!! File moved to Bad Raw Folder :: %s" % filename)

            f.close()

        except Exception as e:
            f = open("Training_Logs/nameValidationLog.txt", 'a+')
            self.logger.log(f, "Error occured while validating FileName %s" % e)
            f.close()
            raise e




    def validateColumnLength(self,NumberofColumns):
        """
                          Method Name: validateColumnLength
                          Description: This function validates the number of columns in the csv files.
                                       It is should be same as given in the schema file.
                                       If not same file is not suitable for processing and thus is moved to Bad Raw Data folder.
                                       If the column number matches, file is kept in Good Raw Data for processing.

                          Output: None
                          On Failure: Exception

                      """
        try:
            f = open("Training_Logs/columnValidationLog.txt", 'a+')
            self.logger.log(f,"Column Length Validation Started!!")
            for file in listdir('Training_Raw_files_validated/Good_Raw/'):
                csv = pd.read_csv("Training_Raw_files_validated/Good_Raw/" + file)
                if csv.shape[1] == NumberofColumns: # very simple, just check if no. of columns in data are equal
                    pass                           # to the number specified in the schema.
                else:              # or else, move to bad data folder.
                    shutil.move("Training_Raw_files_validated/Good_Raw/" + file, "Training_Raw_files_validated/Bad_Raw")
                    self.logger.log(f, "Invalid Column Length for the file!! File moved to Bad Raw Folder :: %s" % file)
            self.logger.log(f, "Column Length Validation Completed!!")
        except OSError:
            f = open("Training_Logs/columnValidationLog.txt", 'a+')
            self.logger.log(f, "Error Occured while moving the file :: %s" % OSError)
            f.close()
            raise OSError
        except Exception as e:
            f = open("Training_Logs/columnValidationLog.txt", 'a+')
            self.logger.log(f, "Error Occured:: %s" % e)
            f.close()
            raise e
        f.close()

    def validateMissingValuesInWholeColumn(self):
        """
                                  Method Name: validateMissingValuesInWholeColumn
                                  Description: This function validates if any column in the csv file has all values missing.
                                               If all the values are missing, the file is not suitable for processing.
                                               SUch files are moved to bad raw data.
                                  Output: None
                                  On Failure: Exception


                              """
        try:
            f = open("Training_Logs/missingValuesInColumn.txt", 'a+')
            self.logger.log(f,"Missing Values Validation Started!!")

            for file in listdir('Training_Raw_files_validated/Good_Raw/'):
                csv = pd.read_csv("Training_Raw_files_validated/Good_Raw/" + file)
                count = 0
                for columns in csv:
                    # len(csv[columns] gives size of a column i.e. no. of possible rows
                    # csv[columns].count() gives count of values inside each column, if difference between both
                    # is equal to len(csv[columns], then it means that all values are missing null.
                    if (len(csv[columns]) - csv[columns].count()) == len(csv[columns]):
                        count+=1   #count of such column taken and recorded whose all values missing null.

                        # as per above condition, if there is even 1 such column having all NaN's, then whole data
                        # sent to Bad data folder.
                        shutil.move("Training_Raw_files_validated/Good_Raw/" + file,
                                    "Training_Raw_files_validated/Bad_Raw")

                        self.logger.log(f,"Invalid Column for the file!! File moved to Bad Raw Folder :: %s" % file)
                        break
                if count==0:
                    csv.rename(columns={"Unnamed: 0": "Wafer"}, inplace=True)
                    csv.to_csv("Training_Raw_files_validated/Good_Raw/" + file, index=None, header=True)
        except OSError:
            f = open("Training_Logs/missingValuesInColumn.txt", 'a+')
            self.logger.log(f, "Error Occured while moving the file :: %s" % OSError)
            f.close()
            raise OSError
        except Exception as e:
            f = open("Training_Logs/missingValuesInColumn.txt", 'a+')
            self.logger.log(f, "Error Occured:: %s" % e)
            f.close()
            raise e
        f.close()












