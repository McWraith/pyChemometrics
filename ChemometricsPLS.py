from sklearn.base import RegressorMixin
from sklearn.cross_decomposition.pls_ import PLSRegression, _PLS
from sklearn.pipeline import Pipeline
from sklearn.model_selection import BaseCrossValidator, KFold
import pandas as pds
from sklearn.base import BaseEstimator, TransformerMixin
import numpy as np
from sklearn.base import clone
from ChemometricsScaler import ChemometricsScaler
import copy


__author__ = 'gd2212'


class ChemometricsPLS(BaseEstimator, RegressorMixin, TransformerMixin):

    def __init__(self, ncomps=2, pls_algorithm=PLSRegression, xscaler=ChemometricsScaler(), yscaler=None, metadata=None,**pls_type_kwargs):
        """

        :param ncomps:
        :param pls_algorithm:
        :param scaling:
        :param metadata:
        :param pls_type_kwargs:
        """
        try:

            # Metadata assumed to be pandas dataframe only
            if (metadata is not None) and (metadata is not isinstance(metadata, pds.DataFrame)):
                raise TypeError("Metadata must be provided as pandas dataframe")

            # Perform the check with is instance but avoid abstract base class runs. PCA needs number of comps anyway!
            pls_algorithm = pls_algorithm(n_components=ncomps)
            if not isinstance(pls_algorithm, (BaseEstimator, _PLS)):
                raise TypeError("Scikit-learn model please")
            if not isinstance(xscaler, TransformerMixin) or xscaler is None:
                raise TypeError("Scikit-learn Transformer-like object or None")
            if not isinstance(yscaler, TransformerMixin) or yscaler is None:
                raise TypeError("Scikit-learn Transformer-like object or None")
            # Force scaling to false, as this will be handled by the provided scaler
            self.pls_algorithm = pls_algorithm(ncomps, scale=False, **pls_type_kwargs)

            # Most initialized as None, before object is fitted.
            self.scores_t = None
            self.scores_u = None
            self.weights = None
            self.loadings_p = None
            self.loadings_c = None
            self._ncomps = None
            self.ncomps = ncomps
            self._x_scaler = None
            self._y_scaler = None
            self.x_scaler = xscaler
            self.y_scaler = yscaler
            self.cvParameters = None
            self.modelParameters = None
            self._isfitted = False

        except TypeError as terp:
            print(terp.args[0])
        except ValueError as verr:
            print(verr.args[0])

    def fit(self, x, y, **fit_params):
        """
        Fit function. Acts exactly as in scikit-learn, but
        :param x:
        :param scale:
        :return:

        """
        try:
            # This scaling check is always performed to ensure running model with scaling or with scaling == None
            # always give consistent results (same type of data scale expected for fitting,
            # returned by inverse_transform, etc
            if self.x_scaler is not None:
                xscaled = self.x_scaler.fit_transform(x)
            else:
                xscaled = x
            if self.y_scaler is not None:
                yscaled = self.y_scaler.fit_transform(y)
            else:
                yscaled = y

            self.pls_algorithm.fit(xscaled, yscaled, **fit_params)
            self.scores_t = self.transform(xscaled)
            self.loadings_p = self.pls_algorithm.x_loadings_
            self.loadings_c = self.pls_algorithm.y_loadings_
            self.weights = self.pls_algorithm.x_weights_
            self.modelParameters = {'R2Y': self.pca_algorithm.explained_variance_, 'R2X': self.pca_algorithm.explained_variance_ratio_}
            self._isfitted = True

        except Exception as exp:
            raise exp

    def fit_transform(self, x, **fit_params):
        """
        Combination of fit and output the scores, nothing special
        :param x: Data to fit
        :param fit_params:
        :return:
        """
        try:
            self.fit(x, **fit_params)
            return self.transform(x)
        except Exception as exp:
            raise exp

    def transform(self, x, **transform_kwargs):
        """
        Calculate the projection of the data into the lower dimensional space
        TO DO as Pls does not contain this...
        :param x:
        :return:
        """

        if self.x_scaler is not None:
            xscaled = self.x_scaler.fit_transform(x)
        else:
            xscaled = x
        if self.y_scaler is not None:
            yscaled = self.y_scaler.fit_transform(y)
        else:
            yscaled = y

        return self.pls. algorithm.transform(xscaled, **transform_kwargs)

    def inverse_transform(self, scores):
        """

        :param scores:
        :return:
        """
        if self.x_scaler is not None:
            xscaled = self.x_scaler.fit_transform(x)
        else:
            xscaled = x
        if self.y_scaler is not None:
            yscaled = self.y_scaler.fit_transform(y)
        else:
            yscaled = y

        return self._model.inverse_transform(scores)

    def score(self, x, y, sample_weight=None):
        """

        :param x:
        :param sample_weight:
        :return:
        """
        # Check this
        r2x = self._model.score(x, y)
        r2y = self._model.score(y, x)

        return None

    def predict(self, x=None, y=None):
        try:
            if x is None:
                self.scores_u
                predicted = 1
            if y is None:
                self.scores_t
                predicted = 1
            return predicted

        except Exception as exp:
            raise exp

    @property
    def ncomps(self):
        """
        Getter for number of components
        :param ncomps:
        :return:
        """
        try:
            return self._ncomps
        except AttributeError as atre:
            raise atre

    @ncomps.setter
    def ncomps(self, ncomps=1):
        """
        Setter for number of components
        :param ncomps:
        :return:
        """
        # To ensure changing number of components effectively resets the model
        try:
            self._ncomps = ncomps
            self.pls_algorithm = clone(self.pls_algorithm, safe=True)
            self.pls_algorithm.n_components = ncomps
            self.modelParameters = None
            self.loadings_p = None
            self.scores_t = None
            self.scores_u = None
            self.loadings_c = None
            self.weights = None
            self.cvParameters = None

            return None
        except AttributeError as atre:
            raise atre

    @property
    def x_scaler(self):
        """
        Getter for the model scaler
        :return:
        """
        try:
            return self._x_scaler
        except AttributeError as atre:
            raise atre

    @x_scaler.setter
    def x_scaler(self, scaler):
        """
        Setter for the model scaler
        :param scaler:
        :return:
        """
        try:
            if not isinstance(scaler, TransformerMixin) or scaler is None:
                raise TypeError("Scikit-learn Transformer-like object or None")
            self._x_scaler = scaler
            self.pls_algorithm = clone(self.pls_algorithm, safe=True)
            self.modelParameters = None
            self.cvParameters = None
            self.loadings_p = None
            self.weights = None
            self.loadings_c = None
            self.scores_t = None
            self.scores_u = None
            return None
        except AttributeError as atre:
            raise atre
        except TypeError as typerr:
            raise typerr

    @property
    def y_scaler(self):
        """
        Getter for the model scaler
        :return:
        """
        try:
            return self._y_scaler
        except AttributeError as atre:
            raise atre

    @y_scaler.setter
    def y_scaler(self, scaler):
        """
        Setter for the model scaler
        :param scaler:
        :return:
        """
        try:
            if not isinstance(scaler, TransformerMixin) or scaler is None:
                raise TypeError("Scikit-learn Transformer-like object or None")
            self._y_scaler = scaler
            self.pls_algorithm = clone(self.pls_algorithm, safe=True)
            self.modelParameters = None
            self.cvParameters = None
            self.loadings_p = None
            self.weights = None
            self.loadings_c = None
            self.scores_t = None
            self.scores_u = None
            return None
        except AttributeError as atre:
            raise atre
        except TypeError as typerr:
            raise typerr

    @property
    def VIP(self):
        try:
            return None
        except AttributeError as atre:
            raise AttributeError("Model not fitted")

    @property
    def regression_coefficients(self):
        try:
            #np.dot(np.dot(self.weights.T, self.weights))
            return None
        except AttributeError as atre:
            raise AttributeError("Model not fitted")

    @property
    def w_SIMPLS(self):
        try:
            # np.dot(np.dot(self.weights.T, self.weights))
            return None
        except AttributeError as atre:
            raise AttributeError("Model not fitted")

    @property
    def hotelling_T2(self, comps):
        try:
            return None
        except AttributeError as atre:
            raise atre
        except ValueError as valerr:
            raise valerr
        except TypeError as typerr:
            raise typerr

    def cross_validation(self, x, y,  method=KFold(7, True), outputdist=False, bro_press=True,**crossval_kwargs):
        """
        # Check this one carefully ... good oportunity to build in nested cross-validation
        # and stratified k-folds
        :param data:
        :param method:
        :param outputdist: Output the whole distribution for (useful when Bootstrapping is used)
        :param crossval_kwargs:
        :return:
        """

        try:
            if not isinstance(method, BaseCrossValidator):
                raise TypeError("Scikit-learn cross-validation object please")

            Pipeline = ([('scaler', self.scaler), ('pca', self._model)])

            # Check if global model is fitted... and if not, fit using x
            # Initialise predictive residual sum of squares variable
            press = 0
            # Calculate Sum of Squares SS
            ss_x = 0
            ss_y = 0
            P = []
            T = []
            W = []
            U = []
            # As assessed in the test set..., opossed to PRESS
            R2X = []
            R2Y = []

            for xtrain, xtest in KFold.split(x):
                Pipeline.fit_transform(xtest)
                if bro_press:
                    for var in range(0, xtest.shape[1]):
                        xpred = Pipeline.predict(xtest, var)
                        press += 1
                else:
                    xpred = Pipeline.fit_transform(xtest)
                    press += 1
                #    Pipeline.predict(xtopred)
            # Introduce loop here to align loadings due to sign indeterminacy.
            # Introduce loop here to align loadings due to sign indeterminacy.
            for cvround in range(0,KFold.n_splits(x)):
                for cv_comploadings in loads:
                    choice = np.argmin(np.array([np.sum(np.abs(self.loadings - cv_comploadings)), np.sum(np.abs(self.loadings[] - cv_comploadings * -1))]))
                    if choice == 1:
                        -1*choice

            # Calculate total sum of squares
            q_squared = 1 - (press/ss)
            # Assemble the stuff in the end


            self.cvParameters = {}

            return None

        except TypeError as terp:
            raise terp

    def permute_test(self, nperms = 1000, crossVal=KFold(7, True)):
        #permuted
        for perm in range(0, nperms):

        return None

    def score_plot(self, lvs=[1,2], scores="T"):

        return None

    def coeffs_plot(self, lv=1, coeffs='weights'):
        return None


