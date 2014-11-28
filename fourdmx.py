import ctypes

class FourDMX(object):
    def __init__(self):
        self.dmx = ctypes.CDLL('./usb.so')

        self.dmx.open_dmx.argtypes = []
        self.dmx.open_dmx.restype = ctypes.c_void_p
        self.dmx.write_buf.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int]
        self.dmx.write_buf.restype = ctypes.c_int

    def open(self):
        self.dmx_ctx = self.dmx.open_dmx()
        return self.dmx_ctx

    def write(self, z):
        self.dmx.write_buf(self.dmx_ctx, str(np.array(z, dtype=np.byte).data), len(z))
