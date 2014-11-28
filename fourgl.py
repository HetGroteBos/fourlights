from OpenGL.GLUT import *
from OpenGL.GL import *

class FourGL(object):

    def __init__(self, fourlights, glob):
        self.fl = fourlights
        self.g = glob

    def run(self):

        self.hoi = 0
        self.frames = 0

        # Setup remaining callbacks and start the program
        glutReshapeFunc( ( lambda s: lambda w, h: reshape(s, w, h) )(self))

        glutKeyboardFunc( ( lambda s: lambda c, x, y: keyboard(s, c, x, y) )(self))

        glutIdleFunc( ( lambda s: lambda: idle(s) )(self))

        #glClearColor(0.2, 0.4, 0.8, 1.0)
        glutDisplayFunc( ( lambda x: lambda: render(x) )(self))

        glutMainLoop()

def idle(self):
    try:
        self.fl.next()
        self.hoi += 1
        self.frames += 1
        if self.hoi > 10 or False:
            self.hoi = 0
            glutPostRedisplay()
        self.idle()

    # Oh no... wtfbbq
    except KeyboardInterrupt as _:
        print('Good-fucking-bye.')
        import sys
        sys.exit(1)

# Window size changed
def reshape(self, width, height):
    self.glob_w, self.glob_h = width, height
    glViewport(0, 0, width, height)

# Handle keyboard input
def keyboard(self, c, x, y):
    if c == 's':
        self.g.scroll_spectre = not self.g.scroll_spectre

    if c == 'l':
        self.g.logarithmic_spectre = not self.g.logarithmic_spectre

    if c == 'L':
        self.g.volume_spectre = not self.g.volume_spectre

    if c == 'f':
        self.g.ffft = not self.g.ffft
        if self.g.ffft:
            print "Now using one FFT"
        else:
            print "Now using two FFTs"

def render(self):
    self.draw()
