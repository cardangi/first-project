# -*- coding: ISO-8859-1 -*-
from decimal import Decimal, getcontext, ROUND_HALF_UP
import cmath

__author__ = 'Xavier ROSSET'


class Circle(object):

    getcontext().prec = 6
    getcontext().rounding = ROUND_HALF_UP
    pi = Decimal(cmath.pi)

    def __init__(self, radius):
        self.diameter = 0
        self.radius = radius

    @property
    def radius(self):
        return self.diameter/2

    @radius.setter
    def radius(self, value):
        self.diameter = Decimal(value)*2

    @property
    def perimeter(self):
        return self.radius*2*self.pi

    @property
    def surface(self):
        return self.pi*self.radius**2


class ArithmeticSequence(object):
    """
    Compute arithmetic sequences.
    """
    getcontext().prec = 12
    getcontext().rounding = ROUND_HALF_UP

    def __init__(self, firstterm=1, difference=1, terms=10):
        """
        :param firstterm: first term of the sequence.
        :param difference: common difference between two consecutive terms of the sequence.
        :param terms: number of calculated terms.
        :return:
        """
        self._terms = 0
        self._difference = 0
        self._firstterm = Decimal(firstterm)
        self.difference = difference
        self.terms = terms

    @property
    def sequence(self):
        for i in range(int(self.terms)):
            yield self._firstterm + i*self.difference

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
        self._terms = Decimal(value)

    @property
    def difference(self):
        return self._difference

    @difference.setter
    def difference(self, value):
        if value == 0:
            raise ValueError("Difference must be greater than 0.")
        self._difference = Decimal(value)

    @property
    def lastterm(self):
        return list(reversed([element for element in self.sequence]))[0]


class GeometricSequence(object):
    """
    Compute geometric sequences.
    """
    getcontext().prec = 16
    getcontext().rounding = ROUND_HALF_UP

    def __init__(self, firstterm=1, ratio=2, terms=10):
        """
        :param firstterm: first term of the sequence.
        :param ratio: common ratio between two consecutive terms of the sequence.
        :param terms: number of calculated terms.
        :return:
        """
        self._terms = 0
        self._ratio = 0
        self._firstterm = Decimal(firstterm)
        self.terms = terms
        self.ratio = ratio

    @property
    def sequence(self):
        for element in [self._firstterm*pow(self.ratio, element) for element in range(int(self.terms))]:
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
        self._terms = Decimal(value)

    @property
    def ratio(self):
        return self._ratio

    @ratio.setter
    def ratio(self, value):
        if value == 0:
            raise ValueError("Ratio must be greater than 0.")
        if value > 100:
            raise ValueError("Ratio above 100 is not allowed due to system limitations.")
        self._ratio = Decimal(value)


def formatnumber(n, rajust=5):
    """
    :param n: decimal.Decimal type number.
    :param rajust: right alignment given to number integer part.
    :return: aligned number.
    """
    part1, part2 = None, None
    numb = str(n)
    part1 = "{:>{rajust}}".format(numb, rajust=rajust)
    if "." in numb:
        l = numb.split(".")
        part1 = "{:>{rajust}}".format(l[0], rajust=rajust)
        part2 = l[1]
    if part2:
        return "{0}.{1}".format(part1, part2)
    return part1
