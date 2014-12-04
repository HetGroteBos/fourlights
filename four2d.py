import pygame
import pygame.surfarray
#from pygame.locals import *

import numpy as np

from time import time

class Four2D(object):

    def __init__(self, fourlights):
        self.fl = fourlights

        self.w = 512 # 1920 / 2
        self.h = 1024
        self.resize(self.w, self.h)

        self.curr = 0

        self.logarithmic = False
        self.interpolate = False

        pygame.init()

    def resize(self, w, h):
        self.w = w
        self.h = h

        self.screen = pygame.display.set_mode((self.w, self.h), pygame.RESIZABLE, 32)
        self.surface = pygame.display.get_surface()
        self.pixels = pygame.surfarray.pixels2d(self.surface)

    def draw(self):
        # TODO: Optimise this
        if self.logarithmic:
            left = self.fl.freql[:self.fl.window / 2][::1] * 220
            right = self.fl.freqr[:self.fl.window / 2][::1] * 220

            newpixelindex = (22100.0 ** np.linspace(0.41, 1.0, self.h, endpoint=False)) / 22100.0
            #newpixelindex = (22100.0 ** np.linspace(0.0, 1.0, self.h, endpoint=False)) / 22100.0

            newpixelindex *= (self.fl.window / 2)
            #newpixelindex %= (self.fl.window / 2)

            # Scale up to self.fl.window / 2
            #newpixelindex *= self.fl.window / 2
            newpixelindex = newpixelindex.astype(int)[::-1]


            lvals = left[newpixelindex]
            rvals = right[newpixelindex]

            #if self.interpolate:
            #    lvals = np.correlate(lvals, [0.2, 0.6, 0.2], "same")
            #    rvals = np.correlate(rvals, [0.2, 0.6, 0.2], "same")


            r = rvals.astype(np.int) << 16
            g = lvals.astype(np.int) << 8
            b = ((lvals + rvals) / 2).astype(np.int)

            b = b | b << 8 | b << 16

            self.pixels[self.curr,:] = r | g | b
        else:
            left = self.fl.freql[:self.fl.window / 2][::-1] * 220
            right = self.fl.freqr[:self.fl.window / 2][::-1] * 220

            pixelindex = np.linspace(0., (self.fl.window / 2), self.h, endpoint=False).astype(np.int)

            lvals = left[pixelindex]
            rvals = right[pixelindex]

            r = rvals.astype(np.int) << 16
            g = lvals.astype(np.int) << 8
            b = ((lvals + rvals) / 2).astype(np.int)

            b = b | b << 8 | b << 16

            self.pixels[self.curr,:] = r | g | b

        up = pygame.Rect(self.curr, 0, self.curr, self.h)

        pygame.display.update(up)

        self.curr = (self.curr + 1) % self.w

        #clock.tick(60)

        #pygame.display.flip()

    def run(self):
        while True:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    return

                if e.type == pygame.KEYUP:
                    if e.key == pygame.K_l:
                        self.logarithmic = not self.logarithmic
                        print 'Log switch'

                    if e.key == pygame.K_i:
                        self.interpolate = not self.interpolate
                        print 'Interpolate switch'

                    if e.key == pygame.K_s:
                        print('TODO: Saving.')

                if e.type == pygame.VIDEORESIZE:
                    w, h = e.dict['size']
                    self.resize(w, h)

            #t = time()
            self.fl.next()
            #print('FL time', time() - t)

            #t = time()
            self.draw()
            #print('Draw time', time() - t)

