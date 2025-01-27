import os
import copy
import cPickle
from pandas import DataFrame, concat

import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Prediction:

    def __init__(self, settings, model_path):
        self.settings = settings
        
        import keras
        logger.info("Using keras" + keras.__version__)
        from KerasModel import KerasObject as modelObject
        self.model = modelObject(filename=model_path)    

    def get_prediction_data_frame(self, data_frame, keep=[]):
        logger.debug("Predicting...")
        prediction_folds = self.get_prediction_folds_for_data_frame(data_frame, keep=keep)
        logger.debug("Concatenating prediction folds...")
        prediction = self.recombine_into_data_frame(prediction_folds)
        for prediction_fold in prediction_folds:
            prediction_fold.drop(prediction_fold.index, inplace=True)
        return prediction

    def recombine_into_data_frame(self, folds):
        logger.debug( "Entering recombine_into_data_frame...")
        all_zero = True
        for prediction_fold in folds:
            if len(prediction_fold) > 0:
                all_zero = False
        if not all_zero:
            return concat(folds)
        else:
            return DataFrame()        
        
        #### core ####
        
    def get_prediction_folds_for_data_frame(self, data_frame, keep=[]):
        self.modify_for_prediction(data_frame)
        # this is a copy
        folds = self.split_in_folds(data_frame)
        
        #TODO: drop original data_frame
        data_frame.drop(data_frame.index, inplace=True)

        prediction = self.get_prediction_folds_for_folds(folds, keep=keep)
        return prediction
    
    def get_prediction_folds_for_folds(self, folds, keep=[]):
        unscaled = copy.deepcopy(folds)
        prediction = self.model.predict(unscaled)
        unscaled[0].drop(unscaled[0].index, inplace=True)
        unscaled[1].drop(unscaled[1].index, inplace=True)
            
        if keep:
            logger.debug("keep specified")
            for i, prediction_fold in enumerate(prediction):
                # append "keep" columns from original data_frame to prediction if they exist
                try:
                    logger.debug("loc")
                    original_df_columns = folds[i].loc[:, keep]
                    logger.debug("keep columns: " + str(original_df_columns))
                    logger.debug("join")
                    prediction_fold = prediction_fold.join(original_df_columns)
                    prediction[i] = prediction_fold
                    logger.debug(prediction_fold)
                except KeyError:
                    logger.debug("Specified column labels not found in data frame")
                    raise KeyError
        else:
            logger.debug("keep not specified")

        logger.debug("Prediction before dropping: " + str(prediction))

        # dropping these does not affect the original data frame
        folds[0].drop(folds[0].index, inplace=True)
        folds[1].drop(folds[1].index, inplace=True)

        return prediction
    
    @staticmethod
    def split_in_folds(data_frame):
        folds = [data_frame.query("abs(evt % 2) != 0 ").reset_index(drop=True),
                 data_frame.query("abs(evt % 2) == 0 ").reset_index(drop=True)]
        return folds

    def modify_for_prediction(self, DF):
        DF["evt"] = DF["evt"].astype('int64')

        if self.settings.era == "2016":
            DF.replace({"jdeta": -10.}, -1., inplace=True)
            DF.replace({"mjj": -10.}, -11., inplace=True)
            DF.replace({"dijetpt": -10.}, -11., inplace=True)

            DF.eval("jdeta =   (njets < 2) *-1  + (njets > 1 )*jdeta ", inplace=True)
            DF.eval("mjj =     (njets < 2) *-11 + (njets > 1 )*mjj ", inplace=True)
            DF.eval("dijetpt = (njets < 2) *-11 + (njets > 1 )*dijetpt ", inplace=True)
            DF.eval("jpt_1 =   (njets == 0)*-10 + (njets > 0 )*jpt_1 ", inplace=True)
            DF.eval("jpt_2 =   (njets < 2 )*-10 + (njets > 1 )*jpt_2 ", inplace=True)

        if self.settings.era == "2017":
            DF.replace({"jdeta": -1.}, -10., inplace=True)
            DF.replace({"mjj": -11.}, -10., inplace=True)
            DF.replace({"dijetpt": -11.}, -10., inplace=True)

            DF.eval("jdeta =   (njets < 2) *-10 + (njets > 1 )*jdeta ", inplace=True)
            DF.eval("mjj =     (njets < 2) *-10 + (njets > 1 )*mjj ", inplace=True)
            DF.eval("dijetpt = (njets < 2) *-10 + (njets > 1 )*dijetpt ", inplace=True)
            DF.eval("jpt_1 =   (njets == 0)*-10 + (njets > 0 )*jpt_1 ", inplace=True)
            DF.eval("jpt_2 =   (njets < 2 )*-10 + (njets > 1 )*jpt_2 ", inplace=True)

