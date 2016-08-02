# -*- coding: ISO-8859-1 -*-
from unittest import TestCase, main
from Applications.AudioFiles.Modules import shared

__author__ = 'Xavier ROSSET'


class TestGetfilefromindex(TestCase):

    def test_first(self):
        self.assertEqual(["file_01", "file_02", "file_03"], shared.getfilefromindex("1, 2, 3", ["file_01", "file_02", "file_03"]))

    def test_second(self):
        self.assertEqual(["file_01", "file_02", "file_03", "file_04", "file_05"], shared.getfilefromindex("1-5", ["file_01", "file_02", "file_03", "file_04", "file_05"]))

    def test_third(self):
        self.assertEqual(["file_01", "file_02", "file_03", "file_04", "file_05"], shared.getfilefromindex("1-10", ["file_01", "file_02", "file_03", "file_04", "file_05"]))

    def test_fourth(self):
        self.assertEqual([], shared.getfilefromindex("1-2-3", ["file_01", "file_02", "file_03", "file_04", "file_05"]))

    def test_fifth(self):
        self.assertEqual([], shared.getfilefromindex("6-10", ["file_01", "file_02", "file_03", "file_04", "file_05"]))

    def test_sixth(self):
        self.assertEqual(["file_01", "file_02", "file_03"], shared.getfilefromindex("1, 2, 3, 4, 5", ["file_01", "file_02", "file_03"]))

    def test_seventh(self):
        self.assertEqual(["file_05"], shared.getfilefromindex("5-10", ["file_01", "file_02", "file_03", "file_04", "file_05"]))

    def test_eighth(self):
        self.assertEqual([], shared.getfilefromindex("1,2,3", ["file_01", "file_02", "file_03", "file_04", "file_05"]))

    def test_ninth(self):
        self.assertEqual([], shared.getfilefromindex("1,2,3,9-10", ["file_01", "file_02", "file_03", "file_04", "file_05"]))

if __name__ == '__main__':
    main()
