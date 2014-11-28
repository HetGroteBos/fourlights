from fourgl import FourGL

import numpy as np

from OpenGL.GLUT import *
from OpenGL.GL import *

class FourBarGL(FourGL):
    def __init__(self, fourlights, glob):
        FourGL.__init__(self, fourlights, glob)

        glutInit()

        self.fl = fourlights

        # Setup OpenGL Window
        glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE)
        self.win = glutCreateWindow('Fourlights')

        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_COLOR_ARRAY)

        self.create_vertices()

    def freq_to_fourier(self, hz):
        return int(self.fl.window * hz / self.fl.samplerate)

    def create_vertices(self):
        cols = []
        self.vertices = []
        for i in xrange(self.fl.window):
            p = float(i) / self.fl.window
            r = (1.0 / self.fl.window) * 1.9
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
                x = (float(self.freq_to_fourier(freq) + .5) / self.fl.window) * 2 - 1
                hs = 1.0 / self.fl.window 
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
        glDrawArrays(GL_QUADS, 0, self.fl.window * 4)

        glColorPointer(3, GL_FLOAT, 0, self.pointer_cols)
        glVertexPointer(2, GL_FLOAT, 0, self.pointer_verts)
        glDrawArrays(GL_TRIANGLES, 0, len(self.fl.lights) * 3 * 3)

        glutSwapBuffers()

    def idle(self):
        pass
