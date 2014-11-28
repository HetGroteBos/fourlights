# Fourier based light clavier.

import numpy as np
from time import time
from math import pi

import sys

WINDOW = 2048 # Recommended values: 1024, 2048 and 4096
SLIDE = 512 # Recommended values: 128, 256, 512, 1024

SAMPLERATE = 44100

FFFT = False

GUI = True
OPENGL = False
SPECTRE = True
SPECTRE_SHADER = True
DMX = False
ECHO = False
LEWD = False

# Only relevant when using LEWD for LED visualisation
LEWDWALL_IP='10.0.20.16'
LEWDWALL_PORT=8000



if GUI:
    if OPENGL:
        from fourbargl import FourBarGL
        from fourspectrogl import FourSpectroGL
    else:
        from four2d import Four2D

if DMX:
    from fourdmx import FourDMX

if ECHO:
    from fouraudio import FourAudio

if LEWD:
    from fourlewds import FourLewds


# globals object
class Globals(object):
    pass
g = Globals()

# some keyboard globals
g.scroll_spectre = False
g.logarithmic_spectre = False
g.volume_spectre = False
g.ffft = FFFT

#fft1 = []
#fft2 = []

def freq_to_fourier(fl, hz):
    return int(fl.window * hz / fl.samplerate)


class FourLight(object):
    def __init__(self, freqs):
        self.freqs = freqs

    def blinkenlights(self, freq):
        pass


def odd_even_decomp(arr):
    odd = (arr - arr[::-1]) / 2.0
    even = arr - odd #lolwut
    #even = odd - arr
    return odd, even


class FourLights(object):

    def __init__(self, inp, lights):
        self.window = WINDOW
        self.slide = SLIDE
        self.samplerate = SAMPLERATE

        self.inp = inp
        self.lights = lights
        self.freq = np.linspace(0.2, 0.8, self.window)
        self.freql = self.freq
        self.freqr = self.freq
        self.ring = np.zeros(self.window * 2, dtype=np.int16)
        self.wave = np.zeros(self.window * 2, dtype=np.int16)
        self.wavec = np.zeros(self.window, dtype=np.int16)
        self.wavel = self.wave[::2]
        self.waver = self.wave[1::2]

        # Ring buffer position
        self.sample = 0

        self.fcs = []

    def next(self):
        if g.ffft:
            x = self._next_single_fft()
        else:
            x = self._next_dual_fft()

        return x

    def _next_dual_fft(self):
        w = (np.arange(0, 2 * (self.window / 2)) - (self.window / 2)) * (
            1.0/ (self.window/ 2))

        www = (1. - w ** 2)

        t = time()
        ifr_l = np.fft.fft(self.wavel * www)
        ifr_r = np.fft.fft(self.waver * www)
        #fft2.append(time() - t)
        #print(time() - t, 'seconds')

        self.freql = np.abs(ifr_l / ((self.window / 2) * (32768 / (self.window >> 2))))
        self.freqr = np.abs(ifr_r / ((self.window / 2) * (32768 / (self.window >> 2))))
        # TODO: remove alias.
        self.freq = self.freql
        self.ring[self.sample:self.sample + self.slide] \
            = np.frombuffer(self.inp.read(self.slide * 2), dtype=np.int16)

        self.sample += self.slide 
        self.sample %= self.window

        self.wave[:self.window * 2 - self.sample] = self.ring[self.sample:]
        self.wave[self.window * 2 - self.sample:] = self.ring[:self.sample]

        self.wavel = self.wave[::2]
        self.waver = self.wave[1::2]

        for _ in self.fcs:
            _(self)

    def _next_single_fft(self):
        w = (np.arange(0, 2 * (self.window / 2)) - (self.window / 2)) * (
            1.0/ (self.window / 2))

        www = (1. - w ** 2)

        t = time()
        ifr = np.fft.fft(self.wavec * www)
        #print(time() - t, 'seconds')

        #f(-x) = -f(x)
        freqc_odd = (ifr - ifr[::-1]) / 2.0

        #f(x) = f(-x)
        ifr -= freqc_odd

        ifr_l = ifr
        e_imag = ifr.imag
        ifr_l.imag = freqc_odd.imag
        ifr_r = freqc_odd
        ifr_r.imag = e_imag

        #ifr_l = np.sqrt(freqc_even.real ** 2 +  freqc_odd.imag ** 2)
        #ifr_r = np.sqrt(freqc_odd.real ** 2 + freqc_even.imag ** 2)
        #fft1.append(time() - t)

        #self.freql = np.abs(ifr_l / ((self.window / 2) * (32768 / (self.window >> 2))))
        self.freql = np.abs(ifr_l) / ((self.window / 2) * (32768 / (self.window >> 2)))
        self.freqr = np.abs(ifr_r) / ((self.window / 2) * (32768 / (self.window >> 2)))

        # TODO: remove alias.
        self.freq = self.freql
        self.ring[self.sample:self.sample + self.slide] \
            = np.frombuffer(self.inp.read(self.slide * 2), dtype=np.int16)

        self.sample += self.slide
        self.sample %= self.window

        self.wave[:self.window * 2 - self.sample] = self.ring[self.sample:]
        self.wave[self.window * 2 - self.sample:] = self.ring[:self.sample]

        self.wavec = www * self.wave[::2] + 1.0j * (self.wave[1::2] * www)

        for _ in self.fcs:
            _(self)

        return



if __name__ == '__main__':
    lampjes = []
    for i in xrange(3):
        lampjes.append(FourLight([SAMPLERATE / WINDOW * (j + (i * 3))
            for j in xrange(3)]))
    for tone in [0, 2, 3, 5, 7, 8, 10]:
        lampjes.append(FourLight([(220.0 * (2.0 ** (octa + (tone/12.0))))
            for octa in xrange(3)]))

    fl = FourLights(sys.stdin, lampjes)

    if DMX:
        dmx = FourDMX()
        dmx.open()

        def _write_led(fourlights):
            avg = np.sum(fourlights.freq) / fourlights.window * 2
            wr = [fourlights.freq[4 * (i + 1)] * 45 for i in xrange(9)]
            freq = np.array(fourlights.freq)
            freq[freq < avg] = 0
            freq[freq >= avg] -= avg
            wr += [freq[freq_to_fourier(fl, 220.0 * (2.0 **
                (oct + (tone/7.0))))] * 45 for tone in xrange(7)
                for oct in xrange(3)][:21]
            dmx.write(wr)

        def write_led(fourlights):
            #avg = np.sum(fourlights.freq) / fourlights.window * 2
            #wr = [fourlights.freq[4 * (i + 1)] * 45 for i in xrange(9)]
            #freq = np.array(fourlights.freq)
            #freq[freq < avg] = 0
            #freq[freq >= avg] -= avg
            #wr += [freq[freq_to_fourier(fl, 220.0 * (2.0 **
            #    (oct + (tone/7.0))))] * 45 for tone in xrange(7)
            #    for oct in xrange(3)][:21]
            wr = [fourlights.freq[freq_to_fourier(fl, freq)] * 45
                    for light in fl.lights
                    for freq in light.freqs]
            dmx.write(wr)
        fl.fcs.append(write_led)

    if ECHO:
        au = FourAudio()

        def write_wav(fourlights):
            w = fourlights.wave.tostring()
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

    if OPENGL:
        if SPECTRE:
            fgl = FourSpectroGL(fl, g, shader=SPECTRE_SHADER)
        else:
            fgl = FourBarGL(fl, g)
    else:
        fgl = Four2D(fl, g)

    fgl.run()
