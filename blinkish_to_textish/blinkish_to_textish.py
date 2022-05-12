import datetime
import queue
from enum import Enum
from threading import Thread, Lock, Timer

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

import muse.muse
from eeg_commons.eeg_commons import EEGSeries, EEGChannel
from muse import muse
from eeg_commons import eeg_commons

CHANNEL_USED_FOR_DETECTION = EEGChannel.TP9
BLINKING_START_FALL = 100
BLINKING_STOP_RISE = 35

NORMAL_SHORT_BLINK_BORDER = 200
SHORT_LONG_BLINK_BORDER = 450
LONG_VERY_LONG_BLINK_BORDER = 1200

DATA_DROP_RATIO = 2

fig = plt.figure(figsize=(12, 6))

animation = None
blink_detector = None
my_muse = None


class Blink(Enum):
    NORMAL_BLINK = 1
    SHORT_BLINK = 2
    LONG_BLINK = 3
    VERY_LONG_BLINK = 4
    PAUSE = 5


class MorseCode(Enum):
    A = ('a', '.-')
    B = ('b', '-...')
    C = ('c', '-.-.')
    D = ('d', '-..')
    E = ('e', '.')
    F = ('f', '..-.')
    G = ('g', '--.')
    H = ('h', '....')
    I = ('i', '..')
    J = ('j', '.---')
    K = ('k', '-.-')
    L = ('l', '.-..')
    M = ('m', '--')
    N = ('n', '--')
    O = ('o', '---')
    P = ('p', '.--.')
    Q = ('q', '--.-')
    R = ('r', '.-.')
    S = ('s', '...')
    T = ('t', '-')
    U = ('u', '..-')
    V = ('v', '...-')
    W = ('w', '.--')
    X = ('x', '-..-')
    Y = ('y', '-.--')
    Z = ('z', '--..')
    N_1 = ('1', '.----')
    N_2 = ('2', '..---')
    N_3 = ('3', '...--')
    N_4 = ('4', '....-')
    N_5 = ('5', '.....')
    N_6 = ('6', '-....')
    N_7 = ('7', '--...')
    N_8 = ('8', '---..')
    N_9 = ('9', '----.')
    N_0 = ('0', '-----')

    def __init__(self, character, code):
        self.character = character
        self.code = code

    @classmethod
    def get_character(cls, morse_code):
        for name, member in MorseCode.__members__.items():
            if member.code == morse_code:
                return member.character
        return None

class BlinkDetector:

    def __init__(self):
        self.eeg_series = EEGSeries(muse.Muse.eeg_channels, 480)
        self.eeg_series_lock = Lock()
        self.blinking_start_time = None
        self.max = 0
        self.data_queue = queue.Queue(0)
        self.running = False
        self.detector = Thread(target=self.detect, daemon=True)
        self.drop_counter = 0
        self.pause_timer = None
        self.blink_listener_callbacks = []
        self.blinks = []
        print('Blink detector initialized')

    def add_blink_listener_callback(self, callback):
        self.blink_listener_callbacks.append(callback)

    def start(self):
        self.detector.start()

    def detect(self):
        print('Blink detector started')
        self.running = True
        while self.running:
            try:
                eeg_data = self.data_queue.get(True, 0.1)
                self.eeg_series_lock.acquire()
                self.eeg_series.add(eeg_data)
                self.eeg_series_lock.release()
                self.detect_blink(eeg_data)
            except queue.Empty as e:
                pass

    def stop(self):
        self.running = False

    def update_plot(self, i):
        plt.clf()
        plt.xlabel('Time')
        plt.ylabel(CHANNEL_USED_FOR_DETECTION)
        plt.xlim(0, 480)
        plt.ylim(400, 1200)
        self.eeg_series_lock.acquire()
        plt.plot(self.eeg_series.time_series[CHANNEL_USED_FOR_DETECTION].elements)
        self.eeg_series_lock.release()

    def detect_blink(self, data):
        self.eeg_series_lock.acquire()
        base_level = self.eeg_series.get_median(CHANNEL_USED_FOR_DETECTION)
        self.eeg_series_lock.release()
        channel_value = data.get_channel_value(CHANNEL_USED_FOR_DETECTION)
        if channel_value > self.max:
            self.max = channel_value
        if (channel_value < base_level - BLINKING_START_FALL) and (self.blinking_start_time is None):
            self.blinking_start_time = datetime.datetime.now()
            if self.pause_timer is not None:
                self.pause_timer.cancel()
        if (self.blinking_start_time is not None) and (channel_value > base_level + BLINKING_STOP_RISE):
            blinking_end_time = datetime.datetime.now()
            blink_length = (blinking_end_time - self.blinking_start_time).total_seconds() * 1000
            blink = BlinkDetector.classify_blink(blink_length)
            for callback in self.blink_listener_callbacks:
                callback(blink, blink_length)
            if blink == Blink.VERY_LONG_BLINK:
                # Resetting conversion
                self.blinks.clear()
            else:
                self.blinks.append(blink)
            self.blinking_start_time = None
            if blink == Blink.SHORT_BLINK or blink == Blink.LONG_BLINK:
                self.pause_timer = Timer(1, self.pause_detected, args=['Pause detected'])
                self.pause_timer.start()

    @staticmethod
    def classify_blink(blink_length):
        if blink_length < NORMAL_SHORT_BLINK_BORDER:
            blink = Blink.NORMAL_BLINK
        elif blink_length < SHORT_LONG_BLINK_BORDER:
            blink = Blink.SHORT_BLINK
        elif blink_length < LONG_VERY_LONG_BLINK_BORDER:
            blink = Blink.LONG_BLINK
        else:
            blink = Blink.VERY_LONG_BLINK
        return blink

    def handle_eeg(self, data):
        if self.drop_counter % DATA_DROP_RATIO != 0:
            self.drop_counter += 1
            return
        else:
            self.drop_counter = 1
        if data is not None:
            if hasattr(self, 'converter'):
                processed_data = self.converter.convert(data)
            else:
                processed_data = data
            self.data_queue.put(processed_data)

    def pause_detected(self, message):
        for callback in self.blink_listener_callbacks:
            callback(Blink.PAUSE, 0)


def start_blink_detection(port, blink_listener, plot_eeg):
    global my_muse
    my_muse = muse.Muse('0.0.0.0', port)
    print('Register for ' + str(eeg_commons.DataType.EEG))
    global blink_detector
    blink_detector = BlinkDetector()
    blink_detector.add_blink_listener_callback(blink_listener)
    blink_detector.start()
    my_muse.add_listener(eeg_commons.DataType.EEG, blink_detector.handle_eeg)
    my_muse.start()
    if plot_eeg:
        global animation
        animation = FuncAnimation(fig, blink_detector.update_plot, interval=40)
        plt.show()


def stop_blink_detection():
    print('Stopping blink detection')
    blink_detector.stop()
    print('Stopping Muse')
    my_muse.stop()


if __name__ == "__main__":
    start_blink_detection(5000, True)

