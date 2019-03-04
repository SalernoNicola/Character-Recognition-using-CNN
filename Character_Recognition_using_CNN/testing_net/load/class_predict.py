from keras.models import load_model
import numpy as np
import cv2
import os
import csv

class predizioni:

    def __init__(self, CSV_PATH: str, PATH_NEW_CSV: str, MODEL_PATH: str, ROOT_DIR: str, size):

        self.CSV_PATH = CSV_PATH
        self.PATH_NEW_CSV = PATH_NEW_CSV
        self.MODEL_PATH = MODEL_PATH
        self.ROOT_DIR = ROOT_DIR
        self.size = size
        self.listPredict = {}

    #ritorna la lista formata dalla lettura delle righe del csv iniziale
    def getListPredict(self):
        with open(self.CSV_PATH, 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for row in reader:
                self.listPredict[row[1]] = row[0]
        return self.listPredict

    def writeCsv(self):
        model = load_model(self.MODEL_PATH)
        # apro il file csv in scrittura
        csv = open(self.PATH_NEW_CSV, "w")
        #intestazioni delle colonne che andranno scritte nel newCsv
        columnTitleRow = "LabelOriginale, LabelPredetta, ImageName\n"
        csv.write(columnTitleRow)

        # in rootDir viene impostata la directory da cui si inizierà la lettura delle sottodirectory conteneti le immagini
        # ogni sottodirectory contiene 55 elementi.
        # es: rootDir= img --> sottodirectory A, aa, B, bb, ecc
        rootDir = self.ROOT_DIR
        for dirName, subdirList, fileList in os.walk(rootDir):
            for label in subdirList:
                d = os.path.join(rootDir, label) #labet è l'etichetta della directory
                for i, filename in enumerate(os.listdir(d)):
                    if (not filename.startswith(".", 0, 1)):
                        f = os.path.join(d, filename)
                        img = np.array([self.read_image(f)])
                        accuracy = model.predict(img)[0]
                        prediction = accuracy.argmax(axis=0)
                        row = label + "," + self.getListPredict()[str(prediction)] + "," + filename + "\n"
                        # scrive la riga nel file csv
                        csv.write(row)

        print("Fine scrittura file CSV")

    # legge le immagine e applica un resize di 32x32
    def read_image(self, path):
        return cv2.resize(cv2.imread(path), self.size) / 255.0