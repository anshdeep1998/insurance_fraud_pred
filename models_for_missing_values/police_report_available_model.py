import pandas as pd
import numpy as np
import os
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import GridSearchCV
from feature_engine.imputation import CategoricalImputer
from sklearn.metrics import accuracy_score
import pickle


class model_police_report_available:
    def __init__(self, data_path, model_save_path):
        self.data_path = data_path
        self.data_missing_values = pd.read_csv(data_path)
        self.model_save_path = model_save_path

    def X_features(self):
        Missing_model_X = self.data_missing_values.drop(['police_report_available'], axis=1)
        imputer = CategoricalImputer(imputation_method='frequent')
        Missing_model_X['collision_type'] = imputer.fit_transform(Missing_model_X[['collision_type']])
        Missing_model_X['property_damage'] = imputer.fit_transform(Missing_model_X[['property_damage']])
        return Missing_model_X

    def Y_features(self):
        Missing_model_Y = self.data_missing_values['police_report_available']
        return Missing_model_Y

    def encoding(self):
        Missing_model_X = self.X_features()
        cat_df = Missing_model_X.select_dtypes(include=['object']).copy()
        cat_df['policy_csl'] = cat_df['policy_csl'].map({'100/300': 1, '250/500': 2.5, '500/1000': 5})
        cat_df['insured_education_level'] = cat_df['insured_education_level'].map(
            {'JD': 1, 'High School': 2, 'College': 3, 'Masters': 4, 'Associate': 5, 'MD': 6, 'PhD': 7})
        cat_df['incident_severity'] = cat_df['incident_severity'].map(
            {'Trivial Damage': 1, 'Minor Damage': 2, 'Major Damage': 3, 'Total Loss': 4})
        cat_df['insured_sex'] = cat_df['insured_sex'].map({'FEMALE': 0, 'MALE': 1})
        cat_df['property_damage'] = cat_df['property_damage'].map({'NO': 0, 'YES': 1})
        # cat_df['police_report_available'] = cat_df['police_report_available'].map({'NO' : 0, 'YES' : 1})
        cat_df['fraud_reported'] = cat_df['fraud_reported'].map({'N': 0, 'Y': 1})

        for col in cat_df.drop(
                columns=['policy_csl', 'insured_education_level', 'incident_severity', 'insured_sex', 'property_damage',
                         'fraud_reported']).columns:
            cat_df = pd.get_dummies(cat_df, columns=[col], prefix=[col], drop_first=True)

        return cat_df

    def prepare_merge_data(self):
        cat_df = self.encoding()
        num_df = self.data_missing_values.select_dtypes(include=['int64']).copy()
        final_df_missing_model = pd.concat([num_df, cat_df], axis=1)
        return final_df_missing_model

    def indices(self):
        Missing_model_Y = self.Y_features()
        train_indices = []
        prediction_indices = []
        for i in range(Missing_model_Y.isnull().shape[0]):
            if Missing_model_Y.isnull()[i] == False:
                train_indices.append(i)
            else:
                prediction_indices.append(i)

        return train_indices, prediction_indices

    def segregation_of_data(self):
        train_indices, prediction_indices = self.indices()
        final_df_missing_model = self.prepare_merge_data()
        dataset_to_train = final_df_missing_model.iloc[train_indices]
        prediction_data = final_df_missing_model.iloc[prediction_indices]
        Missing_model_Y = self.Y_features()
        Y_to_train = Missing_model_Y.iloc[train_indices]
        Y_to_predict = Missing_model_Y.iloc[prediction_indices]
        X_train, X_test, y_train, y_test = train_test_split(dataset_to_train, Y_to_train, test_size=0.2,
                                                            random_state=42)

        return X_train, X_test, y_train, y_test

    def model_training(self):
        X_train, X_test, y_train, y_test = self.segregation_of_data()
        clf = DecisionTreeClassifier()
        params = {'max_depth': list(range(2, 10, 2)),
                  'min_samples_split': list(range(2, 20, 2)),
                  'min_samples_leaf': list(range(1, 10))}

        gcv = GridSearchCV(estimator=clf, param_grid=params)
        gcv.fit(X_train, y_train)

        pickle.dump(gcv, open(self.model_save_path, "wb"))
        y_pred = gcv.predict(X_test)
        return accuracy_score(y_test, y_pred)

    def predicted_values(self):
        Accuracy_score = self.model_training()
        # load model
        loaded_model = pickle.load(open(self.model_save_path, "rb"))
        final_df_missing_model = self.prepare_merge_data()
        train_indices, prediction_indices = self.indices()
        prediction_data = final_df_missing_model.iloc[prediction_indices]
        y_missing_predicted = loaded_model.predict(prediction_data)
        X_train, X_test, y_train, y_test = self.segregation_of_data()
        # print("Accuracy is: ", Accuracy_score * 100, " %")
        return y_missing_predicted

    def filled_column_to_replace(self):  # Only this class method to be called once
        Missing_model_Y = self.Y_features()
        y_missing_predicted = self.predicted_values()
        x = 0
        for i in Missing_model_Y:
            if i != 'YES' and i != 'NO':
                Missing_model_Y.replace(to_replace=i, value=y_missing_predicted[x], inplace=True)
                x += 1
        Missing_model_Y.to_csv(
            r"C:\Users\Anshdeep\OneDrive\Desktop\Ineuron\Full stack data science course\Python projects\fraudDetection\models_for_missing_values\Police_report_available_imputed.csv")
        return Missing_model_Y

