import json
import os

def main():

    C = Cut("-ISO- && -SS-", "et")

    # A = Cut("-MT-")

    # C = C.invert("-ISO-")
    # print C.original
    # C = C+A
    print C.original
    print new.original
    print C.get()

class Cut():

    cutfile = "{0}/config/default_cuts.json".format( "/".join( os.path.realpath(__file__).split("/")[:-1] ) )

    def __init__(self, cutstring, channel="", jec_shift = ""):

        self.original = cutstring
        self.channel = channel
        self.jec_shift = jec_shift
        self.cut_alias = {}
        # self.cutfile = "conf/cuts.json"

        if self.channel:
            with open(self.cutfile,"r") as FSO:
                self.cut_alias = json.load(FSO)

            self.cut_alias = self.flatten( self.cut_alias )

        self.InvertD = {
            "-SS-": "-OS-",
            "-OS-": "-SS-",
            "-ISO-": "-ANTIISO-",
            "-ANTIISO-": "-ISO-"
        }

        self.jec_quantities = [
            "met",
            "metphi",
            "met_ex",
            "met_ey",
            "m_sv",
            "pt_ttjj",
            "m_ttjj",
            # "mt_1",
            "mt_2",
            "mt_tot",
            "pt_sum",
            "njets",
            "njetspt20",
            "njetingap",
            "njetingap20",
            "mjj",
            "jdeta",
            "dijetpt",
            "dijetphi",
            "jdphi",
            "jpt_1",
            "jpt_2",
            "jeta_1",
            "jeta_2",
            "jphi_1",
            "jphi_2",
        ]

    def __add__(self, new):

        if type(new) == str: return Cut(self.original, self.channel)

        return Cut( " & ".join([self.original, new.original])  , self.channel)

    def flatten(self,obj):

        for elem in obj:
            obj[elem] = self.assertChannel(obj[elem])
        return obj


    def assertChannel(self, obj):

        if type(obj) == dict:   return obj[self.channel]
        else: return obj

    def setChannel(self, channel):
        self.channel = channel
        with open(self.cutfile,"r") as FSO:
            self.cut_alias = self.flatten( json.load(FSO) )

    def get(self, channel=""):
        if channel:
            self.setChannel(channel)

        assert self.channel

        cutstring = self.original
        for alias in self.cut_alias:

            cutstring = cutstring.replace( alias, self.cut_alias[alias])

        for jq in self.jec_quantities:
            if jq in cutstring:
                cutstring = cutstring.replace( jq, jq+self.jec_shift )

        return cutstring

    def getForDF(self):

        cutstring = self.get()

        return cutstring.replace("&&","&").replace("||","|")

    def switchCutTo(self,what):

        isos = ["-ISO-","-ANTIISO-","-ANTIISO1-","-ANTIISO2-"]
        charge = ["-SS-","-OS-"]
        cutstring = self.original

        if what in isos:
            repl = isos
        if what in charge:
            repl = charge

        for r in repl:
            if r in cutstring:
                return Cut(cutstring.replace(r, what), self.channel)


if __name__ == '__main__':
            main()
