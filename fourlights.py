# Fourier based light clavier.

import numpy as np
import time
from math import pi

import sys
#from wavepy import z as wav

import ctypes

#RESOLUTION = 512
#RESOLUTION = 128
RESOLUTION = 1024
SAMPLERATE = 44100

LEWDWALL_IP='10.0.20.16'
LEWDWALL_PORT=8000

SPECTROGRAM_LENGTH = 1024
#SPECTROGRAM_LENGTH = 256

from OpenGL.GLUT import *
from OpenGL.GL import *

import pyaudio

# globals object
class Globals(object):
    pass
g = Globals()

# some keyboard globals
g.scroll_spectre = False

def freq_to_fourier(hz):
    return int(RESOLUTION * hz / SAMPLERATE)

class FourLight(object):
    def __init__(self, freqs):
        self.freqs = freqs

    def blinkenlights(self, freq):
        pass

class FourLights(object):

    def __init__(self, inp, lights):
        self.inp = inp
        self.lights = lights
        self.freq = np.linspace(0.2, 0.8, RESOLUTION)
        self.freql = self.freq
        self.freqr = self.freq
        self.doge = np.cos(np.linspace(0.0, (float(RESOLUTION - 1) / RESOLUTION) * 2 * pi, RESOLUTION))
        self.doger = self.doge
        self.dogel = self.doge

        self.sample = 0

        self.fcs = []

    def next(self):
        self.sample += RESOLUTION

        w = (np.arange(0, 2 * (RESOLUTION / 2)) - (RESOLUTION / 2)) * (
            1.0/ (RESOLUTION / 2))

        www = (1. - w ** 2)

        ifr_l = np.fft.fft(self.dogel * www)
        ifr_r = np.fft.fft(self.doger * www)
        #self.freql = np.abs(ifr_l / (32768 * (RESOLUTION / 2)))
        #self.freqr = np.abs(ifr_r / (32768 * (RESOLUTION / 2)))
        #self.freql = np.abs(ifr_l / (32768 * (RESOLUTION / 100)))
        #self.freqr = np.abs(ifr_r / (32768 * (RESOLUTION / 100)))
        self.freql = np.abs(ifr_l / ((RESOLUTION / 2) * (32768 / (RESOLUTION >> 2))))
        self.freqr = np.abs(ifr_r / ((RESOLUTION / 2) * (32768 / (RESOLUTION >> 2))))
        # TODO: remove alias.
        self.freq = self.freql
        self.wav = np.frombuffer(self.inp.read(RESOLUTION * 4), dtype=np.int16)
        self.dogel = self.wav[::2]
        self.doger = self.wav[1::2]

        for _ in self.fcs:
            _(self)

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

class FourAudio(object):

    def __init__(self):
        p = pyaudio.PyAudio()
        self.stream = p.open(format=p.get_format_from_width(2),
                        channels=2,
                        rate=44100,
                        output=True)

    def write(self, wav):
        self.stream.write(wav)

