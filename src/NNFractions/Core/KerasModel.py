import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True  # disable ROOT internal argument parser
import numpy as np
from pandas import DataFrame,concat
import json
np.random.seed(0)
import conf.keras_models as keras_models
from keras.callbacks import EarlyStopping, ModelCheckpoint
from keras.models import load_model as lm
from keras.utils.np_utils import to_categorical
from collections import deque
import time
import os
import copy

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class KerasObject():

    def __init__(self, parameter_file = "", variables=[], target_names = {}, filename = "" ):

        self.variables = variables
        self.models = []

        try:
            if filename: self.load(filename)
            elif not parameter_file or not variables:
                raise Warning("Warning! Object not defined. Load from file or set 'params' and 'variables'")
            else:
                with open(parameter_file,"r") as FSO:
                    params = json.load(FSO)
                self.params = params["model"]
        except Warning as e:
            print e
            self.params = []

        if target_names: self.target_names = target_names



    def load(self, filename):
        with open(filename + ".dict", 'rb') as FSO:
            tmp_dict = json.load(FSO)

        logger.debug( "Dict located in: " + filename)
        self.__dict__.clear()
        self.__dict__.update(tmp_dict)

        self.models = []
        for modelpath in tmp_dict["models"]:
            logger.debug("filename is " + filename)
            logger.debug("path in dict is " + modelpath)
            modelname = os.path.basename(modelpath)

            dirpath = os.path.dirname(filename)
            actual_modelpath = os.path.join(dirpath, modelname)

            logger.debug("Loading model from: " + actual_modelpath)

            self.models.append(lm(actual_modelpath))

    def save(self, filename):
        placeholders = []
        tmp_models = []
        for i,model in enumerate(self.models):
            modelpath = filename + ".fold{0}".format(i)
            modelname = os.path.basename(modelpath)
            model.save(modelname)
            tmp_models.append(model)
            placeholders.append(modelname)
        self.models = placeholders

        with open(filename + ".dict", 'wb') as FSO:
            json.dump(self.__dict__, FSO)

        self.models = tmp_models


    def train(self, samples):

        if type(samples) is list:
            samples = deque(samples)

        for i in xrange( len(samples) ):
            test = samples[0]
            train = [ samples[1] ]

            for j in xrange(2, len(samples) ):
                train.append( samples[j] )
            
            train = concat(train , ignore_index=True).reset_index(drop=True)

            self.models.append( self.trainSingle( train, test ) )
            samples.rotate(-1)

        print "Finished training!"


    def trainSingle(self, train, test):


        # writing targets in keras readable shape
        best = str(int(time.time()))
        y_train = to_categorical( train["target"].values )
        y_test  = to_categorical( test["target"].values )

        N_classes = len(y_train[0])

        model_impl = getattr(keras_models, self.params["name"])
        model = model_impl(len(self.variables), N_classes)
        model.summary()
        history = model.fit(
            train[self.variables].values,
            y_train,
            sample_weight=train["train_weight"].values,
            validation_split = 0.25,
            # validation_data=(test[self.variables].values, y_test, test["train_weight"].values),
            batch_size=self.params["batch_size"],
            epochs=self.params["epochs"],
            shuffle=True,
            callbacks=[EarlyStopping(patience=self.params["early_stopping"]), ModelCheckpoint( best + ".model", save_best_only=True, verbose = 1) ])

        import matplotlib as mpl
        mpl.use('Agg')
        import matplotlib.pyplot as plt

        print "plotting training"
        epochs = xrange(1, len(history.history["loss"]) + 1)
        plt.plot(epochs, history.history["loss"], lw=3, label="Training loss")
        plt.plot(epochs, history.history["val_loss"], lw=3, label="Validation loss")
        plt.xlabel("Epoch")
        plt.ylabel("Loss")
        plt.legend()
        if not os.path.exists("plots"):
            os.mkdir("plots")
        plt.savefig("plots/fold_{0}_loss.png".format(best), bbox_inches="tight")


        print "Reloading best model"
        model = lm(best + ".model")
        os.remove( best + ".model" )

        return model

    def predict(self, samples, where=""):

        predictions = []
        if type(samples) is list:
            samples = deque(samples)

        for i in xrange(len(samples)):
            if len(samples[0]) > 0:
                predictions.append( self.testSingle( samples[0], i))
            else:
                print "Empty fold in prediction: skipping..."
            samples.rotate(-1)

        samples[0].drop(samples[0].index, inplace = True)
        samples[1].drop(samples[1].index, inplace = True)

        return predictions

    def predictAndPreserve(self, in_samples, where=""):

        samples = copy.deepcopy(in_samples)
        predictions = []
        if type(samples) is list:
            samples = deque(samples)

        for i in xrange(len(samples)):
            if len(samples[0]) > 0:
                predictions.append( self.testSingle( samples[0], i))
            else:
                print "Empty fold in prediction: skipping..."
            samples.rotate(-1)

        return predictions

    def testSingle(self, test, fold):

        prediction = DataFrame(self.models[fold].predict(test[self.variables].values))

        # note: this uses idxmax (the column header of the max value) and tries to convert it to a float
        # therefore renaming of the header should be done AFTER extracting the predicted_class
        df = DataFrame(dtype=float, data={"predicted_frac_class": prediction.idxmax(axis=1).values,
                                          "predicted_frac_prob": prediction.max(axis=1).values})

        # header renaming
        headers = []
        for i in range(0, len(prediction.columns)):
            headers.append("predicted_frac_prob_" + str(i))
        prediction.columns = headers

        # horizontal concat (adding columns)
        result = concat([prediction, df], axis=1)

        return result

