import pyaudio

class FourAudio(object):

    def __init__(self):
        p = pyaudio.PyAudio()
        self.stream = p.open(format=p.get_format_from_width(2),
                        channels=2,
                        rate=44100,
                        output=True)

    def write(self, wav):
        self.stream.write(wav)
