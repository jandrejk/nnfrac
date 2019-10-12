import os
import cPickle
from pandas import DataFrame, concat

from CorePrediction import CorePrediction

import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class PredictionWrapper:

    def __init__(self, settings):
        self.settings = settings
        self.scaler = 0
        self.model = 0

    def setup(self, model_path, scaler_path):
        if self.settings.scaler == "standard":
            if os.path.exists(scaler_path):
                logger.debug("Loading Scaler")
                with open(scaler_path, "rb") as FSO:
                    tmp = cPickle.load(FSO)
                    self.scaler = [tmp, tmp]
            else:
                logger.critical("Fatal: Scaler file not found at {0}. Train model using -t first.".format(
                    scaler_path))
                return
            
        import keras
        logger.info("Using keras" + keras.__version__)
        from KerasModel import KerasObject as modelObject

        self.model = modelObject(filename=model_path)

    @staticmethod
    def splitInFolds(data_frame):
        return CorePrediction.splitInFolds(data_frame)

    def get_prediction_folds(self, data_frame, keep=[]):
        logger.debug("in CorePrediction::get_prediction_folds")
        logger.debug("scaler: " + str(self.scaler))
        prediction_handler = CorePrediction(self.settings)
        prediction_handler.setup(self.settings, self.model, self.scaler)

        logger.debug("Got DataFrame, predicting...")
        prediction = prediction_handler.get_prediction_folds_for_data_frame(data_frame, keep=keep)
        return prediction

    def get_prediction_data_frame(self, data_frame, keep=[]):
        prediction_folds = self.get_prediction_folds(data_frame, keep)
        logger.debug("Got prediction folds, concatenating...")
        pred_concat = self.combineFoldsIntoDataFrame(prediction_folds)
        for prediction_fold in prediction_folds:
            prediction_fold.drop(prediction_fold.index, inplace=True)
        return pred_concat

    def combineFoldsIntoDataFrame(self, pred):
        logger.debug( "in combineFoldsIntoDataFrame...")
        all_zero = True
        for prediction_fold in pred:
            if len(prediction_fold) > 0:
                all_zero = False
        if not all_zero:
            return concat(pred)
        else:
            return DataFrame()

