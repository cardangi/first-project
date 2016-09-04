# -*- coding: ISO-8859-1 -*-

__author__ = 'Xavier ROSSET'


class MyClass(object):

    def __call__(self):
        self._index += 1
        return self._seq[self._index - 1][2:6]
    
    def __iter__(self):
        return self

    def __next__(self):
        if self._index2 == len(self._seq):
            raise StopIteration
        self._index2 += 1
        return self._seq[self._index2 - 1][2:6]
            
    def __init__(self, seq):

        def f1(s):
            return int(s.split(".")[0])

        def f2(s):
            return int(s.split(".")[1])

        self._index = 0
        self._index2 = 0
        self._seq = sorted(sorted(seq, key=f1), key=f2)
        

x = MyClass(["2.20160125.13", "2.20160201.13", "2.20160120.13", "1.20160625.13", "2.20160422.13", "1.20160422.13", "2.19841102.13", "2.19990822.13", "2.20021014.13", "2.20000823.13", "2.20170101.13"])
print(list(x))
print(list(iter(x, "2016")))
