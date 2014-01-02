
import wave
import numpy
import sys

x = wave.open(sys.argv[1])
y = numpy.memmap(x._data_chunk.file.file, dtype=numpy.int16, mode='r', offset=x._data_chunk.file.file.tell())
z = y.reshape((-1, 2))

