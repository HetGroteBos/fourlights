# Fourier based light clavier.

import numpy as np
import time
from math import pi

from OpenGL.GLUT import *
from OpenGL.GL import *

from wavepy import z as wav

#RESOLUTION=256
RESOLUTION=1024
#RESOLUTION=4096
#RESOLUTION=32

glutInit()

# Setup OpenGL Window
glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE)
win = glutCreateWindow('Fourier')

freq = np.linspace(0.2, 0.8, RESOLUTION)
doge = np.cos(np.linspace(0.0, (float(RESOLUTION - 1) / RESOLUTION) * 2 * pi, RESOLUTION))

glEnableClientState(GL_VERTEX_ARRAY)
glEnableClientState(GL_COLOR_ARRAY)

def hoi():
    global vertices
    cols = []
    vertices = []
    for i in xrange(RESOLUTION):
        p = float(i) / RESOLUTION
        r = (1.0 / RESOLUTION) * 1.9 
        for _ in xrange(4):
            cols.append((p, 0, 1 - p))
        x = p * 2 - 1
        vertices.append((x, p * 2 - 1))
        vertices.append((x, -1))
        vertices.append((x + r, -1))
        vertices.append((x + r, p * 2 - 1))
    cols = np.array(cols, dtype=np.float)
    vertices = np.array(vertices, dtype=np.float)
    #glColorPointer(3, GL_FLOAT, 0, [0.,] * 9)
    glColorPointer(3, GL_FLOAT, 0, cols)
hoi()

# Window size changed
def reshape(width, height):
    global glob_w, glob_h
    glob_w, glob_h = width, height
    glViewport(0, 0, width, height)

def render():
    global vertices
    glClear(GL_COLOR_BUFFER_BIT)

    print vertices.shape
    vertices[::4, 1] = freq * 2 - 1
    vertices[3::4, 1] = freq * 2 - 1
    glVertexPointer(2, GL_FLOAT, 0, vertices)

    #glBegin(GL_QUADS)

    glDrawArrays(GL_QUADS, 0, RESOLUTION * 4)

    #for i in xrange(RESOLUTION):
    #    p = float(i) / RESOLUTION
    #    r = (1.0 / RESOLUTION) * 1.9 

    #    x = p * 2 - 1
    #    glColor(p, 0, 1 - p)
    #    glVertex(x, freq[i] * 2 - 1)
    #    glVertex(x, -1)
    #    glVertex(x + r, -1)
    #    glVertex(x + r, freq[i] * 2 - 1)

    #glEnd()

    glutSwapBuffers()

counter = 0.0
CINC = 0.02
sample = 0

def idle(once = [True]):
    global freq
    global doge
    global counter
    global sample

    time.sleep(0.02)

    #counter += CINC
    #counter %= 1.0

    sample += RESOLUTION

    #freq = np.random.random((RESOLUTION,))
    ifr = np.fft.fft(doge)
    if (once[0]):
        once[0] = False
        print ifr
    freq = np.abs(ifr)
    freq /= np.max(freq)
    #freq /= 64.0
    freq /= 4.0
    #ival = lambda x: x * pi
    #lfo = np.cos(np.linspace(ival(counter), ival(counter + CINC), RESOLUTION))
    #doge = np.cos(np.linspace(0.0, (float(RESOLUTION - 1) / RESOLUTION) * RESOLUTION * pi, RESOLUTION) * lfo)
    doge = wav[sample:sample + RESOLUTION, 0]
    #print sample * 10
    print sample
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

