import pygame
import pygame.surfarray
#from pygame.locals import *

import numpy as np

from time import time

class Four2D(object):

    def __init__(self, fourlights, glob):
        self.fl = fourlights
        self.g = glob

        self.w = 1920 / 2
        self.h = 1024

        self.screen = pygame.display.set_mode((self.w, self.h), 0, 32)

        surface = pygame.display.get_surface()

        self.pixels = pygame.surfarray.pixels2d(surface)

        self.curr = 0

        pygame.init()

    def draw(self):
        #frl = np.reshape(np.array(np.minimum(self.fl.freql[:self.fl.window / 2] * 255 * 1, 255), dtype=np.ubyte), (-1, 1))
        #frr = np.reshape(np.array(np.minimum(self.fl.freqr[:self.fl.window / 2] * 255 * 1, 255), dtype=np.ubyte), (-1, 1))

        left = self.fl.freql[:self.fl.window / 2][::-1] * 255
        right = self.fl.freqr[:self.fl.window / 2][::-1] * 255

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
        while not pygame.QUIT in [e.type for e in pygame.event.get()]:

            #t = time()
            self.fl.next()
            #print('FL time', time() - t)

            #t = time()
            self.draw()
            #print('Draw time', time() - t)

