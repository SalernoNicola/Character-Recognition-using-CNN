import multiprocessing as mp
from pconv.pool import PoolCore, BatchConverter
from itertools import *
from pconv.abstr_saver import BWriter


class TfrConverter:
    MIN_PROC = 1
    MIN_ELS_DS = 1
    BASE_DIR = "."

    def __init__(self, dataset, turn_to, num_proc=1):
        # controllo se il numero dei processi sia maggiore di 0
        if num_proc < self.MIN_PROC:
            raise ValueError("you should specify at least " + str(self.MIN_PROC) + " processes")
        # controllo se il dataset è vuoto
        if len(dataset) < self.MIN_ELS_DS:
            raise ValueError("dataset is empty")

        self.num_proc = num_proc
        self.part_ds = self.__split_ds(dataset, num_proc) #salvo le parti del dataset splittato in base ai processi
        print(len(self.part_ds))
        self.turn_to = turn_to

    # return la lunghezza del batch presa dal dataset splittato per i processi assegnati
    def ds_size(self):
        return [len(batch) for batch in self.part_ds]

    # metodo utilizzato per la scrittura e il salvataggio del  file tfrecord
    def save(self, saver):
        if not isinstance(saver, BWriter):
            raise TypeError("saver should implement BWriter")
        i = 0
        for a in chain.from_iterable(self.__get_images()):
            saver.write_instance(a) # write_instance si occupa della scrittura degli item
            print(i)
            i = i + 1

    # mp = multi processing
    # creo le code dei processi
    def __get_images(self):
        tasks = mp.JoinableQueue()
        results = mp.Queue()
        cores = [PoolCore(tasks, results) for _ in range(self.num_proc)]

        for core in cores:
            core.start()

        for i in range(self.num_proc):
            tasks.put(BatchConverter(self.part_ds[i], self.turn_to))

        for _ in range(self.num_proc):
            tasks.put(None)

        tasks.join()

        for i in range(self.num_proc):
            yield results.get()

    # split_ds divide il dataset in base ai processi assegnati alla nostra macchina.
    # ds = dataset, split è il numero di processi assegnati.
    @staticmethod
    def __split_ds(ds, split):
        ds_split = []
        ds_size = len(ds)
        batch_size = ds_size // split
        remainder = ds_size % split
        acc = 0

        for i in range(split):
            chunk_size = batch_size + 1 if (i < remainder) else batch_size
            ds_split.append(ds[acc: acc + chunk_size])
            acc += chunk_size

        return ds_split
