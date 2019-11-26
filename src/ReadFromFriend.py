import root_numpy as rn
import ROOT as R
from ROOT import TFile
import pandas as pd
import root_pandas as rp
from pandas import DataFrame, concat
import copy
import os

from Tools.CutObject.CutObject import Cut


def main():
    
    channel = "mt"

    dirpath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../testdata/friends")
    main_path = os.path.join(dirpath, "main.root")
    friend_path = os.path.join(dirpath, "friend.root")
    
    #root_example(main_path, friend_path)

    Cut.cutfile = os.path.join(os.path.dirname(os.path.realpath(__file__)), "cuts_2017.json")
    cut = Cut(cutstring="-OS- && -ANTIISO- && -VETO- && -MT- && -TRIG-", channel=channel)

    root_pandas_example(main_path, friend_path, cut, ["pt_1", "pt_2", "jetFakes"])


def root_example(main_path, friend_path):
    tfile1 = R.TFile(main_path, "read")
    
    tree1 = tfile1.TauCheck
    # TODO: check if renaming the tree is necessary
    tree1.AddFriend("TauCheck2=TauCheck", friend_path)
    cv0 = R.TCanvas()
    tree1.Draw("pt_2")
    cv1 = R.TCanvas()    
    tree1.Draw("TauCheck2.jetFakes")
    cv2 = R.TCanvas()    
    tree1.Draw("pt_2:TauCheck2.jetFakes")
    
    x = raw_input("raw input")

def root_pandas_example(main_path, friend_path, cut, branches):
    
    # example: want to read branches ["pt_1", "pt_2", "jetFakes"] using a selection cut like
    # Cut(cutstring="-OS- && -ANTIISO- && -VETO- && -MT- && -TRIG-", channel=channel)

    # problem 1: pt_1 and pt_2 are branches in main.root; jetFakes is a branch in friend.root
    # pt_1 and pt_2 missing in friend.root; jetFakes missing in main.root
    # -> no common columns for reading directly

    # problem 2: friend.root does not contain the branches needed for evaluating the selection cut

    # solution: add tree from friend.root as friend to the tree in main.root

    tfile1 = R.TFile(main_path, "read")    
    tree1 = tfile1.TauCheck
    # TODO: check if renaming the tree is necessary
    tree1.AddFriend("TauCheck2=TauCheck", friend_path)
    
    arr = rn.tree2array(tree1, ["pt_1", "pt_2", "jetFakes"], selection=cut.get())
    df = rp.readwrite.convert_to_dataframe(arr)

    print df

if __name__ == '__main__':
    main()