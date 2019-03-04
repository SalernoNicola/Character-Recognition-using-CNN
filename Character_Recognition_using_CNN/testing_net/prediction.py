import load.class_predict as predict

MODEL_PATH = 'C:\\Users\\paolo\\Desktop\\testRetiNeurali\\shape32classi62\\shuffle_62_epoche25.h5'
CSV_PATH = 'C:\\Users\\paolo\\Desktop\\testRetiNeurali\\index_62.csv'
PATH_NEW_CSV = 'C:\\Users\\paolo\\Desktop\\PredictionNuovoLearningRate62Classi.csv'
ROOT_DIR = 'C:\\Users\\paolo\\Desktop\\testRetiNeurali\\Img'
size = (32, 32)

# MODEL_PATH --> modello salvato dal training della rete
# CSV_PATH --> CSV contenente le etichette con le classi assegnate
# PATH_NEW_CSV --> path del nuovo CSV che verrà creato dalle predizioni
# ROOT_DIR -->  path della directory contente le immagini che ci serviranno per le predizioni

pre = predict.predizioni(CSV_PATH, PATH_NEW_CSV, MODEL_PATH, ROOT_DIR, size)

pre.writeCsv()