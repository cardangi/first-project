# -*- coding: ISO-8859-1 -*-
from collections import deque

__author__ = 'Xavier ROSSET'


class ArithmeticSequence(object):

    def __init__(self, firstterm=1, difference=1, terms=10):
        if terms > 49999:
            raise ValueError("Terms above 49999 are not allowed due to system limitations.")
        if difference == 0:
            raise ValueError("Difference must be greater than 0.")
        self._difference = difference
        self._firstterm = firstterm
        self._terms = terms

    @property
    def sequence(self):
        for term in range(self._firstterm, self._firstterm + (self._difference*self._terms), self._difference):
            yield term

    @property
    def series(self):
        return ((self._firstterm + list(reversed(deque([term for term in self.sequence])))[0])/2)*self._terms


class GeometricSequence(object):

    def __init__(self, firstterm=1, ratio=2, terms=10):
        if terms > 1499:
            raise ValueError("Terms above 1499 are not allowed due to system limitations.")
        if ratio == 0:
            raise ValueError("Ratio must be greater than 0.")
        if ratio > 100:
            raise ValueError("Ratio above 100 is not allowed due to system limitations.")
        self._difference = difference
        self._firstterm = firstterm
        self._ratio = ratio

    @property
    def sequence(self):
        return (term for term in self._firstterm*pow(self._ratio, i) for i in range(self._terms)):

    @property
    def series(self):
        return self._firstterm*((pow(self._ratio, self._terms) - 1)/(self._ratio - 1))
