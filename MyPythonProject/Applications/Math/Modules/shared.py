# -*- coding: ISO-8859-1 -*-
__author__ = 'Xavier ROSSET'


def arithmeticsequence(firstterm, difference, terms):
    """
    :param firstterm: first term of the sequence.
    :param difference: common difference between two consecutive terms of the sequence.
    :param terms: number of calculated terms.
    :return:
    """
    for i in range(firstterm, firstterm + (difference*terms), difference):
        yield i


def arithmeticseries(firstterm, difference, terms):
    """
    :param firstterm: first term of the sequence.
    :param difference: common difference between two consecutive terms of the sequence.
    :param terms: number of terms.
    :return:
    """
    series = 0
    for i in arithmeticsequence(firstterm, difference, terms):
        series = ((firstterm + i)/2)*terms
    return series


def geometricsequence(firstterm, ratio, terms):
    """
    :param firstterm: first term of the sequence.
    :param ratio: common ratio between two consecutive terms of the sequence.
    :param terms: number of calculated terms.
    :return:
    """
    from math import pow
    l = list((firstterm,))
    for i in range(1, terms):
        l.append(firstterm*pow(ratio, i))
    for term in l:
        yield term


def geometricseries(firstterm, ratio, terms):
    """
    :param firstterm: first term of the sequence.
    :param ratio: common ratio between two consecutive terms of the sequence.
    :param terms: number of calculated terms.
    :return:
    """
    from math import pow
    return firstterm*((pow(ratio, terms) - 1)/(ratio - 1))
