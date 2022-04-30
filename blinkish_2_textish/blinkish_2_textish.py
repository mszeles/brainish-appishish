import datetime
import queue
from threading import Thread

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

import muse.muse
from eeg_commons.eeg_commons import EEGSeries, EEGChannel
from muse import muse
from eeg_commons import eeg_commons

CHANNEL_USED_FOR_DETECTION = EEGChannel.TP9
BLINKING_START_FALL = 50
BLINKING_STOP_RISE = 20
ip = '0.0.0.0'
port = 5000

fig = plt.figure(figsize=(12, 6))


class BlinkDetector:

    def __init__(self):
        self.eeg_series = EEGSeries(muse.Muse.eeg_channels, 480)
        self.blinking_start_time = None
        self.max = 0
        self.data_queue = queue.Queue()
        self.running = False
        self.detector = Thread(target=self.detect)
        print('Blink detector initialized')

    def start(self):
        self.detector.start()

    def detect(self):
        print('Blink detector started')
        self.running = True
        while self.running:
            eeg_data = self.data_queue.get(True, 1)
            if eeg_data:
                self.detect_blink(eeg_data)

    def stop(self):
        self.running = False

    def update_plot(self, i):
        plt.clf()
        plt.xlabel('Time')
        plt.ylabel(CHANNEL_USED_FOR_DETECTION)
        plt.xlim(0, 480)
        plt.ylim(400, 1200)
        plt.plot(self.eeg_series.time_series[CHANNEL_USED_FOR_DETECTION].elements)

    def detect_blink(self, data):
        base_level = self.eeg_series.get_median(CHANNEL_USED_FOR_DETECTION)
        channel_value = data.get_channel_value(CHANNEL_USED_FOR_DETECTION)
        if channel_value > self.max:
            self.max = channel_value
        # print('Base level: ' + str(base_level) + ' channel value: ' + str(channel_value) + ' max: ' + str(self.max))
        if (channel_value < base_level - BLINKING_START_FALL) and (self.blinking_start_time is None):
            self.blinking_start_time = datetime.datetime.now()
        if (self.blinking_start_time is not None) and (channel_value > base_level + BLINKING_STOP_RISE):
            blinking_end_time = datetime.datetime.now()
            blink_length = (blinking_end_time - self.blinking_start_time).total_seconds() * 1000
            print('Blink with length: ' + str(blink_length))
            self.blinking_start_time = None

    def handle_eeg(self, data):
        if data is not None:
            self.eeg_series.add(data)
            self.data_queue.put(data)


if __name__ == "__main__":
    my_muse = muse.Muse('0.0.0.0', 5000)
    print('Register for ' + str(eeg_commons.DataType.EEG))
    blink_detector = BlinkDetector()
    blink_detector.start()
    my_muse.add_listener(eeg_commons.DataType.EEG, blink_detector.handle_eeg)
    my_muse.start()
    global animation
    animation = FuncAnimation(fig, blink_detector.update_plot, interval=40)
    plt.show()