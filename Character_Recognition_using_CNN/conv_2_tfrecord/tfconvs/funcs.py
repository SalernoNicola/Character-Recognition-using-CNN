import tensorflow as tf


def int64_feature(val):
    return tf.train.Feature(int64_list=tf.train.Int64List(value=val))


def bytes_feature(val):
    return tf.train.Feature(bytes_list=tf.train.BytesList(value=val))


def mt_features(feat):
    return tf.train.Features(feature=feat)


def mt_example(feature):
    return tf.train.Example(features=mt_features(feature))
