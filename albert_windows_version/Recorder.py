import pyaudio
from Properties import Properties

AUDIO_FORMAT = pyaudio.paInt16


class Recorder:
    def __init__(self, config: Properties):
        self.conf = config
        self.stream = None
        self.audio = pyaudio.PyAudio()

    def create_stream(self):
        self.audio = pyaudio.PyAudio()

        self.stream = self.audio.open(format=AUDIO_FORMAT,
                                      channels=self.conf.CHANNELS,
                                      rate=self.conf.FRAME_RATE,
                                      input=True,
                                      frames_per_buffer=self.conf.CHUNK)

    def close_stream(self):
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()

    def read_next(self):
        if not self.stream:
            raise AttributeError("No audio stream was set up")

        return self.stream.read(self.conf.CHUNK)

    def check_microphone(self):
        if not self.audio:
            raise AttributeError("No audio stream was set up")

        for i in range(self.audio.get_device_count()):
            print(self.audio.get_device_info_by_index(i))

    def frame_length(self, seconds):
        return (self.conf.FRAME_RATE * seconds) / self.conf.CHUNK

    def continuous_record_microphone(self, execution_queue, output_queue):
        self.create_stream()

        frames = []
        while not execution_queue.empty():
            data = self.read_next()
            frames.append(data)
            if len(frames) >= self.frame_length(self.conf.STAND_BY_TIME_FRAME):
                if not output_queue.full():
                    output_queue.put(frames.copy())
                frames = []

        self.close_stream()

    def record_microphone(self, seconds=None):
        self.create_stream()
        if seconds is None:
            seconds = self.conf.STAND_BY_TIME_FRAME

        frames = []
        command = None
        recorded = False

        while not recorded:
            data = self.read_next()
            frames.append(data)
            if len(frames) >= self.frame_length(seconds):
                command = frames.copy()
                recorded = True

        self.close_stream()
        return command
