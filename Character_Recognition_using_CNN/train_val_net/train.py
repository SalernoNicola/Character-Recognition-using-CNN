import time
from keras.models import Sequential
from keras.layers import LeakyReLU, Conv2D, Dropout, MaxPooling2D
from keras.optimizers import Adam
from keras.layers.core import Dense, Flatten
import netargs
import matplotlib.pyplot as plt
from loader.shuffle_class import TFRecReader
# decommentare su windows
# import win_unicode_console

# decommentare su windows
# win_unicode_console.enable()

"""
quando si esegue questo script, specificare i seguenti argomenti (se no non parte): 
--train=/path/to/train.tfrecord --test=/path/to/test.tfrecord --save_to=/path/to/model 
--learning_rate=0.0001 --num_epochs=25 --num_classes=26 --batch_size=16 --reshape_to=32 
[questi ultimi sono i parametri utilizzati per l'ultimo allenamento effettuato]
"""


# il modello viene costruito qui
def build_model(num_classes, input_shape):
    model = Sequential()

    model.add(Conv2D(128, (5, 5), input_shape=input_shape))
    model.add(LeakyReLU(alpha=0.1))

    model.add(MaxPooling2D(pool_size=(4, 4)))

    model.add(Conv2D(256, (3, 3)))
    model.add(LeakyReLU(alpha=0.1))

    model.add(MaxPooling2D(pool_size=(2, 2)))

    model.add(Flatten())

    model.add(Dense(256))
    model.add(LeakyReLU(alpha=0.1))

    model.add(Dropout(0.5))

    model.add(Dense(512))
    model.add(LeakyReLU(alpha=0.1))

    model.add(Dropout(0.25))

    model.add(Dense(num_classes, activation='softmax'))

    return model


def make_plots(hst):
    print(hst.history.keys())
    #  plot accuracy e loss
    plt.plot(hst.history['acc'])
    plt.plot(hst.history['loss'])
    plt.title('model accuracy')
    plt.ylabel('accuracy')
    plt.xlabel('epoch')
    plt.legend(['train', 'validation'], loc='upper left')
    plt.show()


def run_yoko(args):
    tf_size = (args.reshape_to, args.reshape_to)
    channels = 3

    train_tf = TFRecReader(tfrecord=args.train, batchsize=args.batch_size,
                           num_classes=args.num_classes, verbose=True, size=tf_size)
    test_tf = TFRecReader(tfrecord=args.test, batchsize=args.batch_size,
                          num_classes=args.num_classes, verbose=True, size=tf_size)

    model = build_model(num_classes=args.num_classes,
                        input_shape=(args.reshape_to, args.reshape_to, channels))
    model.summary()

    # alleno il modello usando ADAM come optimizer
    print("[INFO] compiling model...")
    adam = Adam(lr=args.learning_rate)

    model.compile(loss="categorical_crossentropy", optimizer=adam, metrics=["accuracy"])

    print("Inizio training: ", time.strftime("%H:%M:%S"))

    history = model.fit_generator(train_tf.get_next_batch(), steps_per_epoch=train_tf.length_data,
                                  epochs=args.num_epochs)

    print("Fine training: ", time.strftime("%H:%M:%S"))

    # plot di accuratezza e loss
    make_plots(history)

    # Validation
    print("Inizio validation: ", time.strftime("%H:%M:%S"))
    print("[INFO] evaluating on testing set...")
    scores = model.evaluate_generator(test_tf.get_next_batch(), test_tf.length_data, verbose=1)
    print("[INFO] accuracy: {:.4f}%".format(scores[1] * 100))
    print("Fine validation: ", time.strftime("%H:%M:%S"))

    model.save(args.save_to + '.h5')


if __name__ == '__main__':
    run_yoko(netargs.parser_creator())
