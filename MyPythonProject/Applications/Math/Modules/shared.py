# -*- coding: ISO-8859-1 -*-
import cmath

__author__ = 'Xavier ROSSET'


class Circle(object):

    def __init__(self, radius):
        self._diameter = 0
        self.radius = radius

    @property
    def radius(self):
        return self._diameter/2

    @radius.setter
    def radius(self, value):
        self._diameter = value*2

    @property
    def perimeter(self):
        return self._diameter*cmath.pi

    @property
    def surface(self):
        return cmath.pi*(self._diameter/2)**2


class ArithmeticSequence(object):
    """
    Compute arithmetic sequences.
    """

    def __init__(self, firstterm=1, difference=1, terms=10):
        """
        :param firstterm: first term of the sequence.
        :param difference: common difference between two consecutive terms of the sequence.
        :param terms: number of calculated terms.
        :return:
        """
        self._terms = 0
        self._difference = 0
        self._firstterm = firstterm
        self.difference = difference
        self.terms = terms

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
    """
    Compute geometric sequences.
    """

    def __init__(self, firstterm=1, ratio=2, terms=10):
        """
        :param firstterm: first term of the sequence.
        :param ratio: common ratio between two consecutive terms of the sequence.
        :param terms: number of calculated terms.
        :return:
        """
        self._terms = 0
        self._ratio = 0
        self._firstterm = firstterm
        self.terms = terms
        self.ratio = ratio

    @property
    def sequence(self):
        for element in [self._firstterm*pow(self.ratio, term) for term in range(self.terms)]:
            yield element

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


if __name__ == "__main__":

    c = Circle(10)
    print(c.perimeter)
    print(c.surface)

    s = ArithmeticSequence()
    for term in s.sequence:
        print(term)
    print(s.series)

    s = GeometricSequence()
    for term in s.sequence:
        print(term)
    print(s.series)
