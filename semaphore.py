"""
Simple example of Semaphore usage in threads.

Abstract:
Pseudo event loop simulator.
"""
from enum import IntEnum
from queue import Queue
from threading import Semaphore, Thread
import time


class Worker(Thread):
    class STATUS(IntEnum):
        PENDING = 1
        RUNNING = 2
        STOPPED = 3

    def __init__(self, tasks, semaphore):
        super().__init__()
        self.status = self.STATUS.PENDING

        self.tasks = tasks
        self.semaphore = semaphore

    def stop(self):
        self.status = self.STATUS.STOPPED
        self.semaphore.release()

    def run(self):
        self.status = self.STATUS.RUNNING

        while self.status != self.STATUS.STOPPED:
            self.semaphore.acquire()

            if self.tasks.empty():
                continue

            runner, args, kwargs = self.tasks.get()
            runner(*args, **kwargs)

            self.tasks.task_done()
            time.sleep(1)


def start(tasks_):
    tasks = Queue()
    semaphore = Semaphore(len(tasks_))

    for task in tasks_:
        tasks.put(task)

    workers = [
        Worker(tasks, semaphore),
        Worker(tasks, semaphore),
    ]

    for worker in workers:
        worker.start()

    tasks.join()

    for worker in workers:
        worker.stop()


if __name__ == '__main__':
    TASKS = [
        (print, ('Hello', 'Alice'), {}),
        (print, ('Hello', 'Bob'), {}),
        (print, ('Hello', 'World!'), {}),
    ]

    start(TASKS)
