"""
Simple example of Timer usage in threads.

Abstract:
Pseudo async call decorator.
"""
from threading import Timer, Thread
import time


class async_call(object):
    def __init__(self, func):
        self.func = func

    def __call__(self, *args, **kwargs):
        self.func(*args, **kwargs)

    def _call(self, *args, interval=0, delay=0, repeat=1, **kwargs):
        while repeat != 0:
            Timer(interval, self.func, args, kwargs).start()

            if repeat > 0:
                repeat -= 1

            if repeat != 0:
                time.sleep(delay)

    def async_call(self, *args, **kwargs):
        Thread(target=self._call, args=args, kwargs=kwargs).start()


@async_call
def say_hi(name):
    print(f'Hi {name}!')


if __name__ == '__main__':
    say_hi.async_call('Alice', interval=2, delay=1, repeat=3)

    say_hi('Synco')
