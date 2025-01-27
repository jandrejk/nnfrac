import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

import os
import json

from Core.Settings import Settings
from Core.Prediction import Prediction

def main():
    print "Main() function currently not implemented -- to be used as part of another module (by calling the functions or creating instances of the classes)."
    

class NNFractions():
    config_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "default_nn_frac_config.json")

    def __init__(self, channel, era, config=""):

        if config:
            self.config_path = config
            
        logger.info("Loading config from {0}".format(self.config_path))
        
        with open(self.config_path,"r") as FSO:
            self.nn_frac_config = json.load(FSO)

        self.channel = channel
        self.era = era
        self.prediction = None

        logger.debug("Successfully loaded config")
        logger.debug(str(self.nn_frac_config))

        self._load()

    def get_required_branch_names(self):
        variables = self.prediction.model.variables
        logger.debug(variables)
        branches = ["evt"] + variables + ["jdeta", "mjj", "dijetpt", "jpt_1", "jpt_2"]
        return list(set(branches))

    def get_prediction(self, data_frame):
        logger.debug( "Entering get_prediction...")
        return self.prediction.get_prediction_data_frame(data_frame, "evt")

    def _load(self): 
        path_type = self.nn_frac_config["model"]["path_type"]
        path_prefix = self.nn_frac_config["model"]["path_prefix"]
        
        if (path_type == "abs"):
            model_path = os.path.join(path_prefix, self.nn_frac_config["model"]["model_path"])      
        else:
            realpath = os.path.dirname(os.path.realpath(__file__))
            model_path = os.path.join(realpath, self.nn_frac_config["model"]["model_path"])

        model_path = os.path.join(model_path, str(self.era), "{0}.{1}".format(self.channel, "keras"))
        logger.info("Loading model from {0}".format(model_path))
        
        settings = Settings(self.channel, self.era)
        self.prediction = Prediction(settings, model_path)


if __name__ == '__main__':
    main()