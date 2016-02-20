"""
This is the container class that passes data between configure_periphery and run_periphery
"""


class PeripheryOutput:

    def __init__(self):
        # this used to be called "a"
        self.bmAcceleration = []
        # this used to be called "v"
        self.bmVelocity = []
        # this used to be called "y"
        self.bmDisplacement = []
        self.emission = []
        self.cf = []
        self.ihc = []
        self.anfHSR = []
        self.anfMSR = []
        self.anfLSR = []