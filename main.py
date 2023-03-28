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

app = Flask(__name__)
dashboard.bind(app)
CORS(app)

""" Route specifies that control should go where. E.g. whenever we do training, control should go to train route.
   Using route, we can specify/use different functionalities into same python file. There are 3 such routes in this
   file i.e. home route, prediction route and training route. Functionalities provided by these routes are:
                              i) rendering the template done above. 
                              ii) doing prediction using predict route
                              iii) doing training using train route.

    For very detailed explanation of these routes, refer register notes."""


# These routes enable 1 same python application i.e. main.py in our case to perform different jobs/functionalities.
# These routes provided along with the URL of the application.

# All 3 routes are specified with code implementation below.

# 1) This below is the home route which calls the web UI i.e. index.html page for UI below.
@app.route("/", methods=['GET'])
@cross_origin()
def home():
    return render_template('index_n.html')

"""When we click on by default URL http://127.0.0.1:5001/, it calls by default home route until /predict or /train specified.
   For calling predict and train routes, we need to specify /predict and /train respectively, but when we go through the html code
   inside index_n.html, we notice that when button from frontend is clicked, the /predict route called which is specified there in
   html code. Calling /predict route takes input as path of Prediction_Batch_Files folder in root dir for validation and this path
   is already specified in html file."""

# 2) this below is the prediction route which is called at the time of prediction.
@app.route("/predict", methods=['POST'])
@cross_origin()
def predictRouteClient():# predict route as explained in register notes that which starts prediction when called.
    try:
        if request.json is not None:  # This condition is called when we are testing our API through Postman.
                                    # request.json i.e through postman should not be None, else exception raised.

            path = request.json['filepath'] # This is the path of location where client has kept data on which
                                            # we have to do validation and prediction which is the path of batch files inside
                                            # the Predicition_Batch_files folder.

                                    # and this path is passed in the code of html file.


            pred_val = pred_validation(path) # pred_validation class imported from prediction_Validation_Insertion.py file
                                             # in root dir.
                            # In this object of pred_validation() class, we just pass the path to the files to be
                            # validated.
                            # In this, the path of folder Prediction_Batch_Files will be passed bcoz this class is for data validation
                            # to check no. of columns, their datatypes and names of each batch file sent by client, if any batch
                            # fails the validation is sent to bad data folder and deleted or else if batch file passes the validation,
                            # it is sent to database for all data aggregation.

            pred_val.prediction_validation() # data in sent in batches from client in the Prediction_Batch_files folder
                        # First of all file names of all that is validated ie. each batch file here for prediction such that
                        # name of file is in correct format.
                        # then, no. of columns validated, '' converted to "" to make it insertable in database.
                        # Then insert into database so that all prediction batch files are aggregated together.
                        # Then all aggregated data exported as csv into the Prediction_FileFromDB folder as InputFilecsv.




            pred = prediction(path) # object of Prediction class from predictFromModel.py file in root dir.

            # predicting for the data.
            # this function predictionFromModel() called.
            """It includes data preprocessing for the prediction data, then making different clusters out of that whole data,
               load the already saved models, do predictions and save predictions as csv in the Prediction_Output_File
               folder in the root dir.
               """
                   # ctrl+click for explain
            path = pred.predictionFromModel() # THis is the path of Predictions.csv in Prediction_Output_File folfer in root dir.
                                              # This path will be printed in the frontend.
            return Response("Prediction File created at %s!!!" % path)

        elif request.form is not None: # This condition is called when we our testing our API from web GUI/ frontend.
                                     # request.form i.e through postman should not be None, else exception raised.

            path = request.form['filepath'] # This is the path of location where client has kept data on which
                                            # we have to do prediction  which is the path of batch files inside
                                            # the Predicition_Batch_files folder.

            pred_val = pred_validation(path) #object initialization

            pred_val.prediction_validation() #calling the prediction_validation function

            pred = prediction(path) #object initialization

            # predicting for dataset present in database
            path = pred.predictionFromModel()
            return Response("Prediction File created at %s!!!" % path)

    except ValueError:
        return Response("Error Occurred! %s" %ValueError)
    except KeyError:
        return Response("Error Occurred! %s" %KeyError)
    except Exception as e:
        return Response("Error Occurred! %s" %e)


""" As we studied above that clicking on url calls default home route, to call train and predict route, we will use postman
    i.e. flow will go to if request.json['folderPath'] is not None condition."""


@app.route("/train", methods=['POST'])
@cross_origin()
def trainRouteClient(): # In the training route, we are doing validation first and then we come to the actual training.
                      # Explained well in the register notes.

    try:
        if request.json['folderPath'] is not None:
            path = request.json['folderPath']# This is the path of location where client has kept data on which
                                            # we have to do training which is the path of batch files inside
                                            # the Training_Batch_files folder.
            # FOr doing validation first and then the actual training, we have 2 classes i.e. train_validation
            # and trainModel().

            train_valObj = train_validation(path) #object initialization for validation of data.
                                                  #Validation includes checking the names and datatypes of all columns.
            # This is the train_validation class in the training_Validation_Insertion.py in root dir.
            # In this, the path of folder Training_Batch_Files will be passed bcoz this class is for data validation
            # to check no. of columns, their datatypes and names of each batch file sent by client, if any batch
            # fails the validation is sent to bad data folder and deleted or else if batch file passes the validation,
            # it is sent to database for all data aggregation.

            train_valObj.train_validation() # calling the training_validation function.

               # Data now inserted in database and then exported to csv.

            trainModelObj = trainModel() #object initialization of trainModel class in trainingModel.py in root dir.
            trainModelObj.trainingModel() #training the model for the files in the table


    except ValueError:

        return Response("Error Occurred! %s" % ValueError)

    except KeyError:

        return Response("Error Occurred! %s" % KeyError)

    except Exception as e:

        return Response("Error Occurred! %s" % e)
    return Response("Training successful!!")


""" Calling /train and /predict routes in postman:
    open postman, open new tab->click on raw and select input type as json to send input as json.
    
    1) Calling /predict: select method as POST as it was specified above, pass path as http://127.0.0.1:5001/train
       and pass the path of Prediction_Batch_Files.
       like done as follows:
       {
       "filepath":"Prediction_Batch_Files"
       }
    2) calling /train: same process as above, pass path as http://127.0.0.1:5001/predict and pass the path of Training_Batch_Files.
       {
       "folderPath":"Training_Batch_Files"
       }
       
    Calling these in postman can do training and prediction.
    From frontend, we can only call home route.
       """

port = int(os.getenv("PORT",5001))
if __name__ == "__main__":
    app.run(port=port,debug=True)
