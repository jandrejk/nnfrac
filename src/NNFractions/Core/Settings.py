class Settings:

    def __init__(self, channel, era, scaler="none"):
        self.channel = channel
        self.era = era
        self.scaler = scaler

    def __str__(self):
        result = ""
        result += "[Settings: " + "\n"
        result += "Channel: " + self.channel + "\n"
        result += "Era: " + self.era + "\n"
        result += "Scaler: " + self.scaler + "]" + "\n"
        return result
