import shutil
import sqlite3
from datetime import datetime
from os import listdir
import os
import csv
from application_logging.logger import App_Logger


class dBOperation:
    """
      This class shall be used for handling all the SQL operations.



      """
    def __init__(self):
        self.path = 'Training_Database/'
        self.badFilePath = "Training_Raw_files_validated/Bad_Raw"
        self.goodFilePath = "Training_Raw_files_validated/Good_Raw"
        self.logger = App_Logger()


    def dataBaseConnection(self,DatabaseName):

        """
                Method Name: dataBaseConnection
                Description: This method creates the database with the given name and if Database already exists then opens the connection to the DB.
                Output: Connection to the DB
                On Failure: Raise ConnectionError



                """
        try:
            conn = sqlite3.connect(self.path+DatabaseName+'.db')

            file = open("Training_Logs/DataBaseConnectionLog.txt", 'a+')
            self.logger.log(file, "Opened %s database successfully" % DatabaseName)
            file.close()
        except ConnectionError:
            file = open("Training_Logs/DataBaseConnectionLog.txt", 'a+')
            self.logger.log(file, "Error while connecting to database: %s" %ConnectionError)
            file.close()
            raise ConnectionError
        return conn

    def createTableDb(self,DatabaseName,column_names):
        """
                        Method Name: createTableDb
                        Description: This method creates a table in the given database which will be used to insert the Good data after raw data validation.
                        Output: None
                        On Failure: Raise Exception

                        """
        try:
            conn = self.dataBaseConnection(DatabaseName)# We have used sqllite 3 for connection bcoz it is a light databse
                                           # and an run on online server and no installation needed in our local system.
            c=conn.cursor()

            # This below sqllite query is to check if a table with name as Good_Raw_Data exists in db or not.
            c.execute("SELECT count(name)  FROM sqlite_master WHERE type = 'table'AND name = 'Good_Raw_Data'")
            if c.fetchone()[0] ==1: # 1 means that above searched table already exists.
                conn.close()
                file = open("Training_Logs/DbTableCreateLog.txt", 'a+')
                self.logger.log(file, "Tables created successfully!!")
                file.close()
                                # Just simple logging is done that table created successfully and database connection
                                # made successfully.
                file = open("Training_Logs/DataBaseConnectionLog.txt", 'a+')
                self.logger.log(file, "Closed %s database successfully" % DatabaseName)
                file.close()

            else: # else when table doesn't exist as of now.

                for key in column_names.keys(): # column_names is names of all columns to be there in this database table
                                                # and it is passed as arguement in this function.
                    type = column_names[key]

                    # in try block, we have given query to add new column so one by one in this for loop,
                    # if the table exists, then add columns to the table and if not exists, control goes to catch block
                                                # and we will create the table in this query.
                    try:
                        #cur = cur.execute("SELECT name FROM {dbName} WHERE type='table' AND name='Good_Raw_Data'".format(dbName=DatabaseName))
                        conn.execute('ALTER TABLE Good_Raw_Data ADD COLUMN "{column_name}" {dataType}'.format(column_name=key,dataType=type))
                    except:
                        conn.execute('CREATE TABLE  Good_Raw_Data ({column_name} {dataType})'.format(column_name=key, dataType=type))


                    # try:
                    #     #cur.execute("SELECT name FROM {dbName} WHERE type='table' AND name='Bad_Raw_Data'".format(dbName=DatabaseName))
                    #     conn.execute('ALTER TABLE Bad_Raw_Data ADD COLUMN "{column_name}" {dataType}'.format(column_name=key,dataType=type))
                    #
                    # except:
                    #     conn.execute('CREATE TABLE Bad_Raw_Data ({column_name} {dataType})'.format(column_name=key, dataType=type))


                conn.close()

                file = open("Training_Logs/DbTableCreateLog.txt", 'a+')
                self.logger.log(file, "Tables created successfully!!")
                file.close()

                file = open("Training_Logs/DataBaseConnectionLog.txt", 'a+')
                self.logger.log(file, "Closed %s database successfully" % DatabaseName)
                file.close()

        except Exception as e:
            file = open("Training_Logs/DbTableCreateLog.txt", 'a+')
            self.logger.log(file, "Error while creating table: %s " % e)
            file.close()
            conn.close()
            file = open("Training_Logs/DataBaseConnectionLog.txt", 'a+')
            self.logger.log(file, "Closed %s database successfully" % DatabaseName)
            file.close()
            raise e


    def insertIntoTableGoodData(self,Database):

        """
                               Method Name: insertIntoTableGoodData
                               Description: This method inserts the Good data files from the Good_Raw folder into the
                                            above created table.
                               Output: None
                               On Failure: Raise Exception

        """

        conn = self.dataBaseConnection(Database)
        goodFilePath= self.goodFilePath  # path of both good and bad data files passed in this class init.
        badFilePath = self.badFilePath   # i.e. Good_Raw and Bad_Raw in the
                                         # Training_Raw_files_validated folder in the root directory.
        onlyfiles = [f for f in listdir(goodFilePath)] # This file path contains all the csv batches files.
        log_file = open("Training_Logs/DbInsertLog.txt", 'a+')

        for file in onlyfiles: # file denotes all the csv batch files
            try:
                with open(goodFilePath+'/'+file, "r") as f: # "f" i.e. goodFilePath+'/'+file represents path of the each
                                                           # and every batch file in this whole folder.
                    next(f)     # next() takes control to next file in each and every iteration in this loop of batch files.
                    reader = csv.reader(f, delimiter="\n") #all csv batch files read using csv.reader()
                    for line in enumerate(reader): # encodes as tuple with 1st element starting as 0,1,2,3.......
                        for list_ in (line[1]): # line[1] represents each and every csv batch file's data.
                            try:                    # all that data i.e. inside variable list_ is inserted into database.
                                conn.execute('INSERT INTO Good_Raw_Data values ({values})'.format(values=(list_)))
                                self.logger.log(log_file," %s: File loaded successfully!!" % file)
                                conn.commit()
                            except Exception as e:
                                raise e

            except Exception as e:
                                      # as usual exceptions.
                conn.rollback()
                self.logger.log(log_file,"Error while creating table: %s " % e)
                shutil.move(goodFilePath+'/' + file, badFilePath)
                self.logger.log(log_file, "File Moved Successfully %s" % file)
                log_file.close()
                conn.close()

        conn.close()
        log_file.close()


    def selectingDatafromtableintocsv(self,Database):

        """
                               Method Name: selectingDatafromtableintocsv
                               Description: This method exports the data in GoodData table as a CSV file. in a given location.
                                            above created .
                               Output: None
                               On Failure: Raise Exception
        """
        # this function exports data in table to csvfile and all that clubbed data from database saved into the
        # InputFile.csv file inside the Training_FileFromDB folder inside the root directory.

        self.fileFromDb = 'Training_FileFromDB/'
        self.fileName = 'InputFile.csv'
        log_file = open("Training_Logs/ExportToCsv.txt", 'a+')
        try:
            conn = self.dataBaseConnection(Database)
            sqlSelect = "SELECT *  FROM Good_Raw_Data" # All the data from database table where good data was inserted
            cursor = conn.cursor()               # is imported.

            cursor.execute(sqlSelect)

            results = cursor.fetchall()
            # Get the headers of the csv file
            headers = [i[0] for i in cursor.description]

            #Make the CSV ouput directory
            if not os.path.isdir(self.fileFromDb): #If path for saing csv for this table data doesn't exist, so make it.
                os.makedirs(self.fileFromDb)

            # Open CSV file for writing.
            # using csv.writer(), al data inserted into csv.
            csvFile = csv.writer(open(self.fileFromDb + self.fileName, 'w', newline=''),delimiter=',', lineterminator='\r\n',quoting=csv.QUOTE_ALL, escapechar='\\')

            # Add the headers and data to the CSV file.
            csvFile.writerow(headers)
            csvFile.writerows(results)

            self.logger.log(log_file, "File exported successfully!!!")
            log_file.close()

        except Exception as e:
            self.logger.log(log_file, "File exporting failed. Error : %s" %e)
            log_file.close()





