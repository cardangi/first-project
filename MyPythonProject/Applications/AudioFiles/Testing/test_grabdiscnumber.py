# -*- coding: ISO-8859-1 -*-
import re
from unittest import TestCase, main
from ..Modules import shared as s1
from ... import shared as s2

__author__ = 'Xavier ROSSET'


class TestGrabdiscnumber(TestCase):

    def test_first(self):
        self.assertEqual((True, "1"), s1.grabdiscnumber(r"bs160517d1_02_No_Surrender.flac", re.compile(r"[a-z]\B(?:1[1-9])(?:{0})(?:{1})d(\d)\B_".format(s2.DFTMONTHREGEX, s2.DFTDAYREGEX), re.IGNORECASE)))

    def test_second(self):
        self.assertEqual((True, "2"), s1.grabdiscnumber(r"bs160517d2_02_No_Surrender.flac", re.compile(r"[a-z]\B(?:1[1-9])(?:{0})(?:{1})d(\d)\B_".format(s2.DFTMONTHREGEX, s2.DFTDAYREGEX), re.IGNORECASE)))

    def test_third(self):
        self.assertEqual((True, "3"), s1.grabdiscnumber(r"bs160517d3_02_No_Surrender.flac", re.compile(r"[a-z]\B(?:1[1-9])(?:{0})(?:{1})d(\d)\B_".format(s2.DFTMONTHREGEX, s2.DFTDAYREGEX), re.IGNORECASE)))

    def test_fourth(self):
        self.assertEqual((False, None), s1.grabdiscnumber(r"bs20160517d1_02_No_Surrender.flac", re.compile(r"[a-z]\B(?:1[1-9])(?:{0})(?:{1})d(\d)\B_".format(s2.DFTMONTHREGEX, s2.DFTDAYREGEX), re.IGNORECASE)))

    def test_fifth(self):
        self.assertEqual((False, None), s1.grabdiscnumber(r"dummy regular expression", re.compile(r"[a-z]\B(?:1[1-9])(?:{0})(?:{1})d(\d)\B_".format(s2.DFTMONTHREGEX, s2.DFTDAYREGEX), re.IGNORECASE)))

    def test_sixth(self):
        self.assertEqual((True, "4"), s1.grabdiscnumber(r"bstuvwxyz160517d4_02_No_Surrender.flac", re.compile(r"[a-z]\B(?:1[1-9])(?:{0})(?:{1})d(\d)\B_".format(s2.DFTMONTHREGEX, s2.DFTDAYREGEX), re.IGNORECASE)))


if __name__ == '__main__':
    main()
