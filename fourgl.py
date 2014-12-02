from OpenGL.GLUT import *
from OpenGL.GL import *

class FourGL(object):

    def __init__(self, fourlights):
        self.fl = fourlights

        self.volume_spectre = False
        self.logarithmic_spectre = False
        self.scroll_spectre = False

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
        self.scroll_spectre = not self.scroll_spectre

    if c == 'l':
        self.logarithmic_spectre = not self.logarithmic_spectre

    if c == 'L':
        self.volume_spectre = not self.volume_spectre

    if c == 'f':
        self.fl.ffft = not self.fl.ffft
        if self.fl.ffft:
            print "Now using one FFT"
        else:
            print "Now using two FFTs"

def render(self):
    self.draw()
