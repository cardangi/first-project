# -*- coding: ISO-8859-1 -*-
from math import pow

__author__ = 'Xavier ROSSET'


class Sequence(object):

    def __init__(self, firstterm, terms):
        self.firstterm = firstterm
        self._terms = terms


class ArithmeticSequence(Sequence):

    def __init__(self, firstterm=1, difference=1, terms=10):
        super(ArithmeticSequence, self).__init__(firstterm, terms)
        self.difference = difference

    def sequence(self):
        for i in range(self.firstterm, self.firstterm + (self.difference*self.terms), self.difference):
            yield i

    def series(self):
        for i in self.sequence(self.firstterm, self.difference, self.terms):
            series = ((self.firstterm + i)/2)*self.terms
        return series

    @property
    def terms(self):
        return self._terms

    @terms.setter
    def terms(self, value):
        if value > 9999:
            raise ValueError("Terms above 9999 are not possible due to system limitation.")
        self._terms = value


class GeometricSequence(Sequence):

    def __init__(self, firstterm=1, ratio=2, terms=10):
        super(GeometricSequence, self).__init__(firstterm, terms)
        self._ratio = ratio

    def sequence(self):
        for term in [self.firstterm*pow(self.ratio, i) for i in range(self.terms)]:
            yield term

    def series(self):
        return self.firstterm*((pow(self.ratio, self.terms) - 1)/(self.ratio - 1))

    @property
    def terms(self):
        return self._terms

    @terms.setter
    def terms(self, value):
        if value > 1499:
            raise ValueError("Terms above 1499 are not possible due to system limitation.")
        self._terms = value

    @property
    def ratio(self):
        return self.ratio

    @ratio.setter
    def ratio(self, value):
        if value > 100:
            raise ValueError("Ratio above 100 is not possible due to system limitation.")
        self.ratio = value
