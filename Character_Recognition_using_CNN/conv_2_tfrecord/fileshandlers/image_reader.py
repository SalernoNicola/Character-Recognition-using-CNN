import cv2 as cv
import numpy as np


class ImageReader:

    def __init__(self, label, path):
        self.label = label
        self.shape = np.asarray(np.asarray(cv.imread(path), np.uint8).shape, np.int32).tobytes()
        f = open(path, 'rb')
        self.image = f.read()
        f.close()
