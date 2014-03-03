# Fourier based light clavier.

import numpy as np
import time
from math import pi

import sys
#from wavepy import z as wav

import ctypes

RESOLUTION = 1024

from OpenGL.GLUT import *
from OpenGL.GL import *

import pyaudio

class FourLights(object):

    def __init__(self, inp):
        self.inp = inp
        self.freq = np.linspace(0.2, 0.8, RESOLUTION)
        self.doge = np.cos(np.linspace(0.0, (float(RESOLUTION - 1) / RESOLUTION) * 2 * pi, RESOLUTION))

        self.sample = 0

        self.fcs = []

    def next(self):
        self.sample += RESOLUTION
        ifr = np.fft.fft(self.doge)
        self.freq = np.abs(ifr)
        self.freq /= 1000000.0
        self.wav = np.frombuffer(self.inp.read(RESOLUTION * 4), dtype=np.int16)
        self.doge = self.wav[::2]

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
        self.win = glutCreateWindow('Fourier')

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

        cols = np.array(cols, dtype=np.float)
        self.vertices = np.array(self.vertices, dtype=np.float)
        #glColorPointer(3, GL_FLOAT, 0, [0.,] * 9)
        glColorPointer(3, GL_FLOAT, 0, cols)

    def draw(self):
        glClear(GL_COLOR_BUFFER_BIT)

        self.vertices[::4, 1] = self.fl.freq * 2 - 1
        self.vertices[3::4, 1] = self.fl.freq * 2 - 1
        glVertexPointer(2, GL_FLOAT, 0, self.vertices)

        glDrawArrays(GL_QUADS, 0, RESOLUTION * 4)

        glutSwapBuffers()


GUI = True
DMX = True
ECHO = False


if __name__ == '__main__':
    fl = FourLights(sys.stdin)

    if DMX:
        dmx = FourDMX()
        dmx.open()

        def write_led(fourlights):
            wr = [fourlights.freq[4 * (i + 1)] * 15 for i in xrange(12)]
            dmx.write(wr)

        fl.fcs.append(write_led)

    if ECHO:
        au = FourAudio()

        def write_wav(fourlights):
            w = fourlights.wav.tostring()
            au.write(w)

        fl.fcs.append(write_wav)

    if not GUI:
        while True:
            fl.next()

        exit(0)

    fgl = FourGL(fl)

    # TODO: GUI Hacks follow

    def idle():
        fl.next()
        glutPostRedisplay()

    # Handle keyboard input
    def keyboard(c, x, y):
        pass

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
