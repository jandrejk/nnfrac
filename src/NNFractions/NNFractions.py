import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

import os
import json

from Core.Settings import Settings
from Core.PredictionWrapper import PredictionWrapper

def main():
    pass


class NNFractions():
    config_path = "{0}/default_nn_frac_config.json".format(
        "/".join(os.path.realpath(__file__).split("/")[:-1]))

    def __init__(self, channel, era, config=""):

        if config:
            self.config_path = config
            
        logger.info("Loading nn frac config from {0}".format(self.config_path))
        logger.debug("Called constructor of PredictionHelper")
        with open(self.config_path,"r") as FSO:
            self.nn_frac_config = json.load(FSO)

        self.channel = channel
        self.era = era
        self.prediction = None

        logger.debug("Loaded nn_frac_config")
        logger.debug(str(self.nn_frac_config))

        self.setup_prediction()

    def setup_prediction(self): 
        path_type = self.nn_frac_config["model"]["path_type"]
        path_prefix = self.nn_frac_config["model"]["path_prefix"]
        
        if (path_type == "abs"):
            model_path = os.path.join(path_prefix, self.nn_frac_config["model"]["model_path"])      
        else:
#             realpath = "/".join(os.path.realpath(__file__).split("/")[:-1])
            realpath = os.path.dirname(os.path.realpath(__file__))
            model_path = os.path.join(realpath, self.nn_frac_config["model"]["model_path"])

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


if __name__ == '__main__':
    main()