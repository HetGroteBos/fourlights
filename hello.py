# The game of life implemented in OpenGL/GLSL

import numpy as np
import time
from math import pi

from OpenGL.GLUT import *
from OpenGL.GL import *

RESOLUTION=128

glutInit()

# Setup OpenGL Window
glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE)
win = glutCreateWindow('Fourier')

freq = np.linspace(0.2, 0.8, RESOLUTION)
doge = np.cos(np.linspace(0.0, (float(RESOLUTION - 1) / RESOLUTION) * 2 * pi, RESOLUTION))

# Window size changed
def reshape(width, height):
    global glob_w, glob_h
    glob_w, glob_h = width, height
    glViewport(0, 0, width, height)

def render():
    glClear(GL_COLOR_BUFFER_BIT)

    glBegin(GL_QUADS)

    for i in xrange(RESOLUTION):
        p = float(i) / RESOLUTION
        r = (1.0 / RESOLUTION) * 1.9 

        x = p * 2 - 1
        glColor(p, 0, 1 - p)
        glVertex(x, freq[i] * 2 - 1)
        glVertex(x, -1)
        glVertex(x + r, -1)
        glVertex(x + r, freq[i] * 2 - 1)

    glEnd()

    glutSwapBuffers()

counter = 0.0
CINC = 0.02

def idle(once = [True]):
    global freq
    global doge
    global counter

    time.sleep(0.1)

    counter += CINC
    counter %= 1.0

    #freq = np.random.random((RESOLUTION,))
    ifr = np.fft.fft(doge)
    if (once[0]):
        once[0] = False
        print ifr
    freq = np.abs(ifr)
    freq /= np.max(freq)
    ival = lambda x: x * pi
    lfo = np.cos(np.linspace(ival(counter), ival(counter + CINC), RESOLUTION))
    doge = np.cos(np.linspace(0.0, (float(RESOLUTION - 1) / RESOLUTION) * RESOLUTION * pi, RESOLUTION) * lfo)
    glutPostRedisplay()
    pass

# Handle keyboard input
def keyboard(c, x, y):
    pass

# Setup remaining callbacks and start the program
glutReshapeFunc(reshape)
glutKeyboardFunc(keyboard)
glutIdleFunc(idle)

#glClearColor(0.2, 0.4, 0.8, 1.0)
glutDisplayFunc(render)

glutMainLoop()

