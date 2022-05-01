from enum import Enum
from statistics import mean, median
import datetime


class DataType(Enum):
    EEG = 1
    GYROSCOPE = 2
    ACCELEROMETER = 3


class EEGChannel(Enum):
    AF7 = 1
    AF8 = 2
    TP9 = 3
    TP10 = 4
    AUX = 5


class EEGChannelMapping:
    def __init__(self, *args):
        self.index_to_channel = {}
        self.channel_to_index = {}

    def add_mapping(self, index, channel):
        self.index_to_channel[index] = channel
        self.channel_to_index[channel] = index

    def get_channel(self, index):
        return self.index_to_channel[index]

    def get_index(self, channel):
        return self.channel_to_index[channel]


class Data(object):
    def __init__(self, data_type):
        self.creation_time = datetime.datetime.now()
        self.type = data_type


class EEG(Data):

    @classmethod
    def create_eeg_data_map(cls, channel_mapping, data_tuple):
        data_per_channel = {}
        for idx, data in enumerate(data_tuple):
            data_per_channel[channel_mapping.get_channel(idx)] = data
        return data_per_channel

    def __init__(self, eeg_data_map):
        super(EEG, self).__init__(DataType.EEG)
        self.data_per_channel = eeg_data_map

    def get_channel_value(self, eeg_channel):
        return self.data_per_channel[eeg_channel]

    def channel_count(self):
        return len(self.data_per_channel)

    def get_channels(self):
        return self.data_per_channel.keys()


class Gyroscope(Data):
    def __init__(self, *args):
        super(Gyroscope, self).__init__(DataType.GYROSCOPE)
        self.x = args[0]
        self.y = args[1]
        self.z = args[2]

    def get_up_down_location(self):
        return self.x

    def get_tilt(self):
        return self.y


# TODO: check and fix x,y,z meaning
class Accelerometer(Data):
    def __init__(self, *args):
        super(Accelerometer, self).__init__(DataType.ACCELEROMETER)
        self.x = args[0]
        self.y = args[1]
        self.z = args[2]

    def get_left_right_pitch_acc(self):
        return self.x

    def get_up_down_acc(self):
        return self.y

    def get_left_right_acc(self):
        return self.z


class WindowedSeries:
    def __init__(self, window_size):
        self.elements = []
        self.window_size = window_size

    def add_element(self, element):
        self.elements.append(element)
        if self.window_size == len(self.elements):
            del (self.elements[0])

    def get_average(self):
        if len(self.elements) == 0:
            return 0
        return mean(self.elements)

    def get_median(self):
        if len(self.elements) == 0:
            return 0
        return median(self.elements)


class EEGSeries:
    def __init__(self, eeg_channels, series_length):
        self.time_series = {}
        self.last_stamp = None
        for channel in eeg_channels:
            self.time_series[channel] = WindowedSeries(series_length)

    def add(self, eeg_data):
        if self.last_stamp is not None and (eeg_data.creation_time - self.last_stamp).total_seconds() < 0:
            print('Data from past: ' + str((eeg_data.creation_time - self.last_stamp).total_seconds() * 1000))
            return
        else:
            self.last_stamp = eeg_data.creation_time
        channels = eeg_data.get_channels()
        for channel in channels:
            self.time_series[channel].add_element(eeg_data.get_channel_value(channel))

    def get_median(self, channel):
        return self.time_series[channel].get_median()


class EEGConverter:
    def __init__(self, converter):
        self.converter = converter

    def convert(self, data):
        converted_data = {}
        for channel in data.data_per_channel.keys():
            converted_data[channel] = self.converter.apply(data.data_per_channel[channel])
        return EEG(converted_data)
