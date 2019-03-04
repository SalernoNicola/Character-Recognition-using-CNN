# import the necessary packages
import tensorflow as tf
import time
from keras.utils import np_utils
import numpy as np
import cv2
import random
import math

# import win_unicode_console

# win_unicode_console.enable()


class TFRecReader:

    # inizializzazione
    def __init__(self, tfrecord: str, batchsize: int, num_classes: int, verbose:bool, size):
        self.tfrecord = tfrecord
        self.batchsize = batchsize
        self.num_classes = num_classes
        self.verbose = verbose
        self.size = size
        (self.list_shuffled, self.length_data, self.niteration) = self.__read_tfrecord()

    def __read_tfrecord(self):
        data = []
        if self.verbose:
            print("inizio lettura file: {0}, Ore: {1} ".format(self.tfrecord ,time.strftime("%H:%M:%S")))
        for example in tf.python_io.tf_record_iterator(self.tfrecord):
            result = tf.train.Example.FromString(example)
            l = result.features.feature['label'].int64_list.value[0]
            im = result.features.feature['image_bin'].bytes_list.value[0]
            sh = result.features.feature['shape'].bytes_list.value[0]
            data.append({'label': l, 'image_bin': im,'shape': sh})
        if self.verbose:
            print("Fine lettura file: {0}, Ore: {1} ".format(self.tfrecord, time.strftime("%H:%M:%S")))

        ld = len(data)
        ls = random.sample(data, ld)
        niter = int(math.ceil(ld/self.batchsize))
        
        return ls, ld, niter
        
    def get_next_batch(self):
        while 1:
            for j in range(self.niteration):
                shuffled_batch = self.list_shuffled[self.batchsize * j: ((j + 1) * self.batchsize)]
                images = []
                labels = []
                for vl in shuffled_batch:
                    images.append(self.image_to_feature_vector(vl['image_bin']))
                    labels.append(vl['label'])
                yield np.array(images), np_utils.to_categorical(labels, self.num_classes)
    
    def image_to_feature_vector(self, image):
        image_from_buffer = np.frombuffer(image, np.uint8)
        decoded_image = cv2.imdecode(image_from_buffer, cv2.COLOR_BGR2BGR555)
        return self.resize_image(decoded_image)/255.0

    def resize_image(self, image):
        # resize the image to a fixed size, then flatten the image into
        #  a list of raw pixel intensities
        return cv2.resize(image, self.size)