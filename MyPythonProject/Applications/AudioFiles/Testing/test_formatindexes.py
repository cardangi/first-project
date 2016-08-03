# -*- coding: ISO-8859-1 -*-
from unittest import TestCase, main
from ..Modules import shared

__author__ = 'Xavier ROSSET'


class TestFormatindexes(TestCase):

    def test_first(self):
        self.assertEqual("1, 2, 3", shared.formatindexes("1, 2, 3"))

    def test_second(self):
        self.assertEqual("1, 2, 3", shared.formatindexes("1-3"))

    def test_third(self):
        self.assertEqual("1, 2, 3, 5, 6, 9, 10, 11, 12", shared.formatindexes("1-3, 5-6, 9-12"))

    def test_fourth(self):
        self.assertEqual("1, 2, 3, 15, 16", shared.formatindexes("1-3, 5-6-10, 15, 16"))

    def test_fifth(self):
        self.assertEqual("1", shared.formatindexes("1"))

    def test_sixth(self):
        self.assertEqual("", shared.formatindexes("1,2"))

    def test_seventh(self):
        self.assertEqual("", shared.formatindexes("1-2-3-4"))

    def test_eighth(self):
        self.assertEqual("", shared.formatindexes("1 2 3 4"))

    def test_ninth(self):
        self.assertEqual("", shared.formatindexes(""))

    def test_tenth(self):
        self.assertEqual("1, 2, 3, 5, 6, 9, 10, 11, 12, 15, 16", shared.formatindexes("1-3, 5-6, 9-12, 15, 16"))


if __name__ == '__main__':
    main()
