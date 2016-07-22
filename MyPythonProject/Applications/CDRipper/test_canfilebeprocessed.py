# -*- coding: ISO-8859-1 -*-
from unittest import TestCase, main
from Applications.CDRipper.Modules import shared

__author__ = 'Xavier ROSSET'


class TestCanfilebeprocessed(TestCase):

    def test_first(self):
        self.assertTrue(shared.canfilebeprocessed("flac", *()))

    def test_second(self):
        self.assertFalse(shared.canfilebeprocessed("pdf", *()))

    def test_third(self):
        self.assertTrue(shared.canfilebeprocessed("flac", *("flac",)))

    def test_fourth(self):
        self.assertFalse(shared.canfilebeprocessed("mp3", *("flac",)))

    def test_fifth(self):
        self.assertFalse(shared.canfilebeprocessed("flac", *("pdf",)))

    def test_sixth(self):
        self.assertTrue(shared.canfilebeprocessed("FLAC", *()))

    def test_seventh(self):
        self.assertFalse(shared.canfilebeprocessed("PDF", *()))

    def test_eighth(self):
        self.assertTrue(shared.canfilebeprocessed("FLAC", *("flac",)))

    def test_ninth(self):
        self.assertTrue(shared.canfilebeprocessed("flac", *("FLAC",)))

    def test_tenth(self):
        self.assertTrue(shared.canfilebeprocessed("FLAC", *("FLAC",)))


if __name__ == '__main__':
    main()
