from pconv.abstr_saver import BWriter
import tensorflow as tf

# classe per la scrittura del tfrecord
class TFRWriter(BWriter):

    def __init__(self, write_path):
        self.writer = tf.python_io.TFRecordWriter(write_path + '.tfrecord')

    def write_instance(self, item):
        self.writer.write(item)

    def close_conn(self):
        self.writer.close()
