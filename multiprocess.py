"""
Simple example with multi-threading.

Abstract:
Let's assume we have multiple big tasks that will consume a lot of time.
We will use multi-processing approach to increase performance.

We will create multiple workers that will process jobs from queue.
Finally all results will be stored resulting dictionary.

Logs from processes will be
"""
from multiprocessing import Manager

from utils import log
from worker import create_workers, start_workers, start_compute, stop_workers


if __name__ == '__main__':
    manager = Manager()
    sources = manager.Queue()
    results = manager.dict()

    workers = create_workers(2, manager)

    start_workers(sources, results, workers)

    for i in range(1, 100, 10):
        sources.put(i)

    start_compute(workers)

    sources.join()

    log(results)

    stop_workers(workers)
