import argparse
# import os
from tfconvs.funcs import *
from fileshandlers.dir_explorer import DirectoryExplorer
from fileshandlers.image_reader import ImageReader
from pconv.tfr_converter import TfrConverter
from tfrecord_writer import TFRWriter
import csv

# specifica gli argomenti da riga di comando
def parser_creator():
    parser = argparse.ArgumentParser(description="This script is used to convert a dataset into tfrecord")
    parser.add_argument('-p', '--path',
                        help='insert the root directory of the dataset that you want to concert',
                        required=True, type=str)
    parser.add_argument('-w', '--write_path',
                        help='add the path in which you want to save the newly created tfrecord',
                        required=True, type=str)
    parser.add_argument('-n', '--num_proc',
                        help='process number to use [specify more than one only if your hd/sdd disk is good]', type=int)
    return parser.parse_args()

# ritorna il dataset di tuple e l'indice della classe assegnata
def convert_de_result(dexpl):
    dataset_to_tuple = []
    class_index = {}
    for i, d in enumerate(dexpl.dirs):
        files = dexpl.get_files_from(d)
        class_index[d] = i
        dataset_to_tuple += list(zip([i] * len(files), files))
    return dataset_to_tuple, class_index

# crea la struttura del tfr,
# per ogni entry converte in un oggetto che viene convertito in bytecode e poi sarà salvato in tfrecord
def to_tfr(x):
    image = ImageReader(x[0], x[1])
    print("reading from " + str(x[0]) + " image " + str(x[1]))
    return mt_example({
        'shape': bytes_feature([image.shape]),
        'image_bin': bytes_feature([image.image]),
        'label': int64_feature([image.label])
    }).SerializeToString()


# scrivo nel file CSV le classi con la lettera associata. Original indica il carattere e new la classe
# ci = è index della classe; p = il path dove andrà salvato il file.
def save_index(ci, p):
    with open(p + '_index.csv', 'w') as f:
        writer = csv.writer(f, delimiter=',')
        writer.writerow(['original', 'new'])
        writer.writerows(ci.items())

# --write_path aggiungi il percorso in cui vuoi salvare il file csv/tfrecord appena creato
# --path Questo script viene utilizzato per convertire un set di dati in tfrecord
# --num_proc numero dei processi da usare [specificarne più di uno solo se il disco hdd / ssd è buono]
def main():
    cmd_line_args = parser_creator()
    # zipped è il dataset di tuple
    zipped, class_container = convert_de_result(DirectoryExplorer(cmd_line_args.path))
    print('detected classes: %s\t total files: ' % len(class_container), len(zipped))
    save_index(class_container, cmd_line_args.write_path) # salvo il file csv
    tfr = TfrConverter(dataset=zipped, turn_to=to_tfr, num_proc=cmd_line_args.num_proc)
    saver = TFRWriter(cmd_line_args.write_path) # passo il percorso in cui voglio salvare il file
    tfr.save(saver)
    print("closing saver")
    saver.close_conn()


if __name__ == '__main__':
    main()
