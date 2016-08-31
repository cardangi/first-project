# -*- coding: ISO-8859-1 -*-
from itertools import repeat
from decimal import Decimal
from operator import mul
import cmath

__author__ = 'Xavier ROSSET'


# ========
# Classes.
# ========
class Circle(object):

    pi = Decimal(cmath.pi)

    def __init__(self, radius):
        self._diameter = 0
        self.radius = radius

    @property
    def diameter(self):
        return self._diameter

    @property
    def radius(self):
        return self._diameter/Decimal("2")

    @radius.setter
    def radius(self, value):
        self._diameter = Decimal(value)*Decimal("2")

    @property
    def perimeter(self):
        return self.diameter*self.pi

    @property
    def surface(self):
        return self.pi*self.radius**2


class ArithmeticSequence(object):
    """
    Compute arithmetic sequences.
    """
    def __init__(self, firstterm=1, difference=1, terms=10):
        """
        :param firstterm: first term of the sequence.
        :param difference: common difference between two consecutive terms of the sequence.
        :param terms: number of returned terms.
        """
        self._terms = 0
        self._difference = 0
        self._firstterm = Decimal(firstterm)
        self.terms = terms
        self.difference = difference

    @property
    def sequence(self):
        for i in range(self.terms):
            yield self._firstterm + i*self.difference

    @property
    def series(self):
        return ((self._firstterm + self.lastterm)/2)*self.terms

    @property
    def terms(self):
        return self._terms

    @terms.setter
    def terms(self, value):
        value = int(Decimal(value))
        if value == 0:
            raise ValueError("Terms must be greater than 0.")
        if value > 49999:
            raise ValueError("Terms must be lower than 50000 due to system limitations.")
        self._terms = value

    @property
    def difference(self):
        return self._difference

    @difference.setter
    def difference(self, value):
        value = Decimal(value)
        if value.compare(Decimal("0")) == Decimal("0"):
            raise ValueError("Difference must be greater than 0.")
        self._difference = value

    @property
    def lastterm(self):
        return list(reversed(list(self.sequence)))[0]

    @classmethod
    def fromsequence(cls, seq):
        return cls(seq[0], seq[1] - seq[0], len(seq))


class GeometricSequence(object):
    """
    Compute geometric sequences.
    """
    def __init__(self, firstterm=1, ratio=2, terms=10):
        """
        :param firstterm: first term of the sequence.
        :param ratio: common ratio between two consecutive terms of the sequence.
        :param terms: number of returned terms.
        """
        self._terms = 0
        self._ratio = 0
        self._firstterm = Decimal(firstterm)
        self.terms = terms
        self.ratio = ratio

    @property
    def sequence(self):
        for element in map(mul, repeat(self._firstterm), map(pow, repeat(self.ratio), map(Decimal, range(self.terms)))):
            yield element

    @property
    def series(self):
        return self._firstterm*((pow(self.ratio, self.terms) - 1)/(self.ratio - 1))

    @property
    def terms(self):
        return self._terms

    @terms.setter
    def terms(self, value):
        value = int(Decimal(value))
        if value == 0:
            raise ValueError("Terms must be greater than 0.")
        if value > 1499:
            raise ValueError("Terms must be lower than 1500 due to system limitations.")
        self._terms = value

    @property
    def ratio(self):
        return self._ratio

    @ratio.setter
    def ratio(self, value):
        value = Decimal(value)
        if value.compare(Decimal("0")) == Decimal("0"):
            raise ValueError("Ratio must be greater than 0.")
        if value.compare(Decimal("1")) == Decimal("0"):
            raise ValueError("Ratio must be different from 1.")
        if value.compare(Decimal("99")) == Decimal("1"):
            raise ValueError("Ration must be lower than 100 due to system limitations.")
        self._ratio = value

    @property
    def lastterm(self):
        return list(reversed(list(self.sequence)))[0]


# ==========
# Functions.
# ==========
def power_sum(x, n):
    """
    Return result of 1 + x**1 + x**2 + x**3 + ... + x**n.
    :param x: constant operand.
    :param n: rising exponent.
    :return: value of 1 + x**1 + x**2 + x**3 + ... + x**n.
    """
    return (pow(Decimal(x), int(Decimal(n)) + Decimal(1)) - Decimal(1))/(Decimal(x) - Decimal(1))


def sequence_sum(n):
    """
    Return result of 1 + 2 + 3 + 4 + ... + n.
    :param n: rising operand.
    :return: value of 1 + 2 + 3 + 4 + ... + n.
    """
    return (int(Decimal(n))*(int(Decimal(n)) + Decimal(1)))/Decimal(2)
