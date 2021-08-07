from sklearn.model_selection import cross_val_score
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.decomposition import PCA
from sklearn.pipeline import make_pipeline
import pandas as pd
import numpy as np

class Tree:
    """
    Decision Tree Model
    """

    def __init__(self, name: str):
        """
        @param name: Name of the school or institution.
        @type name: str
        """

        self.name = name
        self._raw_data = pd.read_csv(name, header=None).values

        state_encoder = None
        major_encoder = LabelEncoder()

        if len(self._raw_data[0] == 5): # there's in/out state on 3rd column
            state_encoder = LabelEncoder()
            self._raw_data[:, 2] = state_encoder.fit_transform(self._raw_data[:, 2])

        # 2nd column guaranteed to be major
        self._raw_data[:, 1] = major_encoder.fit_transform(self._raw_data[:, 1])
        X, y = self._raw_data[:, 1:], self._raw_data[:, 0]
        self._pipeline = make_pipeline(StandardScaler(), DecisionTreeClassifier())
        self._score = cross_val_score(self._pipeline, X, y.astype(np.int), cv=10, n_jobs=1)

    @property
    def model(self):
        return self._pipeline._final_estimator
    
    @property
    def score(self):
        return (np.mean(self._score), np.std(self._score))
    
    @property
    def coef(self):
        self._pipeline.fit(self._raw_data[:, 1:], self._raw_data[:, 0].astype(np.int))
        return self.model.coef_