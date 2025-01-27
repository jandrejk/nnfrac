import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

import os

from Tools.CutObject.CutObject import Cut
from Tools.Weights.Weights import Weight
from Tools.VarObject.VarObject import Var
from NNFractions.NNFractions import NNFractions
from FFCalculator import FFCalculator

import root_pandas as rp
from pandas import DataFrame, concat
import pandas as pd

import argparse

def main():
    
    parser = argparse.ArgumentParser(description='Input for NN-FF framework')
    
    
    parser.add_argument('-era', dest='era', type=str, choices=["2016","2017","2018"],
                        help='Year of data taking', default="2017")
    parser.add_argument('-c', dest='channel', type=str, choices=["mt","et","tt"],
                        help='HTT decay channel', default="mt")

    parser.add_argument('-var', dest='variable', type=str,
                        help='Variable for plotting', default="m_vis")


    args = parser.parse_args()
    print "era: {}".format(args.era)

    channel = args.channel
    era = args.era
    variable = args.variable
    
    filename = "{0}_test.root".format(channel)
    dirpath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../testdata")
    path = os.path.join(dirpath, filename)
    
    Cut.cutfile = os.path.join(os.path.dirname(os.path.realpath(__file__)), "cuts_{era}.json".format
    (era=era))
    cut = Cut(cutstring="-OS- && -ANTIISO2- && -VETO- && -MT- && -TRIG-", channel=channel)
    
    ff = NNFakeFactor(channel, Var(variable, channel), era)
    
    # fraction_outpath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "fractions_output.root")    
    # ff.saveFractions(cut, path, weight = Weight("1.0",[]), outpath=fraction_outpath)
    
    ff_weight_outpath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "ff_weights_output.root")
    ff.saveFFWeights(cut, path, weight = Weight("1.0",[]), outpath=ff_weight_outpath)

    friend_outpath = os.path.join(dirpath, "friends/friend.root") 
    ff.saveFFWeightsToFriend(cut, path, weight = Weight("1.0",[]), outpath=friend_outpath)


class NNFakeFactor:    
    # TODO: make this configurable
    

    def __init__(self, channel, variable, era):

        # TODO: add everything else necessary for fake factor calculation
        self.channel = channel
        self.era = era
        self.variable = variable
        
    def getJetFakeHisto(self):
        pass

    def saveFractions(self, cut, path, weight, outpath):
        fractions = self._readFractions(cut, path)
        fractions.to_root(outpath, key="TauCheck", mode="w")
    
    def saveFFWeights(self, cut, path, weight, outpath):
        ff_weights = self._readFFWeights(cut, path, weight, outpath)        
        logger.debug(ff_weights)        
        ff_weights.to_root(outpath, key="TauCheck", mode="w") 

    def saveFFWeightsToFriend(self, cut, path, weight, outpath):
        ff_weights = self._readFFWeights(cut, path, weight, outpath)        
        logger.debug(ff_weights)

        # read "evt" branch for all events without selection cut
        evt_df = rp.read_root(paths=path, where="", columns=["evt"])        
        print "Merging..."

        merged_df = pd.merge(evt_df, ff_weights, on="evt", how="outer").fillna(-999)
        print merged_df
        
        merged_df.to_root(outpath, key="TauCheck", mode="w")   
        
#         for row in merged_df[1:]:
#             merged_df.to_root(outpath, key="TauCheck", mode="a") 

    def _readFFWeights(self, cut, path, weight, outpath):
        calculator = FFCalculator(channel=self.channel,
                              variable=self.variable,
                              era=self.era,
                              renormalize_fractions=True,
                              add_systematics=True,
                              debug=True
                              )
        
        data = calculator.read_data(cut, path, weight)        
        ff_weights = calculator.getFFWeights(data)
        return ff_weights

    def _readFractions(self, cut, path, weight, outpath):
        calculator = FFCalculator(channel=self.channel,
                              variable=self.variable,
                              era=self.era,
                              renormalize_fractions=True,
                              add_systematics=True,
                              debug=True
                              )
        
        fractions = calculator.read_fractions(cut, path)
        return fractions
        
       
    
        
    
        

if __name__ == '__main__':
    main()