class FourGL(object):
    def __init__(self, fourlights):

        glutInit()

        self.fl = fourlights

        # Setup OpenGL Window
        glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE)
        self.win = glutCreateWindow('Fourlights')

        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_COLOR_ARRAY)

        self.create_vertices()

    def create_vertices(self):
        cols = []
        self.vertices = []
        for i in xrange(RESOLUTION):
            p = float(i) / RESOLUTION
            r = (1.0 / RESOLUTION) * 1.9
            for _ in xrange(4):
                cols.append((p, 0, 1 - p))
            x = p * 2 - 1
            self.vertices.append((x, p * 2 - 1))
            self.vertices.append((x, -1))
            self.vertices.append((x + r, -1))
            self.vertices.append((x + r, p * 2 - 1))

        self.cols = np.array(cols, dtype=np.float)
        self.vertices = np.array(self.vertices, dtype=np.float)
        #glColorPointer(3, GL_FLOAT, 0, [0.,] * 9)

        # Create light pointers
        self.pointer_verts = []
        self.pointer_cols = []
        for light in self.fl.lights:
            print light.freqs
            for freq, colour in zip(light.freqs,
                    (np.identity(3) * 255.0).tolist()):
                x = (float(freq_to_fourier(freq) + .5) / RESOLUTION) * 2 - 1
                hs = 1.0 / RESOLUTION
                #hs *= 5
                self.pointer_verts.extend([
                        (x - hs, 0),
                        (x, -hs * 45),
                        (x + hs, 0)
                    ])
                for _ in xrange(3):
                    self.pointer_cols.append(colour)

        self.pointer_cols = np.array(self.pointer_cols, dtype=np.float)
        self.pointer_verts = np.array(self.pointer_verts, dtype=np.float)

        print self.pointer_verts

    def draw(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        #glOrtho(-1.0, -.8, -1.0, 1.0, -1.0, 1.0)
        glMatrixMode(GL_MODELVIEW)

        glClear(GL_COLOR_BUFFER_BIT)

        self.vertices[::4, 1] = self.fl.freq * 2 - 1
        self.vertices[3::4, 1] = self.fl.freq * 2 - 1
        glColorPointer(3, GL_FLOAT, 0, self.cols)
        glVertexPointer(2, GL_FLOAT, 0, self.vertices)
        glDrawArrays(GL_QUADS, 0, RESOLUTION * 4)

        glColorPointer(3, GL_FLOAT, 0, self.pointer_cols)
        glVertexPointer(2, GL_FLOAT, 0, self.pointer_verts)
        glDrawArrays(GL_TRIANGLES, 0, len(self.fl.lights) * 3 * 3)

        glutSwapBuffers()

    def idle(self):
        pass

class FourSpectroGL(object):
    def __init__(self, fourlights):

        glutInit()

        self.fl = fourlights

        # Setup OpenGL Window
        glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE)
        self.win = glutCreateWindow('Fourlights')

        self.spectrogram = glGenTextures(1)
        self.frame_counter = 0

        glBindTexture(GL_TEXTURE_2D, self.spectrogram)

        # Tightly packed data
        glPixelStorei(GL_PACK_ALIGNMENT, 1)
        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)

        # Clear texture (black)
        texdata = np.zeros((SPECTROGRAM_LENGTH, RESOLUTION / 2, 3), dtype=np.byte)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB8, SPECTROGRAM_LENGTH, RESOLUTION / 2,
            0, GL_RGB, GL_UNSIGNED_BYTE, texdata)

        # Simple interpolation and repeat
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

        # Finally enable texture visiblity
        glEnable(GL_TEXTURE_2D)

    def draw(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        #glOrtho(-1.0, -.8, -1.0, 1.0, -1.0, 1.0)
        glMatrixMode(GL_MODELVIEW)

        # Update spectogram
        #texdata = np.reshape(np.array(self.fl.freq * 10000, dtype=np.byte), (-1, 1))[:, [0, 0, 0]]
        #texdata = np.reshape(np.array(self.fl.freq * 100, dtype=np.byte), (-1, 1))[:, [0, 0, 0]]
        #texdata = np.reshape(np.array(np.minimum(self.fl.freq[:RESOLUTION / 2] * 255 * 40, 255), dtype=np.ubyte), (-1, 1))[:, [0, 0, 0]]
        #texdata = np.reshape(np.array(np.minimum(self.fl.freq * 255 * 1, 255), dtype=np.ubyte), (-1, 1))[:, [0, 0, 0]]
        #texdata = np.reshape(np.array(np.minimum(self.fl.freq * 255 * 40, 255), dtype=np.ubyte), (
        glClear(GL_COLOR_BUFFER_BIT)

        if g.scroll_spectre:
            base = self.frame_counter / float(SPECTROGRAM_LENGTH)
        else:
            base = 0.0

        clamp = 0.0
        if True:
            clamp = 0.5

        glBegin(GL_QUADS)
        glTexCoord(base + 0.0, 1.0 - clamp)
        glVertex(-1,  1)

        glTexCoord(base + 0.0, 0.0)
        glVertex(-1, -1)

        glTexCoord(base + 1.0, 0.0)
        glVertex( 1, -1)

        glTexCoord(base + 1.0, 1.0 - clamp)
        glVertex( 1,  1)
        glEnd()

        glutSwapBuffers()

    def idle(self):
        frl = np.reshape(np.array(np.minimum(self.fl.freql[:RESOLUTION / 2] * 255 * 1, 255), dtype=np.ubyte), (-1, 1))
        frr = np.reshape(np.array(np.minimum(self.fl.freqr[:RESOLUTION / 2] * 255 * 1, 255), dtype=np.ubyte), (-1, 1))
        texdata = np.hstack((frl, frr, frr / 2 + frl / 2))

        #print texdata[1:5]
        glTexSubImage2D(GL_TEXTURE_2D, 0, self.frame_counter, 0, 1, RESOLUTION / 2,
            GL_RGB, GL_UNSIGNED_BYTE, texdata)

        self.frame_counter = (self.frame_counter + 1) % SPECTROGRAM_LENGTH

class FourLewds(object):
    def __init__(self):
        sys.path.insert(0, './lewd/src')
        from remotescreen import RemoteScreen
        self.w = 10
        self.h = 12
        self.screen = RemoteScreen(LEWDWALL_IP, LEWDWALL_PORT,
            dimension=(self.w,self.h))

        # hoi
        f = [[(0, 0, 0) for y in range(self.h)] for x in range(self.w)]
        self.screen.load_frame(f)
        self.screen.push()

    def write(self, freq):
        fr = [freq[10 * (i + 1)] for i in xrange(12)]
        f = [[(0, 0, 0) for y in range(self.h)] for x in range(self.w)]

        def fill_bar(bar, fill):
            for idx in range(fill):
                f[9 - idx][bar] = (0, 30, 75)

        for ind, frq in enumerate(fr):
            #frq =frq*75
            frq =frq*25
            bars = int(round(min(frq, 10)))

            fill_bar(ind, bars)

        self.screen.load_frame(f)
        self.screen.push()

GUI = True
SPECTRE = True
DMX = False
ECHO = False
LEWD = False

if __name__ == '__main__':
    lampjes = []
    for i in xrange(3):
        lampjes.append(FourLight([SAMPLERATE / RESOLUTION * (j + (i * 3))
            for j in xrange(3)]))
    for tone in [0, 2, 3, 5, 7, 8, 10]:
        lampjes.append(FourLight([(220.0 * (2.0 ** (octa + (tone/12.0))))
            for octa in xrange(3)]))

    fl = FourLights(sys.stdin, lampjes)

    if DMX:
        dmx = FourDMX()
        dmx.open()

        def _write_led(fourlights):
            avg = np.sum(fourlights.freq) / RESOLUTION * 2
            wr = [fourlights.freq[4 * (i + 1)] * 45 for i in xrange(9)]
            freq = np.array(fourlights.freq)
            freq[freq < avg] = 0
            freq[freq >= avg] -= avg
            wr += [freq[freq_to_fourier(220.0 * (2.0 **
                (oct + (tone/7.0))))] * 45 for tone in xrange(7)
                for oct in xrange(3)][:21]
            dmx.write(wr)

        def write_led(fourlights):
            #avg = np.sum(fourlights.freq) / RESOLUTION * 2
            #wr = [fourlights.freq[4 * (i + 1)] * 45 for i in xrange(9)]
            #freq = np.array(fourlights.freq)
            #freq[freq < avg] = 0
            #freq[freq >= avg] -= avg
            #wr += [freq[freq_to_fourier(220.0 * (2.0 **
            #    (oct + (tone/7.0))))] * 45 for tone in xrange(7)
            #    for oct in xrange(3)][:21]
            wr = [fourlights.freq[freq_to_fourier(freq)] * 45
                    for light in fl.lights
                    for freq in light.freqs]
            dmx.write(wr)
        fl.fcs.append(write_led)

    if ECHO:
        au = FourAudio()

        def write_wav(fourlights):
            w = fourlights.wav.tostring()
            au.write(w)

        fl.fcs.append(write_wav)

    if LEWD:
        lewd = FourLewds()

        def write_lewd(fourlights):
            lewd.write(fourlights.freq)

        fl.fcs.append(write_lewd)

    if not GUI:
        while True:
            fl.next()

        exit(0)

    if SPECTRE:
        fgl = FourSpectroGL(fl)
    else:
        fgl = FourGL(fl)

    # TODO: GUI Hacks follow

    hoi = 0
    frames = 0
    def idle():
        global hoi, frames

        fl.next()
        hoi += 1
        frames += 1
        if hoi > 1 or True:
            hoi = 0
            glutPostRedisplay()
        fgl.idle()

    # Handle keyboard input
    def keyboard(c, x, y):
        if c == 's':
            g.scroll_spectre = not g.scroll_spectre

    def render():
        fgl.draw()

    # Window size changed
    def reshape(width, height):
        global glob_w, glob_h
        glob_w, glob_h = width, height
        glViewport(0, 0, width, height)


    # Setup remaining callbacks and start the program
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard)
    glutIdleFunc(idle)

    #glClearColor(0.2, 0.4, 0.8, 1.0)
    glutDisplayFunc(render)

    glutMainLoop()
