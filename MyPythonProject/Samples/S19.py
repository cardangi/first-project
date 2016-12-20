# -*- coding: utf-8 -*-

__author__ = "Xavier ROSSET"


class Attributes(object):

    def __init__(self, func):
        self.func = func
        self.name = func.__name__

    def __get__(self, instance, cls):
        return self.func(instance)

    def __set__(self, obj, value):
        for k, v in value.items():
        	setattr(obj, k, v)


class MyClass(object):

    def __init__(self, arg):
        self._index = 0
        self._inputs = arg

    def __iter__(self):
        return self

    def __next__(self):
        if self._index >= len(self._inputs):
            raise StopIteration
        if self._uid:
            raise StopIteration
        self._index += 1
        self._step += 1
        return self._inputs[self._index - 1]

    # attributes = Attributes(attributes)
    @Attributes
    def attributes(self, attr):
        return getattr(self, attr)


def interface(interface):
    for inp, dest in interface:
        while True:
            value = input("{0}. {1}: ".format(interface.step, inp))
            try:
                interface.attributes = {dest: value}
            except ValueError:
                continue
            break
    return interface


if __name__ == "__main__":
    gui = interface(MyClass([("Enter database to update", "database"), ("Singled or Ranged ", "type"), ("Enter interface(s) unique ID", "uid"), ("Enter ranged from interface unique ID", "from_uid"), ("Enter ranged to interface unique ID", "to_uid")]))
    print(gui.attributes("database"))
