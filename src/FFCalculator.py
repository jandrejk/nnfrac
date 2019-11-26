import json
import copy
import sys
import os
import math

import ROOT as R
import numpy as np
import root_numpy as rn
import root_pandas as rp

from array import array
from pandas import DataFrame, concat
from Tools.CutObject.CutObject import Cut
from Tools.Weights.Weights import Weight
from Tools.VarObject.VarObject import Var

from NNFractions.NNFractions import NNFractions

import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class FFCalculator:
    ff_config = os.path.join(os.path.dirname(os.path.realpath(__file__)), "ff_config.json")
    
    nn_frac_config_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "NNFractions/default_nn_frac_config.json")
    nn_fractions = None
    
    def __init__(self, channel, variable, era, add_systematics = True, debug = False, renormalize_fractions=True):

        self.channel = channel
#         self.fracs = {}
        self.variable = variable
        self.era = era

        with open(self.ff_config,"r") as FSO:
            self.config = json.load(FSO)

        self.ff_obj  = R.TFile.Open( self.config["ff_file"][channel] )
        self.ff = self.ff_obj.Get("ff_comb")
        self.ff_isopen = True

#         self.data_file = data_file
        self.renormalize_fractions = renormalize_fractions

        self.inputs = self.config["inputs"][channel]

        self.uncert_naming = self.config["uncert_naming"]
        self.uncerts = ["jetFakes"]
        if add_systematics:
            self.uncerts += [ str(u) for u in self.config["uncerts"][self.channel] ]
        if debug:
            self.uncerts += ["jetFakes_W","jetFakes_TT","jetFakes_QCD"]            
            
    def __del__(self):
        if self.ff_isopen:
            self.ff.Delete()
            self.ff_obj.Close()   
            
    def read_data(self, cut, path, weight):
        data_content = self.read_fakefactor_data(cut, path, weight)
    
        fraction_df = self.read_fractions(cut, path)
        
        logger.debug("length of data_content: " + str(len(data_content)))
        logger.debug("length of prediction: " + str(len(fraction_df)))
        
        logger.info("merging data frames...")
    
        if len(data_content) > 0 and len(fraction_df) > 0:
            data_content = data_content.merge(fraction_df)

            logger.debug("data_content after merge: ")
            logger.debug(data_content)
        
        fraction_df.drop(fraction_df.index, inplace=True)

        return data_content
    
    def read_fractions(self, cut, path):
        logger.info("Entering read_fractions...")
        self.nn_fractions = NNFractions(self.channel, self.era, self.nn_frac_config_file)
        
        branches = self.nn_fractions.get_required_branch_names()
    
        logger.info("reading for prediction from " + path)
        df = rp.read_root(paths=path, where=cut.get(), columns=branches)

        logger.debug("------------------------------------------------------")
        logger.debug("prediction data frame before prediction columns are added:")
        logger.debug(df)

        logger.info("getting prediction...")
        prediction_df = self.nn_fractions.get_prediction(df)

        logger.debug("------------------------------------------------------")
        logger.debug("prediction data_frame after prediction:")
        logger.debug(prediction_df)

        df.drop(df.index, inplace=True)

        return prediction_df

    def read_fakefactor_data(self, cut, path, weight):
        logger.info("In read_fakefactor_data...")

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
        
        logger.debug("------------------------------------------------------")
        logger.debug("data_content that prediction columns will be added to:")
        logger.debug(data_content)
        return data_content      
    
    def getFFWeights(self, data_content):
        ff_weights = []
        # This is slow. Figure out how to use it with vectorization.
        for _, row in data_content.iterrows():
            ff_weights.append(self.getFFWeightForEvent(row))

        ff_weights = DataFrame(ff_weights)
        ff_weights.columns = self.uncerts
        
        print "uncerts:"
        print self.uncerts

        if self.channel == "tt":
            ff_weights *= 0.5

        result = concat([data_content["evt"], ff_weights], axis=1)

        return result
    
    def getFFWeightForEvent(self, row):
        aiso = 0
        if self.channel == "tt":
            if row["aiso1"]:
                aiso = 1
                input_list = self.inputs["aiso1"]
            elif row["aiso2"]:
                aiso = 2
                input_list = self.inputs["aiso2"]
            else:
                return [0.]*len(self.uncerts)
        else:
            input_list = self.inputs

        frac = self.get_fractions_for_row(row)
        
        input_vars = []
        input_fracs = []
        for v in input_list["vars"]:
            input_vars.append(row[v])
        for f in ["QCD", "W", "TT"]:
            input_fracs.append(frac[f])

        ff = []
        for uncert in self.uncerts:

            if uncert == "jetFakes":
                ff_value = self.ff.value(len(input_vars + input_fracs), array('d', input_vars + input_fracs))
            elif uncert == "jetFakes_QCD":
                ff_value = self.ff.value(len(input_vars) + 3, array('d', input_vars + [frac["QCD"], 0., 0.]))
            elif uncert == "jetFakes_W":
                ff_value = self.ff.value(len(input_vars) + 3, array('d', input_vars + [0., frac["W"], 0.]))
            elif uncert == "jetFakes_TT":
                ff_value = self.ff.value(len(input_vars) + 3, array('d', input_vars + [0., 0., frac["TT"]]))
            else:
                ff_value = self.ff.value(len(input_vars + input_fracs), array('d', input_vars + input_fracs), uncert)

            if not R.TMath.IsNaN(ff_value) and not R.TMath.Infinity() == ff_value:
                ff.append(ff_value * row["mc_weight"])
            else:
                print uncert, ff_value
                ff.append(0.0)

        return np.array(ff)       
    
    
    def get_fractions_for_row(self, row):
        frac = {}
        frac["QCD"] = row["predicted_frac_prob_2"]
        frac["W"] = row["predicted_frac_prob_1"]
        frac["TT"] = row["predicted_frac_prob_0"]

        if self.renormalize_fractions:
            denom = (frac["QCD"] + frac["W"] + frac["TT"])
            if denom > 0:
                for f in ["QCD", "W", "TT"]:
                    frac[f] *= 1.0 / denom

        return frac
    