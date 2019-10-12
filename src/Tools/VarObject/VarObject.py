from array import array
import numpy as np

def main():
    v = Var("predicted_prob", "mt")

    stage1cats = {"ggh":["VBFTOPO_JET3VETO125","VBFTOPO_JET3125",
                         "0J125","1J_PTH_0_60125","1J_PTH_60_120125","1J_PTH_120_200125","1J_PTH_GT200125",
                         "GE2J_PTH_0_60125","GE2J_PTH_60_120125","GE2J_PTH_120_200125","GE2J_PTH_GT200125"],
                  "qqh":["VBFTOPO_JET3VETO125","VBFTOPO_JET3125","VH2JET125","REST125","PTJET1_GT200125"]
    }

    for mode , cats in stage1cats.items():
        binning = []
        for i,c in enumerate(cats):
            bins = v.bins( "_".join([mode,c]) )[1]
            if i == 0:
                first = bins[0]
                binning.append(first)
                interval = round(bins[-1],4) - first

            for j,b in enumerate(bins):
                if j > 0:
                    binning.append(b + i*interval)

        binning = list(set(binning))
        binning.sort()
        print mode, binning

def getStage1Binnings(channel):

    if channel in ["et","mt"]:
        return {
            "ggh_VBFTOPO_JET3VETO":  array("d", [0.125, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0] ),
            "ggh_VBFTOPO_JET3":      array("d", [0.125, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0] ),
            "ggh_0J":                array("d", [0.125, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0] ),
            "ggh_1J_PTH_0_60":       array("d", [0.125, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0] ),
            "ggh_1J_PTH_60_120":     array("d", [0.125, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0] ),
            "ggh_1J_PTH_120_200":    array("d", [0.125, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0] ),
            "ggh_1J_PTH_GT200":      array("d", [0.125, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0] ),
            "ggh_GE2J_PTH_0_60":     array("d", [0.125, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0] ),
            "ggh_GE2J_PTH_60_120":   array("d", [0.125, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0] ),
            "ggh_GE2J_PTH_120_200":  array("d", [0.125, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0] ),
            "ggh_GE2J_PTH_GT200":    array("d", [0.125, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0] ),

            "qqh_VBFTOPO_JET3VETO":  array("d", [0.125, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0] ),
            "qqh_VBFTOPO_JET3":      array("d", [0.125, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0] ),
            "qqh_VH2JET":            array("d", [0.125, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0] ),
            "qqh_REST":              array("d", [0.125, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0] ),
            "qqh_PTJET1_GT200":      array("d", [0.125, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0] )
        }

    if channel in ["tt"]:
        return {
            "ggh_VBFTOPO_JET3VETO":  array("d", [0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0] ),
            "ggh_VBFTOPO_JET3":      array("d", [0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0] ),
            "ggh_0J":                array("d", [0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0] ),
            "ggh_1J_PTH_0_60":       array("d", [0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0] ),
            "ggh_1J_PTH_60_120":     array("d", [0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0] ),
            "ggh_1J_PTH_120_200":    array("d", [0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0] ),
            "ggh_1J_PTH_GT200":      array("d", [0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0] ),
            "ggh_GE2J_PTH_0_60":     array("d", [0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0] ),
            "ggh_GE2J_PTH_60_120":   array("d", [0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0] ),
            "ggh_GE2J_PTH_120_200":  array("d", [0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0] ),
            "ggh_GE2J_PTH_GT200":    array("d", [0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0] ),

            "qqh_VBFTOPO_JET3VETO":  array("d", [0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0] ),
            "qqh_VBFTOPO_JET3":      array("d", [0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0] ),
            "qqh_VH2JET":            array("d", [0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0] ),
            "qqh_REST":              array("d", [0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0] ),
            "qqh_PTJET1_GT200":      array("d", [0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0] ),
        }
    return {}


