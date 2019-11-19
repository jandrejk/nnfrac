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


def main():
    
    channel = "mt"
    
    filename = "{0}_test.root".format(channel)
    dirpath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../testdata")
    path = os.path.join(dirpath, filename)
    
    Cut.cutfile = os.path.join(os.path.dirname(os.path.realpath(__file__)), "cuts_2017.json")
    cut = Cut(cutstring="-OS- && -ISO- && -VETO- && -MT- && -TRIG-", channel=channel)
    
    ff = NNFakeFactor(channel, Var("m_vis", channel), "2017")
    
#     fraction_outpath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "fractions_output.root")    
#     ff.saveFractions(cut, path, weight = Weight("1.0",[]), outpath=fraction_outpath)
    
    ff_weight_outpath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "ff_weights_output.root")
    ff.saveFFWeights(cut, path, weight = Weight("1.0",[]), outpath=ff_weight_outpath)


class NNFakeFactor:    
    # TODO: make this configurable
    

    def __init__(self, channel, variable, era):

        # TODO: add everything else necessary for fake factor calculation
        self.channel = channel
        self.era = era
        self.variable = variable
        
    def getJetFakeHisto(self):
        pass
    
    def saveFFWeights(self, cut, path, weight, outpath):
        calculator = FFCalculator(channel=self.channel,
                              variable=self.variable,
                              era=self.era,
                              real_nominal=["xy"],
                              real_shifted=["xy"],
                              add_systematics=True,
                              debug=True
                              )
        
        data = calculator.read_data(cut, path, weight)
        
        ff_weights = calculator.getFFWeights(data)   
        
        print ff_weights
        
        data.to_root(outpath, key="TauCheck", mode="w") 
        
        complete_df = calculator.appendFFWeights(data)
        
        print complete_df
        
        complete_df.to_root(outpath, key="TauCheck", mode="w")
        
    def saveFractions(self, cut, path, weight, outpath):
        data = self.read_data(cut, path, weight)        
        data.to_root(outpath, key="TauCheck", mode="w")
        

if __name__ == '__main__':
    main()