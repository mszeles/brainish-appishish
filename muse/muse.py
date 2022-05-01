from pythonosc import dispatcher
from pythonosc import osc_server
from eeg_commons.eeg_commons import EEG, Gyroscope, Accelerometer, EEGChannelMapping, EEGChannel
from threading import Thread

addresses = []


class MuseEEGChannelMapping(EEGChannelMapping):
    def __init__(self):
        super(MuseEEGChannelMapping, self).__init__()
        self.add_mapping(0, EEGChannel.TP9)
        self.add_mapping(1, EEGChannel.AF7)
        self.add_mapping(2, EEGChannel.AF8)
        self.add_mapping(3, EEGChannel.TP10)
        self.add_mapping(4, EEGChannel.AUX)


MUSE_EEG_CHANNEL_MAPPING = MuseEEGChannelMapping()


class MuseEEG(EEG):
    def __init__(self, *args):
        super(MuseEEG, self).__init__(EEG.create_eeg_data_map(MUSE_EEG_CHANNEL_MAPPING, args[0]))


class Muse:
    eeg_channels = [EEGChannel.AF7, EEGChannel.TP9, EEGChannel.TP10, EEGChannel.AF8, EEGChannel.AUX]

    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.listener_thread = None
        self.server = None
        self.listeners = {}

    def add_listener(self, data_type, data_arrived_func):
        if data_type not in self.listeners.keys():
            self.listeners[data_type] = []
        self.listeners[data_type].append(data_arrived_func)

    def notify_listeners(self, data):
        if data.type in self.listeners.keys():
            for callback in self.listeners[data.type]:
                callback(data)

    def handler(self, address: str, *args):
        if address.endswith('eeg'):
            self.notify_listeners(MuseEEG(args))
            #    elif address.endswith('gyro'):
        #        self.notify_listeners(Gyroscope(args))
        #    elif address.endswith('acc'):
        #        self.notify_listeners(Accelerometer(args))

        if address not in addresses:
            addresses.append(address)
            print(address)
        raw_entry = str(address) + ':'
        for arg in args:
            raw_entry += "," + str(arg)
        # print(raw_entry)

    def start_muse_listening(self):
        disp = dispatcher.Dispatcher()
        disp.map("/*", self.handler)
        print("Connecting to  " + self.ip + ":" + str(self.port))
        self.server = osc_server.ThreadingOSCUDPServer((self.ip, self.port), disp)
        print("Connected")
        self.server.serve_forever()

    def start(self):
        thread = Thread(target=self.start_muse_listening)
        thread.start()

    def stop(self):
        self.server.close()
