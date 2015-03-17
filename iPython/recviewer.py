# Experimental record viewer, recalculates the waterfall

import numpy as np
import Queue as queue
import threading
import scipy.io.wavfile
import sys
import os.path
import math

def waterfallize(signal, bins):
    window = 0.5 * (1.0 - np.cos((2 * math.pi * np.arange(bins)) / bins))
    segment = bins / 2
    nsegments = int(len(signal) / segment)
    m = np.repeat(np.reshape(signal[0:segment * nsegments], (nsegments, segment)), 2, axis=0)
    t = np.reshape(m[1:len(m) - 1], (nsegments - 1, bins))
    img = np.multiply(t, window)
    wf = np.log(np.abs(np.fft.fft(img)))
    return np.concatenate((wf[:, bins / 2:bins], wf[:, 0:bins / 2]), axis=1)

'''class RecordViewer():
    def __init__(self, signal, sample_rate=None):
        if sample_rate is not None:
            # TODO: cutting off trailing frames in waterfallize
            #       probably causes time axis to be a bit off
            duration = float(len(signal)) / sample_rate
            self.layers.append(PlotAxes(self, static_axis(UNIT_HZ, sample_rate / 2,
                                                          cutoff=(-1.0, 1.0)),
                                        static_axis(UNIT_SEC, -duration, offset=duration)))
        self.signal = signal
        self.bins = None
        self.texture = None
        self.new_data = None
        self.update_texture()


    def update_texture(self):
        bins = int(int(np.sqrt(len(self.signal) / self.view.scale_y * self.view.scale_x)) / 16) * 16
        bins = min(max(bins, 16), glGetIntegerv(GL_MAX_TEXTURE_SIZE))

        if bins == self.bins:
            return

        def texture_work(self, bins):
            waterfall = waterfallize(self.signal, bins)
            waterfall[np.isneginf(waterfall)] = np.nan
            wmin, wmax = np.nanmin(waterfall), np.nanmax(waterfall)
            waterfall = ((waterfall - wmin) / (wmax - wmin)) * 5.5 - 4.5
            self.new_data = ext.mag2col(waterfall.astype('f'))
            self.new_data_event.set()

        self.worker.set_work(texture_work, (self, bins))
'''

def read_file(filename):
    ext = os.path.splitext(filename)[1]

    if ext == ".wav":
        import scipy.io.wavfile

        (sample_rate, audio) = scipy.io.wavfile.read(filename)
        return (sample_rate, audio[:,0] + 1j * audio[:,1])
    elif ext == ".fits":
        import pyfits
        img = pyfits.open(filename)[0]

        if int(img.header["NAXIS"]) != 2:
            raise Exception("expecting a two dimensional image")

        size = [img.header["NAXIS%d" % (i,)] for i in [1, 2]]

        if size[0] % 2 != 0:
            raise Exception("width %d is not a multiple of 2" % (size[0],))

        flat_data = np.ravel(img.data)
        return (48000, flat_data[0::2] + 1j * flat_data[1::2])
    else:
        raise Exception("unknown filename extension: %s" % (ext,))


