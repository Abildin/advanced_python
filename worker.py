from enum import IntEnum
from multiprocessing import Process
import time

from utils import log


class STATUS(IntEnum):
    CREATED = 0
    PENDING = 1
    STARTED = 2
    STOPPED = 3
    CLOSED = 4


class Worker(Process):
    def __init__(self, status):
        super().__init__()

        self.sources = None
        self.results = None
        self.epsilon = None
        self.status = status

    def start_worker(self, sources, results, epsilon):
        log(f'Starting worker {self.name}')
        self.sources = sources
        self.results = results
        self.epsilon = epsilon
        self.start()

    def start_compute(self):
        log(f'Starting compute {self.name}')
        self.status.set(STATUS.STARTED)

    def stop(self):
        log(f'Stopping compute {self.name}')
        self.status.set(STATUS.STOPPED)

    def run(self):
        log('Worker started')

        self.status.set(STATUS.PENDING)

        while True:
            status = self.status.get()

            if status == STATUS.PENDING:
                self.wait_for_starting()
            elif status == STATUS.STARTED:
                self.process_task()
            elif status == STATUS.STOPPED:
                self.status.set(STATUS.CLOSED)
            elif status == STATUS.CLOSED:
                break

        log('Worker stopped')

    def wait_for_starting(self):
        log(f'Status: PENDING')

        time.sleep(0.1)

        log(f'Status: STARTED')

    def process_task(self):
        if self.sources.empty():
            time.sleep(0.1)
            return

        source = self.sources.get()

        if source not in self.results:
            log('Compute started')
            self.results[source] = self.sqrt(source)
            log('Compute finished')

        log(f'{source}: {self.results[source]}')

        self.sources.task_done()

    def sqrt(self, source):
        if source == 1:
            return 1

        low = 0
        high = source / 2
        target = (high - low) / 2 + low
        square = target * target

        while abs(source - square) > self.epsilon:
            if square < source:
                low = target
            else:
                high = target

            target = (high - low) / 2 + low
            square = target * target

        return target


def create_workers(count, manager):
    workers = []

    for _ in range(count):
        status = manager.Value('d', STATUS.CREATED)
        worker = Worker(status=status)

        workers.append(worker)

    return workers


def start_workers(sources, results, workers, epsilon=0.00001):
    log('Starting workers')

    for worker in workers:
        worker.start_worker(sources, results, epsilon)

    for worker in workers:
        while worker.status.get() != STATUS.PENDING:
            time.sleep(0.1)

    log('Workers started')


def start_compute(workers):
    log('Starting compute')

    for worker in workers:
        worker.start_compute()

    log('Compute started')


def stop_workers(workers):
    log('Stopping workers')

    for worker in workers:
        worker.stop()

    for worker in workers:
        while worker.status.get() != STATUS.CLOSED:
            time.sleep(0.1)

    log('Workers stopped')
