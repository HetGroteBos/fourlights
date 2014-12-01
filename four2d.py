import pygame
import pygame.surfarray
#from pygame.locals import *

import numpy as np

from time import time

class Four2D(object):

    def __init__(self, fourlights, glob):
        self.fl = fourlights
        self.g = glob

        self.w = 1920 # 1920 / 2
        self.h = 512

        self.screen = pygame.display.set_mode((self.w, self.h), 0, 32)

        surface = pygame.display.get_surface()

        self.pixels = pygame.surfarray.pixels2d(surface)

        self.curr = 0

        self.logarithmic = False

        pygame.init()

    def draw(self):
        left = self.fl.freql[:self.fl.window / 2][::-1] * 255
        right = self.fl.freqr[:self.fl.window / 2][::-1] * 255


        # TODO: Optimise this
        if self.logarithmic:
            # 0.90 is bad, but we don't want to go beyond the fourier index ...
            # TODO
            newpixelindex = np.log2(np.linspace(0., 0.90, self.h) * 32 + 1.0) / 5.

            # Scale up to self.fl.window / 2
            newpixelindex *= self.fl.window / 2
            newpixelindex = newpixelindex.astype(int)

            lvals = left[newpixelindex]
            rvals = right[newpixelindex]

            r = rvals.astype(np.int) << 16
            g = lvals.astype(np.int) << 8
            b = ((lvals + rvals) / 2).astype(np.int)

            b = b | b << 8 | b << 16

            self.pixels[self.curr,:] = r | g | b

            #self.pixels[self.curr,:] = left[newpixelindex]

        # If not logarithmic view, apply trim & colouring
        else:
            trim = (self.fl.window / 2) / self.h
            if trim != 1:
                left = (left[::trim] + left[1::trim]) / trim
                right = (right[::trim] + right[1::trim]) / trim

            r = right.astype(np.int) << 16
            g = left.astype(np.int) << 8
            b = ((left + right) / 2).astype(np.int)

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

            #t = time()
            self.fl.next()
            #print('FL time', time() - t)

            #t = time()
            self.draw()
            #print('Draw time', time() - t)

