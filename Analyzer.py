"""Analyzer implements a neural network as a handwritten digit classifier.
It requires a pre-trained, external weights file which contains the weights
and biases in an ordered dictionary. 'analyze_writing' is the method that
will take in 'writing' sample and return the digit written as a char.
"""


import numpy as np
import cPickle as cp
from scipy.ndimage.measurements import center_of_mass as CoM
from scipy.misc import imresize as Resize

class Analyzer(object):

    def __init__(self, param_file):
        self.params = cp.load(open(param_file))

    # We crop the data to align with the center of mass and match the size
    def crop_CoM(self, _in):
        ym, xm = _in.shape
        yc, xc = CoM(_in) # Scipy center of mass

        #Bounding box
        aw = np.argwhere(_in)
        (y0, x0), (y1, x1) = aw.min(0), aw.max(0) + 1 
        dim = int(max(abs(y0 - yc), y1 - yc, abs(x0 - xc), x1 - xc))

        #A square with dimensions determined by our bounding box, centered
        #at the CoM might stretch over the boundary, so we pad if necessary.
        padding = int(max(abs(min(xc - dim, yc - dim, 0)),
                    max(xc + dim - xm, yc + dim - ym, 0)))
        _tmp = np.lib.pad(_in, padding, 'constant')

        return _tmp[yc-dim+padding:yc+dim, xc-dim:xc+dim+padding]

    # Feed forward through our neural net
    def predict(self, _in):
        for layer in self.params:
            _in = np.dot(_in, self.params[layer]['w']) + self.params[layer]['b']
            if layer == 'Out':
                return np.argmax(_in)
            else:
                _in = np.maximum(_in, 0)

    # Method to be called externally
    def analyze_writing(self, matrix):
        cropped = self.crop_CoM(matrix)
        rs = Resize(cropped, (24, 24))
        val = self.predict(rs.reshape(-1))
        return str(val)
