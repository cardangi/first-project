# -*- coding: ISO-8859-1 -*-

__author__ = 'Xavier ROSSET'


class Circle(object):

    def __init__(self, radius):
        self.radius = radius

    @property
    def radius(self):
        return self._diameter/2

    @radius.setter
    def radius(self, value):
        self._diameter = value*2

    @perimeter
    def perimeter(self):
        return 2*math.pi*self.radius

    @surface
    def surface(self):
        return math.pi*self.radius**2


class ArithmeticSequence(object):

    def __init__(self, firstterm=1, difference=1, terms=10):
        self.difference = difference
        self.terms = terms
        self._firstterm = firstterm

    @property
    def sequence(self):
        for term in range(self._firstterm, self._firstterm + (self.difference*self.terms), self.difference):
            yield term

    @property
    def series(self):
        return ((self._firstterm + self.lastterm)/2)*self.terms

    @property
    def terms(self):
        return self._terms

    @terms.setter
    def terms(self, value):
        if value > 49999:
            raise ValueError("Terms above 49999 are not allowed due to system limitations.")
        self._terms = value

    @property
    def difference(self):
        return self._difference

    @difference.setter
    def difference(self, value):
        if value == 0:
            raise ValueError("Difference must be greater than 0.")
        self._difference = value

    @property
    def lastterm(self):
        return list(reversed([term for term in self.sequence]))[0]


class GeometricSequence(object):

    def __init__(self, firstterm=1, ratio=2, terms=10):
        self.terms = terms
        self.ratio = ratio
        self._firstterm = firstterm

    @property
    def sequence(self):
        return (term for term in self._firstterm*pow(self.ratio, i) for i in range(self.terms)):

    @property
    def series(self):
        return self._firstterm*((pow(self.ratio, self.terms) - 1)/(self.ratio - 1))

    @property
    def terms(self):
        return self._terms

    @terms.setter
    def terms(self, value):
        if value > 1499:
            raise ValueError("Terms above 1499 are not allowed due to system limitations.")
        self._terms = value

    @property
    def ratio(self):
        return self._ratio

    @ratio.setter
    def ratio(self, value):
        if value == 0:
            raise ValueError("Ratio must be greater than 0.")
        if value > 100:
            raise ValueError("Ratio above 100 is not allowed due to system limitations.")
        self._ratio = value
