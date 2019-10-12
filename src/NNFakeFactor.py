import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

import os

from Tools.CutObject.CutObject import Cut
from Tools.Weights.Weights import Weight
from Tools.VarObject.VarObject import Var
from NNFractions.NNFractions import NNFractions

import root_pandas as rp
from pandas import DataFrame, concat


def main():
    
    channel = "mt"
    
    filename = "{0}_test.root".format(channel)
    dirpath = "../testdata"
    path = os.path.join(dirpath, filename)
    
    Cut.cutfile = "./cuts_2017.json"
    cut = Cut(cutstring="-OS- && -ISO- && -VETO- && -MT- && -TRIG-", channel=channel)
    
    ff = NNFakeFactor(channel, "2017")
    ff.run(cut, path, weight = Weight("1.0",[]))


class NNFakeFactor:    
    nn_frac_config_file = "{0}/NNFractions/default_nn_frac_config.json".format("/".join(os.path.realpath(__file__).split("/")[:-1]))
    

    nn_fractions = None

    def __init__(self, channel, era):

        # TODO: add everything else necessary for fake factor calculation
        self.channel = channel
        self.era = era
        self.inputs = {}
        self.inputs["vars"] = ["pt_2","decayMode_2","njets","m_vis","mt_1","iso_1"]
        self.inputs["frac"] = ["QCD","W","TT"]
        self.inputs["binning"] = ["pt_2","njets"]
        self.variable = Var("m_vis", channel)
        
        
    def run(self, cut, path, weight):
        data = self.read_data(cut, path, weight)
        
    def read_data(self, cut, path, weight):
        data_content = self.read_fakefactor_data(cut, path, weight)
    
        pred_concat = self.read_fractions(cut, path)
        
        logger.info("merging data frames...")
    
        if len(data_content) > 0 and len(pred_concat) > 0:
            data_content = data_content.merge(pred_concat)

            # logger.debug("data_content after merge: ")
            # logger.debug(data_content)
        
        pred_concat.drop(pred_concat.index, inplace=True)

        return data_content


    def read_fractions(self, cut, path):
        logger.info("Entering read_fractions...")
        self.nn_fractions = NNFractions(self.channel, self.era, self.nn_frac_config_file)
        
        branches = self.nn_fractions.getBranchesForPrediction()
    
        logger.info("reading for prediction from " + path)
        df = rp.read_root(paths=path, where=cut.get(), columns=branches)

        # logger.debug("------------------------------------------------------")
        # logger.debug("prediction data frame before prediction columns are added:")
        # logger.debug(df)

        logger.info("getting prediction...")
        pred_concat = self.nn_fractions.getPredictionDataFrame(df)

#         logger.debug("------------------------------------------------------")
#         logger.debug("prediction data_frame after prediction:")
#         logger.debug(pred_concat)
#   
#         logger.debug("length of data_content: " + str(len(data_content)))
#         logger.debug("length of prediction: " + str(len(pred_concat)))

        df.drop(df.index, inplace=True)

        return pred_concat

    def read_fakefactor_data(self, cut, path, weight):
        logger.info("In read_fakefactor_data...")
#             self.prediction_helper = NNFractionProvider(self.channel, self.era, self.nn_frac_config_file)

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