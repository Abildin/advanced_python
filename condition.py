"""
Simple example of usage of Conditions in threads.

Abstract:
Let's imagine we have service that downloads a lot of JSON files and process them.
We will have 2 types of workers.
1. JSON downloader - downloads JSON files
2. JSON processor - processes downloaded JSON files

As you understand we can't process JSON file if download didn't completed.
So JSON processor will wait until download will complete and only after that processes it.

If you will disable condition checking, processor will try to decode partially downloaded JSON file
and will raise JSONDecodeError.
"""
from enum import IntEnum
from queue import Queue
import json
from threading import Condition, Thread
import time


USE_CONDITION = True


class Buffer(object):
    """
    Buffer that stores JSON body and download status.
    """
    class STATUS(IntEnum):
        PENDING = 1
        COMPLETED = 2

    def __init__(self, source):
        self.buffer = []
        self.condition = Condition()
        self.status = self.STATUS.PENDING

        self.source = source

    def add(self, block):
        self.buffer.append(block)

    def completed(self):
        return self.status == self.STATUS.COMPLETED

    def complete(self):
        self.status = self.STATUS.COMPLETED

        with self.condition:
            self.condition.notify_all()

    def json(self):
        if not USE_CONDITION:
            return self.load_json()

        with self.condition:
            self.condition.wait_for(self.completed)

            return self.load_json()

    def load_json(self):
        text = ''.join(self.buffer)

        try:
            return json.loads(text)
        except json.decoder.JSONDecodeError:
            print(f"Could not decode: {text}")


class Downloader(Thread):
    def __init__(self, sources, buffers):
        super().__init__()

        self.sources = sources
        self.buffers = buffers

    @staticmethod
    def receive_block(source):
        for block in source:
            yield block

            time.sleep(0.1)

    def run(self):
        while not self.sources.empty():
            source = self.sources.get()
            print(f"Starting download: {source}")

            buffer = Buffer(source)
            self.buffers.put(buffer)

            for block in self.receive_block(source):
                buffer.add(block)

            buffer.complete()
            print(f"Download completed: {source}")


class Processor(Thread):
    class STATUS(IntEnum):
        PENDING = 1
        COMPLETED = 2

    def __init__(self, buffers):
        super().__init__()

        self.buffers = buffers
        self.status = self.STATUS.PENDING

    def run(self):
        while self.status != self.STATUS.COMPLETED:
            if self.buffers.empty():
                time.sleep(0.1)
                continue

            buffer = self.buffers.get()
            print(f"Accepted: {buffer.source}")

            data = buffer.json()
            print(f"Process completed: {data}")

            self.buffers.task_done()

    def complete(self):
        self.status = self.STATUS.COMPLETED


def start(sources_, use_condition=True):
    sources = Queue()
    buffers = Queue()

    for source in sources_:
        sources.put(source)

    global USE_CONDITION
    USE_CONDITION = use_condition

    processors = [
        Processor(buffers),
        Processor(buffers),
    ]

    for processor in processors:
        processor.start()

    downloaders = [
        Downloader(sources, buffers),
        Downloader(sources, buffers),
    ]

    for downloader in downloaders:
        downloader.start()

    buffers.join()

    for processor in processors:
        processor.complete()


if __name__ == '__main__':
    SOURCES = [
        '"FIRST COMPLETE JSON STRING"',
        '"SECOND COMPLETE JSON STRING"',
    ]

    start(SOURCES, use_condition=True)
