class Settings:

    def __init__(self, channel, era, ml_type="keras", scaler="none"):
        self.channel = channel
        self.era = era
        self.ml_type = ml_type
        self.scaler = scaler
        self.ext_input = False
        self.config_parser = None
        self.filtered_samples = None
        self.model_file_manager = None
        self.prediction_file_manager = None
        self.fraction_plot_file_manager = None

    def __str__(self):
        result = ""
        result += "[Settings: " + "\n"
        result += "ML Type: " + self.ml_type + "\n"
        result += "Channel: " + self.channel + "\n"
        result += "Era: " + self.era + "\n"
        result += "Scaler: " + self.scaler + "]" + "\n"
        return result
