import multiprocessing as mp

# inizializzo i vari task  per ogni processo della macchina
class PoolCore(mp.Process):
    def __init__(self, tasks, results):
        mp.Process.__init__(self)
        self.tasks = tasks
        self.results = results

    def run(self):
        while True:
            new_task = self.tasks.get()
            if new_task is None:
                self.tasks.task_done()
                break
            ans = new_task()
            self.tasks.task_done()
            self.results.put(ans)

# converte le righe per il tfrecord
class BatchConverter:
    def __init__(self, batch, func):
        self.batch = batch # batch = part_ds, che sono le parti del dataset splittato
        self.conv_func = func # func = turn_to, è la struttura delle row del tfrecord

    def __call__(self):
        return [self.conv_func(row) for row in self.batch]
