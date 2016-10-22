# -*- coding: ISO-8859-1 -*-
from contextlib import ContextDecorator

__author__ = 'Xavier ROSSET'


class MyClass(ContextDecorator):

    def __enter__(self):
        print("Starting")

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("Stopping")


@MyClass()
def myfunc(s):
    print(s)


myfunc("Running")
with MyClass():
    print("Running")
