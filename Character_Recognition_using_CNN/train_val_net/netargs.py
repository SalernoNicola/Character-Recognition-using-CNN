import argparse


def parser_creator():
    parser = argparse.ArgumentParser(description="Train and validate a MoNet")
    parser.add_argument('-t', '--train',
                        help='specify tfrecord used for training',
                        required=True, type=str)
    parser.add_argument('-e', '--test',
                        help='specify tfrecord used for testing',
                        required=True, type=str)
    parser.add_argument('-s', '--save_to',
                        help='specify the name of the file in which the model will be saved',
                        required=True, type=str)
    parser.add_argument('-l', '--learning_rate',
                        help='specify the learning rate used for ADAM',
                        required=True, type=float)
    parser.add_argument('-o', '--num_epochs',
                        help='specify number of epochs',
                        required=True, type=int)
    parser.add_argument('-c', '--num_classes',
                        help='specify number of classes',
                        required=True, type=int)
    parser.add_argument('-b', '--batch_size',
                        help='specify the batch_size',
                        required=True, type=int)
    parser.add_argument('-r', '--reshape_to',
                        help='specify in which size the images will be reshaped',
                        required=True, type=int)

    return parser.parse_args()
