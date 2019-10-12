from DataController import DataController
from Tools.NNCore.PredictionWrapper import PredictionWrapper

import os
import cPickle


class PredictionHelper:

    def __init__(self, settings):
        self.settings = settings
        self.file_manager = settings.prediction_file_manager
        self.parser = settings.config_parser
        self.sample_sets = settings.filtered_samples
        self.scaler = 0
        self.model = 0
        self.ext_input = settings.ext_input
        self.prediction = None
        self.setup_prediction()

    def setup_prediction(self):
        pred = PredictionWrapper(self.settings)

        scaler_path = self.file_manager.get_scaler_filepath()
        model_path = self.file_manager.get_model_filepath()

        pred.setup(model_path, scaler_path)
        self.prediction = pred

    def predict(self):

        print "scaler: ", self.scaler
        controller = DataController(self.parser.data_root_path, self.settings.folds, self.parser, self.settings, self.ext_input,
                                    sample_sets=[])

        sample_info_dicts = controller.prepare(self.sample_sets)

        first = True
        for sample_info in sample_info_dicts:
            print "predicting for " + sample_info["histname"]
            if self.ext_input:
                sample_info["path"] = sample_info["path"].replace("WJets", "W")

            filename = "NOMINAL_ntuple_" + sample_info["histname"].split("_")[0]
            filename = filename.replace("data", "Data")
            dirpath = self.file_manager.get_dir_path("prediction_output_dir")
            outpath = "{0}/{1}-{2}.root".format(dirpath, self.settings.channel, filename)

            iter = controller.read_for_prediction(sample_info)
            for data_frame in iter:
                if not self.ext_input:
                    controller.modifyDF(data_frame, sample_info)
                prediction_folds = self.prediction.get_prediction_folds(data_frame)
                self.addPredictionToOutput(prediction_folds, data_frame, outpath, first)
                first = False

    def addPredictionToOutput(self, prediction, df, outpath, new=True):

        folds = PredictionWrapper.splitInFolds(df, self.settings.folds)
        df.drop(df.index, inplace=True)

        for i in xrange(len(folds)):
            for c in prediction[i].columns.values.tolist():
                folds[i][c] = prediction[i][c]

            if i == 0 and new:
                mode = "w"
            else:
                mode = "a"
            folds[i].to_root(outpath, key="TauCheck", mode=mode)
            prediction[i].drop(prediction[i].index, inplace=True)
            folds[i].drop(folds[i].index, inplace=True)