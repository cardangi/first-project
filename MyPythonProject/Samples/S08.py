# -*- coding: ISO-8859-1 -*-
from contextlib import ContextDecorator

__author__ = 'Xavier ROSSET'


class MyClass(ContextDecorator):

    def __enter__(self):
        print("Starting")
        try:
            print("A")
            raise ValueError("Exception!")
        except ValueError as e:
            print(e)

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("Stopping")
        print(exc_type, exc_val, exc_tb)


# @MyClass()
# def myfunc(s):
#     print(s)
# myfunc("Running")
with MyClass():
    print("Running")
