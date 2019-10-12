import os
import root_pandas as rp
from pandas import DataFrame, concat

from Tools.CutObject.CutObject import Cut

def main():
    
    channel = "mt"
    
    filename = "{0}-NOMINAL_ntuple_Data.root".format(channel)
    dirpath = "/eos/user/m/msajatov/data/ntuples_scp/v10"
    path = os.path.join(dirpath, filename)
    
    Cut.cutfile = "./cuts_2017.json"
    cut = Cut(cutstring="-OS- && -ISO- && -VETO- && -MT- && -TRIG-", channel=channel)
    
    
    branches = [
"pt_1",
"pt_2",
"jpt_1",
"jpt_2",
"bpt_1",
"bpt_2",
"njets",
"nbtag",
"m_sv",
"mt_1",
"mt_2",
"pt_vis",
"pt_tt",
"mjj",
"jdeta",
"m_vis",
"dijetpt",
"met",
"eta_1",
"eta_2",
"iso_1",
"iso_2"
] + [
        "evt",
        "by*IsolationMVArun2017v2DBoldDMwLT2017*",       
        "pt_1",
        "pt_2",
        "q_1",
        "q_2",
        "iso_1",
        "iso_2",
        "phi_1",
        "phi_2",
        "eta_1",
        "eta_2",
        "mt_1",
        "njets",
        "decayMode_1",
        "decayMode_2",
        "dilepton_veto",
        "extraelec_veto",
        "extramuon_veto",
        "againstMuon*",
        "againstElectron*",
        "flagMETFilter",
        "trg*",
        "*Weight*",
        "*weight*",
        "htxs*"     
    ] + ["*weight*","gen_match*","topPtReweightWeight*","zPtReweightWeight", "sf*","njets","jpt_1","jdeta","mjj"]
    
    # chunksize is the number of events BEFORE the selection (where) is applied
    # for tt a chunksize of 5000 results in 37 events in the SR
    # for mt a chunksize of 2000 results in 36 events in the SR
    # for et a chunksize of 1000 results in 34 events in the SR
    df_iter = rp.read_root(paths=path, where=cut.getForDF(), columns=branches, chunksize=2000)
    
    print df_iter

    # get first chunk only (there must be a better way to do this but next() is not implemented for the genchunk...)
    for df in df_iter:
        print df
        break
    
    outpath = "../testdata/{0}_test.root".format(channel)
    df.to_root(outpath, key="TauCheck", mode="w")



if __name__ == '__main__':
    main()