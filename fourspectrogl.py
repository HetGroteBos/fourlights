from fourgl import FourGL

import numpy as np

from OpenGL.GLUT import *
from OpenGL.GL import *

class FourSpectroGL(FourGL):
    def __init__(self, fourlights, glob, spectro_length=2048, shader=True):
        FourGL.__init__(self, fourlights, glob)

        self.shader = shader

        glutInit()

        self.fl = fourlights
        self.spectrogram_length = spectro_length

        # Setup OpenGL Window
        glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE)
        self.win = glutCreateWindow('Fourlights')

        self.spectrogram = glGenTextures(1)
        self.frame_counter = 0

        glBindTexture(GL_TEXTURE_2D, self.spectrogram)

        # Tightly packed data
        glPixelStorei(GL_PACK_ALIGNMENT, 1)
        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)

        # Compile shader for visualisation support
        if self.shader:
            self.spectre_shader, self.spectre_prog = build_frag_prog('spectre.frag')
            glUseProgram(self.spectre_prog)
            self.log_uniform = \
                glGetUniformLocation(self.spectre_prog, 'logarithmic')
            self.volume_uniform = \
                glGetUniformLocation(self.spectre_prog, 'volume')
            glUniform1f(self.log_uniform, -1.0)
            glUniform1f(self.volume_uniform, -1.0)

        # Clear texture (black)
        texdata = np.zeros((self.spectrogram_length, self.fl.window / 2, 3), dtype=np.byte)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB8, self.spectrogram_length, self.fl.window / 2,
            0, GL_RGB, GL_UNSIGNED_BYTE, texdata)

        # Simple interpolation and repeat
        #glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        #glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

        # Finally enable texture visiblity
        glEnable(GL_TEXTURE_2D)

    def draw(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        #glOrtho(-1.0, -.8, -1.0, 1.0, -1.0, 1.0)
        glMatrixMode(GL_MODELVIEW)

        glClear(GL_COLOR_BUFFER_BIT)

        if self.scroll_spectre:
            base = self.frame_counter / float(self.spectrogram_length)
        else:
            base = 0.0

        clamp = 0.0
        if False:
            clamp = 0.5

        if self.shader:
            if self.logarithmic_spectre:
                glUniform1f(self.log_uniform, 1.0)
            else:
                glUniform1f(self.log_uniform, -1.0)

            if self.volume_spectre:
                glUniform1f(self.volume_uniform, 1.0)
            else:
                glUniform1f(self.volume_uniform, -1.0)

        glBegin(GL_QUADS)
        glTexCoord(base + 0.0, 1.0 - clamp)
        glVertex(-1,  1)

        glTexCoord(base + 0.0, 0.0)
        glVertex(-1, -1)

        glTexCoord(base + 1.0, 0.0)
        glVertex( 1, -1)

        glTexCoord(base + 1.0, 1.0 - clamp)
        glVertex( 1,  1)
        glEnd()

        glutSwapBuffers()

    def idle(self):
        frl = np.reshape(np.array(np.minimum(self.fl.freql[:self.fl.window / 2] * 255 * 1, 255), dtype=np.ubyte), (-1, 1))
        frr = np.reshape(np.array(np.minimum(self.fl.freqr[:self.fl.window / 2] * 255 * 1, 255), dtype=np.ubyte), (-1, 1))
        texdata = np.hstack((frl, frr, frr / 2 + frl / 2))

        #print texdata[1:5]
        glTexSubImage2D(GL_TEXTURE_2D, 0, self.frame_counter, 0, 1, self.fl.window / 2,
            GL_RGB, GL_UNSIGNED_BYTE, texdata)

        self.frame_counter = (self.frame_counter + 1) % self.spectrogram_length

# helper function for compiling GLSL shaders
def build_frag_prog(filename):
    frag_shader = glCreateShader(GL_FRAGMENT_SHADER)
    #print open('frag.frag').read().split('\n')
    glShaderSource(frag_shader, open(filename).read().split('\n'))
    glCompileShader(frag_shader)

    if glGetShaderiv(frag_shader, GL_COMPILE_STATUS) != GL_TRUE:
        print "Compiling fragment shader '%s' failed" % filename
        print glGetShaderInfoLog(frag_shader)
        sys.exit(1)

    # Build GPU program
    frag_prog = glCreateProgram()
    err = glAttachShader(frag_prog, frag_shader)
    glLinkProgram(frag_prog)

    if glGetProgramiv(frag_prog, GL_LINK_STATUS) != GL_TRUE:
        print "Linking fragment program '%s' failed" % filename

    return frag_shader, frag_prog


