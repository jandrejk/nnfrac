from Tools.CutObject.CutObject import Cut
from Tools.VarObject.VarObject import Var
from Tools.FakeFactor.FakeFactor import FakeFactor, getEmptyHist
from Tools.Weights.Weights import Weight
from Tools.NNCore.PredictionWrapper import PredictionWrapper
from Tools.NNCore.Settings import Settings

import ROOT as R
import numpy as np
import root_numpy as rn
import root_pandas as rp

from array import array
from pandas import DataFrame, concat

import copy
import os
import json

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

#from multiprocessing import Process, Queue


def main():
    pass


class PredictionHelper:
    nn_frac_config_file = "{0}/config/default_nn_frac_config.json".format(
        "/".join(os.path.realpath(__file__).split("/")[:-1]))

    def __init__(self, channel, era, config=""):

        if config:
            self.nn_frac_config_file = config
            
        logger.info("Loading nn frac config from {0}".format(self.nn_frac_config_file))
        logger.debug("Called constructor of PredictionHelper")
        with open(self.nn_frac_config_file,"r") as FSO:
            self.nn_frac_config = json.load(FSO)

        self.channel = channel
        self.era = era
        self.prediction = None

        logger.debug("Loaded nn_frac_config")
        logger.debug(str(self.nn_frac_config))

        self.setup_prediction()

    def setup_prediction(self): 
        path_prefix = self.nn_frac_config["model"]["path_prefix"]
        model_path = os.path.join(path_prefix, self.nn_frac_config["model"]["model_path"])        

        scaler = self.nn_frac_config["model"]["scaler"]
        
        scaler_path = ""

        if scaler == "standard":
            scaler_path = os.path.join(path_prefix, self.nn_frac_config["model"]["scaler_path"])
            scaler_path = os.path.join(scaler_path, str(self.era), "StandardScaler.{0}.pkl".format(self.channel))
            logger.info("Loading scaler from {0}".format(scaler_path))

        model_path = os.path.join(model_path, str(self.era), "{0}.{1}".format(self.channel, "keras"))
        logger.info("Loading model from {0}".format(model_path))
        
        settings = Settings(self.channel, self.era, "keras", scaler)
        pred = PredictionWrapper(settings)

        pred.setup(model_path, scaler_path)
        self.prediction = pred

    def getBranchesForPrediction(self):
        variables = self.prediction.model.variables
        logger.debug(variables)
        branches = ["evt"] + variables + ["jdeta", "mjj", "dijetpt", "jpt_1", "jpt_2"]
        return list(set(branches))

    def getPredictionDataFrame(self, data_frame):
        logger.debug( "in getPredictionForDataFrame...")
        return self.prediction.get_prediction_data_frame(data_frame, "evt")


class NNFakeFactor(FakeFactor):

    nn_frac_config_file = "{0}/config/default_nn_frac_config.json".format("/".join(os.path.realpath(__file__).split("/")[:-1]))

    prediction_helper = None

    def __init__(self, channel, variable, data_file, era, add_systematics=True, debug=False, real_nominal={}, real_shifted={}):
        FakeFactor.__init__(self, channel, variable, data_file, era, add_systematics=add_systematics,
                                           debug=debug, real_nominal=real_nominal, real_shifted=real_shifted)

        self.data_file = data_file
        self.channel = channel
        
    def calc(self, cut, category="def"):
        logger.info("In calc...")
        logger.info("-----hh script-----")
#         queue = Queue()
#         logger.info("starting process...")
#         p = Process(target=self.run_calculation, args=(queue, cut, category))
#         p.start()
#         result = queue.get()
#         p.join()  # this blocks until the process terminates
#         FFHistos = result
        FFHistos = FakeFactor.calc(self, cut, category)

        return FFHistos
    
    def run_calculation(self, queue, cut, category):
        logger.info("In run_calculation...")
        FFHistos = FakeFactor.calc(self, cut, category)
#         queue.put(copy.deepcopy(FFHistos))

    def read_data_content(self, cut, path, weight):
        logger.info("In read_data_content...")
        self.prediction_helper = PredictionHelper(self.channel, self.era, self.nn_frac_config_file)

        if self.channel != "tt":

            logger.info("reading from " + path)
            data_content = rp.read_root(paths=path,
                                        where=cut.get(),
                                        columns=self.inputs["vars"] + self.variable.getBranches(for_df=True) +
                                                self.inputs["binning"] + weight.need + ["njets", "decayMode_2"] + [
                                                    "evt"])
        else:

            inputs = list(set(self.inputs["aiso1"]["vars"] + self.inputs["aiso2"]["vars"]))
            inputs.append("by*IsolationMVA*")

            logger.info("reading from " + path)
            data_content = rp.read_root(paths=path,
                                        where=cut.get(),
                                        columns=inputs + self.variable.getBranches(for_df=True) + self.inputs[
                                            "binning"] + weight.need + ["evt"])

            data_content.eval(" aiso1 = {0} ".format(Cut("-ANTIISO1-", "tt").getForDF()), inplace=True)
            data_content.eval(" aiso2 = {0} ".format(Cut("-ANTIISO2-", "tt").getForDF()), inplace=True)

        data_content.eval("mc_weight = {0}".format(weight.use), inplace=True)

#         logger.debug("------------------------------------------------------")
#         logger.debug("data_content that prediction columns will be added to:")
#         logger.debug(data_content)

        branches = self.prediction_helper.getBranchesForPrediction()

        logger.info("reading for prediction from " + path)
        df = rp.read_root(paths=path, where=cut.get(), columns=branches)

        # logger.debug("------------------------------------------------------")
        # logger.debug("prediction data frame before prediction columns are added:")
        # logger.debug(df)

        logger.info("getting prediction...")
        pred_concat = self.prediction_helper.getPredictionDataFrame(df)

#         logger.debug("------------------------------------------------------")
#         logger.debug("prediction data_frame after prediction:")
#         logger.debug(pred_concat)
#   
#         logger.debug("length of data_content: " + str(len(data_content)))
#         logger.debug("length of prediction: " + str(len(pred_concat)))

        logger.info("merging data frames...")

        if len(data_content) > 0 and len(pred_concat) > 0:
            data_content = data_content.merge(pred_concat)

            # logger.debug("data_content after merge: ")
            # logger.debug(data_content)

        df.drop(df.index, inplace=True)
        pred_concat.drop(pred_concat.index, inplace=True)

        return data_content

    def get_fractions_for_row(self, aiso, row):
        frac = {}
        frac["QCD"] = row["predicted_frac_prob_2"]
        frac["W"] = row["predicted_frac_prob_1"]
        frac["TT"] = row["predicted_frac_prob_0"]

        if self.real_nominal:
            denom = (frac["QCD"] + frac["W"] + frac["TT"])
            if denom > 0:
                for f in ["QCD", "W", "TT"]:
                    frac[f] *= 1.0 / denom

        return frac

if __name__ == '__main__':
    main()