from abc import abstractmethod

from scipy import signal


class Converter(object):

    @abstractmethod
    def apply(self, data):
        pass


class LowPassFilter(Converter):

    def __init__(self, cutoff_frequency):
        self.cutoff_frequency = cutoff_frequency
        self.state = None

    def apply(self, data):
        b = signal.firwin(150, self.cutoff_frequency, fs=256)
        if self.state is None:
            self.state = signal.lfilter_zi(b, 1) * data
        result, self.state = signal.lfilter(b, 1, [data], zi=self.state)
        return result
