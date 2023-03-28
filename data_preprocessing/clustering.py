import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from kneed import KneeLocator
from file_operations import file_methods

class KMeansClustering:
    """
            This class shall  be used to divide the data into clusters before training.

            """

    def __init__(self, file_object, logger_object):
        self.file_object = file_object
        self.logger_object = logger_object

    def elbow_plot(self,data):
        """
                        Method Name: elbow_plot
                        Description: This method saves the plot to decide the optimum number of clusters to the file.
                        Output: A picture saved to the directory
                        On Failure: Raise Exception
                """
        # This function saves the elbow plot as studied many times before as PNG in the preprocessing_data folder
        # in the root directory where the null_values.csv was saved.
        # and in the end also returns the optimal K value.
        self.logger_object.log(self.file_object, 'Entered the elbow_plot method of the KMeansClustering class')
        wcss=[] # initializing an empty list
        try:
            for i in range (1,11):
                kmeans=KMeans(n_clusters=i,init='k-means++',random_state=42) # initializing the KMeans object
                kmeans.fit(data) # fitting the data to the KMeans Algorithm
                wcss.append(kmeans.inertia_)
            plt.plot(range(1,11),wcss) # creating the graph between WCSS and the number of clusters
            plt.title('The Elbow Method')
            plt.xlabel('Number of clusters')
            plt.ylabel('WCSS')
            #plt.show()
            plt.savefig('preprocessing_data/K-Means_Elbow.PNG') # saving the elbow plot locally
            # finding the value of the optimum cluster programmatically

            # out of wcss list, we select best K using KneeLocator()
            self.kn = KneeLocator(range(1, 11), wcss, curve='convex', direction='decreasing')
            self.logger_object.log(self.file_object, 'The optimum number of clusters is: '+str(self.kn.knee)+' . Exited the elbow_plot method of the KMeansClustering class')
            return self.kn.knee

        except Exception as e:
            self.logger_object.log(self.file_object,'Exception occured in elbow_plot method of the KMeansClustering class. Exception message:  ' + str(e))
            self.logger_object.log(self.file_object,'Finding the number of clusters failed. Exited the elbow_plot method of the KMeansClustering class')
            raise Exception()

    def create_clusters(self,data,number_of_clusters):
        """
                                Method Name: create_clusters
                                Description: Create a new dataframe consisting of the cluster information.
                                Output: A datframe with cluster column
                                On Failure: Raise Exception

                        """
        self.logger_object.log(self.file_object, 'Entered the create_clusters method of the KMeansClustering class')
        self.data=data
        try:
            # no.of clusters were computed by the above
            # function .elbow_plot() which are passed in the below KMeans() model as an arguement.
            # init = kmeans++ ensures that clusters don't depend on the centroid initialization as studied in register notes.
            self.kmeans = KMeans(n_clusters=number_of_clusters, init='k-means++', random_state=42)
            #self.data = self.data[~self.data.isin([np.nan, np.inf, -np.inf]).any(1)]

            """ fit_predict() is more relevant to unsupervised or transductive estimators.
                Essentially, this method will fit and perform predictions over training data thus, is more
                appropriate when performing operations such as clustering."""

            self.y_kmeans=self.kmeans.fit_predict(data) #  divide data into clusters like cluster-0, 1, 2, 3...

                         # file_methods.py file imported above is located in file_operations folder in root dir.
             # this file_methods.py file has File_Operation class which takes the above initialized arguements
            # i.e. fle_object anf logger_object.
            self.file_op = file_methods.File_Operation(self.file_object,self.logger_object)

            # the class File_Operation() has the method .save_model() which saves this kmeans model
            # in the subfolders of models folder in root dir.
            self.save_model = self.file_op.save_model(self.kmeans, 'KMeans') # saving the KMeans model to directory
                                                                                    # passing 'Model' as the functions need three parameters
            """We are saving the clustered data and model bcoz later on when new data records from client comes to us,
               model will help us classify that new records/rows into clusters we made just now so that we can apply
               specific model to these clusters."""
            self.data['Cluster']=self.y_kmeans  # create a new column in dataset for storing the cluster information
            self.logger_object.log(self.file_object, 'succesfully created '+str(self.kn.knee)+ 'clusters. Exited the create_clusters method of the KMeansClustering class')
            return self.data
        except Exception as e:
            self.logger_object.log(self.file_object,'Exception occured in create_clusters method of the KMeansClustering class. Exception message:  ' + str(e))
            self.logger_object.log(self.file_object,'Fitting the data to clusters failed. Exited the create_clusters method of the KMeansClustering class')
            raise Exception()