class Var(object):

    def __init__(self, var, channel = None, config = {}):
        self.channel = channel
        if config:
            self.config = config
        else: 
            self.config = {
                "predicted_prob": {"tex":r"ML score",           "binning": {"def": array("d", [0.125, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0] ),
                                                                            "tt":  array("d", [0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0] ),
                                                                            "mt":  array("d", [0.125, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0]),
                                                                            "et":  array("d", [0.125, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0]),
                                                                           }
                },
                "predicted_class":     {"tex":r"class",              "binning": {"def": (8, -0.5,7.5 ) },   },
                "m_sv":           {"tex":r"m_{sv}" ,            "binning": {"def": (30,0,300) },  },
                # "m_vis":        {"tex":r"m_{vis}" ,           "binning": {"def": (10,20,200) },    },
                "m_vis":          {"tex":r"m_{vis}" ,           "binning": {"def": (30,0,300) },    },
                "eta_1":          {"tex":r"#eta_{1}" ,          "binning": {"def": (10,-2.3,2.3) },     },
                "eta_2":          {"tex":r"#eta_{2}" ,          "binning": {"def": (10,-2.3,2.3) }, },
                "iso_1":          {"tex":r"iso_{1}" ,           "binning": {"def": (28,0.01,0.15) },     },
                "iso_2":          {"tex":r"iso_{2}" ,           "binning": {"def": (50,0,1) },     },
                "pt_1":           {"tex":r"p_{T,1}" ,           "binning": {"def": (30,0,150) },  },
                "pt_2":           {"tex":r"p_{T,2}" ,           "binning": {"def": (30,0,150) },  },
                "jpt_1":          {"tex":r"p_{T,1}^{jet}" ,     "binning": {"def": (10,20,200) }, },
                "jpt_2":          {"tex":r"p_{T,2}^{jet}" ,     "binning": {"def": (10,20,200) }, },
                "jm_1":           {"tex":r"m_{1}^{jet}" ,       "binning": {"def": (10,2,30) }, },
                "jm_2":           {"tex":r"m_{2}^{jet}" ,       "binning": {"def": (10,2,30) }, },
                "jphi_1":         {"tex":r"#phi_{1}^{jet}" ,    "binning": {"def": (100,-10,5) },   },
                "jphi_2":         {"tex":r"#phi_{2}^{jet}" ,    "binning": {"def": (100,-10,5) },   },
                "jdeta":          {"tex":r"jdeta" ,             "binning": {"def": (50,0,10) },   },
                "dijetpt":        {"tex":r"p_{T}^{j1,j2}" ,     "binning": {"def": (10,0,200) },   },
                "bpt_1":          {"tex":r"p_{T,1}^{b-jet}" ,   "binning": {"def": (10,30,200) }, },
                "bpt_2":          {"tex":r"p_{T,2}^{b-jet}" ,   "binning": {"def": (10,30,200) }, },
                "bcsv_1":         {"tex":r"b_{csv}^{1}" ,       "binning": {"def": (10,0.6,1) },     },
                "bcsv_2":         {"tex":r"b_{csv}^{2}" ,       "binning": {"def": (10,0.6,1) },     },
                "beta_1":         {"tex":r"#eta_{1}^{b-jet}" ,  "binning": {"def": (100,-10,2.5) }, },
                "beta_2":         {"tex":r"#eta_{2}^{b-jet}" ,  "binning": {"def": (100,-10,2.5) }, },
                "decayMode_2":    {"tex":r"DM tau" ,            "binning": {"def": (13,0,13) }, },
                # "njets":        {"tex":r"N_{jet}" ,           "binning": {"def": (5,array("d", [0,1,2,3,4,25])) },     },
                "njets":          {"tex":r"N_{jet}" ,           "binning": {"def": (9,0,9) },     },
                "nbtag":          {"tex":r"N_{b-tag}" ,         "binning": {"def": (5,array("d", [0,1,2,3,4,25])) },     },
                "mt_1":           {"tex":r"m_{T,1}" ,           "binning": {"def": (40,0,200) },   },
                "mt_2":           {"tex":r"m_{T,2}" ,           "binning": {"def": (10,0,100) },   },
                "pt_tt":          {"tex":r"p_{T}^{#tau#tau}" ,  "binning": {"def": array("d", [0,5,10,15,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90,95,100,105,110,115,120,125,130,135,140,145,150,155,160] ) },   },
                "pt_vis":         {"tex":r"p_{T}^{#tau#tau}" ,  "binning": {"def": (15,0,150) },   },
                "mjj":            {"tex":r"m_{jj}" ,            "binning": {"def": (10,10,150) }, },
                "npv":            {"tex":r"N_{PV}" ,            "binning": {"def": (100,0,100) }, },
                "met":            {"tex":r"E_{T}^{miss}" ,      "binning": {"def": (10,0,150) },   },
                "dzeta":          {"tex":r"D_{#zeta}" ,         "binning": {"def": (100,-100,150) },},
            }

        self.shifted_quantities = {
            "jes":{
                "find":["scale_j"],
                "vars":[
                    "met",
                    "m_sv",
                    "pt_ttjj",
                    "mt_1",
                    "mt_2",
                    "mt_tot",
                    "njets",
                    "mjj",
                    "jdeta",
                    "dijetpt",
                    "dijetphi",
                    "jdphi",
                    "jpt_1",
                    "jpt_2",
                ] 
            },
            "met":{
                "find":["boson_reso_met","boson_scale_met"],
                "vars":[
                    "met",
                    "m_sv",
                    "pt_ttjj",
                    "mt_1",
                    "mt_2",
                    "mt_tot",
                    "njets",
                    "mjj",
                    "jdeta",
                    "dijetpt",
                    "dijetphi",
                    "jdphi",
                    "jpt_1",
                    "jpt_2",
                ] 
            },            
            "btag":{
                "find":["Btag","Mistag"],
                "vars":[
                    "bpt_1",
                    "bpt_2",
                    "nbtag"
                ]
            }
        }
      


        self.set(var)

    def getBranches(self,for_df = False, jec_shift="", as_list = False):

        if for_df: # return var as list and make sure that also shifts are included
            if ":" in self.name:
                names = []
                for n in self.name.split(":"):
                    names.append( n+"*" )     
                return names 
            return [self.name + "*"]

        if as_list:
            if ":" in self.name:
                return  self.name.split(":")

            return [self.name ]    

        if ":" in self.name:
            names = []
            for n in self.name.split(":"):
                names.append( self.getShiftedName(jec_shift) )   
            return names

        return self.getShiftedName(jec_shift)

    def getShiftedName(self, shift):
        for _, shifts in self.shifted_quantities.items():
            for s in shifts["find"]:
                if s in shift and self.name in shifts["vars"]:
                    return self.name+shift
        return self.name

    def is2D(self):
        if ":" in self.name: return True
        return False

    def set(self, var):
        
        self.name = var

        if ":" in var:
            binning = []
            names = var.split(":")
            for n in names:
                binning+= self.config[n]["binning"]["def"]
            self.binning = {"def":binning}
            self.tex = " / ".join([ self.config[names[0]]["tex"], self.config[names[1]]["tex"] ])


        else:
            if not self.config.get(var, False ):
                self.binning = {"def":(100,-50,50) }
                self.tex = var

            else:
                self.binning = self.config[var]["binning"]
                if var == "predicted_prob":
                    self.binning.update( getStage1Binnings(self.channel) )
                self.tex = self.config[var]["tex"]


    def bins(self, other = ""):

        if other in self.binning and other != "tt":
            return getForTH( self.binning[other] )
        elif self.channel in self.binning:
            return getForTH( self.binning[self.channel] )
        else:
            return getForTH( self.binning["def"] )

        return getForTH( self.binning["def"] )

def getForTH(binning):

    if type(binning) == array:
        return ( len(binning)-1, binning )
    else:
        return binning


if __name__ == '__main__':
    main()
