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


Cut.cutfile = "/afs/hephy.at/work/m/mspanring/CMSSW_9_4_0/src/HephyHiggs/Tools/Datacard/conf2016/cuts.json"


class FakeFactor():
    fraction_path = "{0}/default_fractions".format( "/".join( os.path.realpath(__file__).split("/")[:-1] ) )
    fractions = "{0}/default_fractions/htt_ff_fractions_2016.root".format( "/".join( os.path.realpath(__file__).split("/")[:-1] ) )
    ff_config = "{0}/config/default_ff_config.json".format( "/".join( os.path.realpath(__file__).split("/")[:-1] ) )

    def __init__(self, channel, variable, data_file, era, add_systematics = True, debug = False, real_nominal={}, real_shifted={}):

        self.channel = channel
        self.frac_isopen = False
        self.w = None
        self.fracs = {}
        self.variable = variable
        self.era = era

        if os.path.exists(self.fractions):
            f = R.TFile(self.fractions)
            self.w = f.Get("w")
            f.Close()

        with open(self.ff_config,"r") as FSO:
            self.config = json.load(FSO)

        self.ff_obj  = R.TFile.Open( self.config["ff_file"][channel] )
        self.ff = self.ff_obj.Get("ff_comb")
        self.ff_isopen = True

        self.data_file = data_file
        self.real_nominal = real_nominal
        self.real_shifted = real_shifted


        self.inputs = self.config["inputs"][channel]

        self.uncert_naming = self.config["uncert_naming"]
        self.uncerts = ["jetFakes"]
        if add_systematics:
            self.uncerts += [ str(u) for u in self.config["uncerts"][self.channel] ]
        if debug:
            self.uncerts += ["jetFakes_W","jetFakes_TT","jetFakes_QCD"]

    def __del__(self):
        if self.frac_isopen:
            self.frac_file.Close()

        if self.ff_isopen:
            self.ff.Delete()
            self.ff_obj.Close()
    
    # overridden in NNFakeFactor
    def calc(self, cut, category = "def"):


        cut = cut.switchCutTo("-ANTIISO-")

        FFHistos = self.fillHistograms(cut = cut, 
                                       path =self.data_file, 
                                       category=category)


        # Do this before nominal. Need fully jetFakes template
        if self.real_shifted:
            jetFakes_TES = {}
            for shift in self.real_shifted:
                jetFakes_TES[shift] = copyTemplate(FFHistos["jetFakes"], "jetFakes_"+ shift )


        if self.real_nominal:

            if "EMB" in self.real_nominal:
                emb_cut = Cut("-GENTAU-")
                mc_cut = Cut("!(-GENTAU- | -GENJET-)")
            else:
                mc_cut = Cut(" !(-GENJET-)")

            real_parts = {}
            for uncert in self.uncerts:
                if not "jetFakes" in uncert:
                    name = self.convertSystematicName(uncert)
                else: 
                    name = uncert

                real_parts[name] = getEmptyHist("real"+name, self.variable, category)
                real_parts[name].Sumw2(True)

            for name, info in self.real_nominal.items():
                if name == "EMB":
                    subcut = emb_cut
                else:
                    subcut = mc_cut

                tmp = self.fillHistograms(cut = cut + subcut, 
                                          path =info["path"], 
                                          category=category,
                                          weight = info["weight"]
                                        )
                
                for uncert in FFHistos:
                    real_parts[uncert].Add(tmp[uncert])

            for uncert in FFHistos:
                
                FFHistos[uncert].Add(real_parts[uncert], -1)                

        if self.real_shifted:

            #Only calculate nominal templates for TES shifts
            full_uncerts = self.uncerts
            self.uncerts = ["jetFakes"]

            for shift in self.real_shifted:
                samples = self.real_shifted[shift]

                if "EMB" in samples:
                    emb_cut = Cut("-GENTAU-")
                    mc_cut = Cut("!(-GENTAU- | -GENJET-)")
                else:
                    mc_cut = Cut(" !(-GENJET-)")

                realTES_parts = getEmptyHist("real"+shift+name, self.variable, category)
                realTES_parts.Sumw2(True)

                for name, info in samples.items():
                    if name == "EMB":
                        subcut = emb_cut
                    else:
                        subcut = mc_cut

                    tmp = self.fillHistograms(cut = cut + subcut, 
                                              path =info["path"], 
                                              category=category,
                                              weight = info["weight"]
                                            )
  
                    realTES_parts.Add(tmp["jetFakes"])

                jetFakes_TES[shift].Add(realTES_parts, -1)

            for shift in jetFakes_TES:
                FFHistos["jetFakes_"+shift] = copy.deepcopy( jetFakes_TES[shift] )

            self.uncerts = full_uncerts
            
        print "jetFakes Integral:"
        print str(FFHistos["jetFakes"].Integral())

               
        norm_factors = {}
        for upname, uphist in FFHistos.items():
            if not "jetFakes_CMS_ff" in upname: continue
            if upname.endswith("Down"): continue

            downname=upname.replace('Up','Down')
            h1_orig,h2_orig = FFHistos[upname],FFHistos[downname]

            h1,h2 = self.interpolateHistos( h1_orig, h2_orig )  #TODO: Check if Down histo really exists
            
            for name,hist in zip( [ upname , downname ], [ h1 , h2 ] ):
                if not hist.Integral(0, hist.GetNbinsX()+1 ):
                    norm_factors[name] = 1
                else:
                    norm_factors[name] =  FFHistos["jetFakes"].Integral(0,FFHistos["jetFakes"].GetNbinsX()+1) / hist.Integral(0, hist.GetNbinsX()+1 )

                hist.Scale( norm_factors[name] )
                FFHistos[name] = copy.deepcopy(hist)
                
        # norm_factors = {}
        # for name, hist in FFHistos.items():
        #     if not "jetFakes_CMS_ff" in name: continue
        #     if not hist.Integral(0, hist.GetNbinsX()+1 ):
        #         norm_factors[name] = 1
        #     else:
        #         norm_factors[name] =  FFHistos["jetFakes"].Integral(0,FFHistos["jetFakes"].GetNbinsX()+1) / hist.Integral(0, hist.GetNbinsX()+1 )

        #     hist.Scale( norm_factors[name] )
        #     FFHistos[name] = copy.deepcopy(hist)

        if norm_factors: FFHistos["jetFakes_norm"] = self.getNormUncertainty(norm_factors)

        histos = FFHistos.keys()
        for hist in histos:
            if "CMS" in hist:
                addClone(FFHistos, name=hist, dolly=hist.replace("_Run{0}".format(self.era),""))

        return copy.deepcopy(FFHistos)
    
    def fillHistograms(self, cut, path, category, weight = Weight("1.0",[]) ):

        data_content = self.read_data_content(cut, path, weight)

        ff_weights = self.getFFWeights(data_content)

        FFHistos = {}
        for i,uncert in enumerate(self.uncerts):

            if not "jetFakes" in uncert:
                name = self.convertSystematicName(uncert)
            else:
                name = uncert

            FFHistos[name] = getEmptyHist(name, self.variable, category)
            FFHistos[name].Sumw2(True)

            if len(data_content):
                rn.fill_hist( FFHistos[name], array = data_content[self.variable.getBranches()].values,
                                              weights = ff_weights[i].values )

            FFHistos[name] = self.unroll2D(FFHistos[name])

        data_content.drop( data_content.index, inplace = True )
        return copy.deepcopy(FFHistos)
    
    # overridden in NNFakeFactor
    def read_data_content(self, cut, path, weight):
        if self.channel != "tt":

            data_content = rp.read_root(paths=path,
                                        where=cut.get(),
                                        columns=self.inputs["vars"] + self.variable.getBranches(for_df=True) +
                                                self.inputs["binning"] + weight.need + ["njets", "decayMode_2"])
        else:

            inputs = list(set(self.inputs["aiso1"]["vars"] + self.inputs["aiso2"]["vars"]))
            inputs.append("by*IsolationMVA*")

            data_content = rp.read_root(paths=path,
                                        where=cut.get(),
                                        columns=inputs + self.variable.getBranches(for_df=True) + self.inputs[
                                            "binning"] + weight.need)

            data_content.eval(" aiso1 = {0} ".format(Cut("-ANTIISO1-", "tt").getForDF()), inplace=True)
            data_content.eval(" aiso2 = {0} ".format(Cut("-ANTIISO2-", "tt").getForDF()), inplace=True)

        data_content.eval("mc_weight = {0}".format(weight.use), inplace=True)

        return data_content  
    
    def getFFWeights(self, data_content):
        ff_weights = []
        # This is slow. Figure out how to use it with vectorization.
        for _, row in data_content.iterrows():
            ff_weights.append(self.addFF(row))

        ff_weights = DataFrame(ff_weights)

        if self.channel == "tt":
            ff_weights *= 0.5

        return ff_weights


    def addFF(self, row):
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

        frac = self.get_fractions_for_row(aiso, row)

        return self.get_FF_for_row(row, input_list, frac)

    # overridden in NNFakeFactor
    def get_fractions_for_row(self, aiso, row):
        self.w.var("aiso").setVal(aiso)

        for b in self.inputs["binning"]:
            if b == "predicted_class":
                self.w.var("cat").setVal(row["predicted_class"])
            else:
                self.w.var("cat").setVal(-1)
                self.w.var(b).setVal(row[b])

        frac = {"QCD": self.w.function(self.channel[0] + "_frac_qcd").getVal(),
                "W": self.w.function(self.channel[0] + "_frac_w").getVal(),
                "TT": self.w.function(self.channel[0] + "_frac_tt").getVal(),
                }
        
        print "overriding fractions: qcd:1, w:0, tt:0"
        frac["QCD"] = 1.0
        frac["W"] = 0
        frac["TT"] = 0

        if self.real_nominal:
            denom = ( frac["QCD"] + frac["W"] + frac["TT"] )
            if denom > 0:
                for f in ["QCD","W","TT"]:
                    frac[f] *= 1.0 / denom

        return frac

    def get_FF_for_row(self, row, input_list, frac):
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

    # def interpolateHistos(self, h1_old, h2_old):

    #     h1,h2 = copy.deepcopy(h1_old),copy.deepcopy(h2_old)

    #     nbins=h1_old.GetNbinsX()
    #     for ibin in xrange(nbins+2):     #includes under- and overflow
    #         cont1,cont2=h1_old.GetBinContent(ibin),h2_old.GetBinContent(ibin)
    #         h1.SetBinContent( ibin, cont2* float(nbins-ibin)/nbins + cont1* float(ibin)/nbins )
    #         h2.SetBinContent( ibin, cont1* float(nbins-ibin)/nbins + cont2* float(ibin)/nbins )

    #     return h1,h2

    def interpolateHistos(self, h1_old, h2_old):

        h1,h2 = copy.deepcopy(h1_old),copy.deepcopy(h2_old)

        nbins=h1_old.GetNbinsX()
        for ibin in xrange(1,nbins+1):
            cont1,cont2=h1_old.GetBinContent(ibin),h2_old.GetBinContent(ibin)
            h1.SetBinContent( ibin, cont2* float(nbins-ibin)/(nbins) + cont1* float(ibin)/(nbins) )
            h2.SetBinContent( ibin, cont1* float(nbins-ibin)/(nbins) + cont2* float(ibin)/(nbins) )

        return h1,h2

    # def interpolateHistos(self, h1_old, h2_old):

    #     h1,h2 = copy.deepcopy(h1_old),copy.deepcopy(h2_old)

    #     nbins=h1_old.GetNbinsX()
    #     for ibin in xrange(nbins):
    #         cont1,cont2=h1_old.GetBinContent(ibin),h2_old.GetBinContent(ibin+1)
    #         h1.SetBinContent( ibin+1, cont2* float(nbins-ibin-1)/(nbins-1) + cont1* float(ibin)/(nbins-1) )
    #         h2.SetBinContent( ibin+1, cont1* float(nbins-ibin-1)/(nbins-1) + cont2* float(ibin)/(nbins-1) )

    #     return h1,h2    
    
    def unroll2D(self, th):
        if type(th) is R.TH1D: return th

        bins = th.GetNbinsX()*th.GetNbinsY()
        name = th.GetName().replace("2D","")
        unrolled = R.TH1D(name,name, *(bins,0,bins) )
        unrolled.Sumw2(True)

        for i,y in  enumerate( xrange(1,th.GetNbinsY()+1) ):
            for x in xrange(1,th.GetNbinsX()+1):
                offset = i*th.GetNbinsX()

                unrolled.SetBinContent( x+offset, th.GetBinContent(x,y) )
                unrolled.SetBinError( x+offset, th.GetBinError(x,y) )

        return unrolled

    def convertSystematicName(self,name):

        if "ff_w_syst" in name or "ff_tt_syst" in name:
            if not self.channel == "tt":
                uncert_name = "jetFakes_" + self.uncert_naming[name].format(channel = "")
            else:
                uncert_name = "jetFakes_" + self.uncert_naming[name].format(channel = "_"+self.channel )
        else:
            uncert_name = "jetFakes_" + self.uncert_naming[name].format(channel = "_"+self.channel )
        return uncert_name

    def getNormUncertainty(self, norm_factors ):
        ff_norm = R.TH1D("jetFakes_norm","jetFakes_norm",4,-0.5,3.5 )

        norms = { "statUp":0.,"statDown":0.,"systUp":0.,"systDown":0. }
        for name, factor in norm_factors.items():
            if "syst" in name: key  = "syst"
            else:              key  = "stat"
            if factor > 1:     key += "Up"
            else:              key += "Down"

            norms[key] = math.sqrt( norms[key]**2 + (1. - factor)**2  )

        ff_norm.SetBinContent(1, norms["statUp"])
        ff_norm.SetBinContent(2, norms["statDown"])
        ff_norm.SetBinContent(3, norms["systUp"])
        ff_norm.SetBinContent(4, norms["systDown"])

        return ff_norm    

def getNeededShifts( shift_dict ):
    shifts = []
    for sample in shift_dict:
        for shift in shift_dict[sample]:

            shifts.append( "_".join( shift.split("_")[1:] ) )
    return list(set(shifts))

def getEmptyHist(name, variable, category):

    if variable.is2D():
        return R.TH2D(name+"2D",name+"2D",*( variable.bins(category) ))
    else:
        return R.TH1D(name,name,*( variable.bins(category) ))

def addClone(histo_dict, dolly, name):
    histo_dict[dolly] = copyTemplate( histo_dict[name], dolly)

def copyTemplate(template, name):

    newtemplate = copy.deepcopy(template)
    newtemplate.SetName(name)
    newtemplate.SetTitle(name)

    return newtemplate
