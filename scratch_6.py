# god this is so stupid

import sys


class Foo:
    def __init__(self):
        print("Hello")

    @classmethod
    def method(cls):
        print("Hi")


def call(func):
    func()


stmt = call(getattr(getattr(sys.modules[__name__], "Foo"), "method"))

from timeit import timeit

print(timeit(lambda: stmt))
