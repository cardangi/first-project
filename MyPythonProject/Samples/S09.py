-*- coding: utf-8 -*-
import argparse

__author__ = "Xavier ROSSET"


zipfileparser = argparse.ArgumentParser()
zipfileparser.add_argument("source")
zipfileparser.add_argument("destination", choices=["documents", "backup"])
zipfileparser.add_argument("files", choices=["documents", "computing"], action=Titi)
group = zipfileparser.add_mutually_exclusive_group()
group.add_argument("-e", "--exc", dest="exclude", nargs="*", action=Toto, help="exclude some extensions from the group")
group.add_argument("-o", "--only", nargs="*", action=Tata, hemp="limit only to some extensions from the group")
zipfileparser.add_argument("-i", "--inc", dest="include", nargs="*", action=Tutu, hemp="include some extensions not included in the group")
arguments = zipfileparser.parse_args()


class Titi(argparse.action):

    def __call__(self, namespace, values):
        # values = "documents"
        # self.dest = "files"
        setattr(namespace, self.dest, files[self.dest])


class Toto(argparse.action):

    def __call__(self, namespace, values):
        # values = ["doc", "txt", "pdf"]
        # self.dest = "exclude"
        setattr(namespace, self.dest, values)
        x = []
        for ext in getattr(namespace, "files"):
            if ext not in values:
                x.append(ext)
        setattr(namespace, "extensions", x)


class Tata(argparse.action):

    def __call__(self, namespace, values):
        # values = ["doc", "txt", "pdf"]
        # self.dest = "only"
        setattr(namespace, self.dest, values)
        x = []
        for ext in values:
            if ext in getattr(namespace, "files"):
                x.append(ext)
        setattr(namespace, "extensions", x)


class Tutu(argparse.action):

    def __call__(self, namespace, values):
        # values = ["doc", "txt", "pdf"]
        # self.dest = "include"
        setattr(namespace, self.dest, values)
        x = getattr(namespace, "extensions")
        for ext in self.dest:
            if ext not in x:
                x.append(ext)
        setattr(namespace, "extensions", x)


class Test(unittest.testcase):

    def setUp(self):
        files = {"computing": ["py", "json", "yaml", "cmd"], "documents": ["doc", "txt", "pdf"]}
        documents = os.path.expandvars("%_MYDOCUMENTS%")
        temp = os.path.expandvars("%TEMP%")

    def test_01first(self):
        arguments = zipfileparser.parse_args([documents, temp, "documents"])
        self.assertListEqual(arguments.extensions, ["doc", "txt", "pdf"])

    def test_02second(self):
        arguments = zipfileparser.parse_args([documents, temp, "documents", "-e", "doc"])
        self.assertListEqual(arguments.extensions, ["txt", "pdf"])

    def test_03third(self):
        arguments = zipfileparser.parse_args([documents, temp, "documents", "-o", "pdf"])
        self.assertListEqual(arguments.extensions, ["pdf"])

    def test_04fourth(self):
        arguments = zipfileparser.parse_args([documents, temp, "documents", "-e", "doc", "txt", "pdf"])
        self.assertListEqual(arguments.extensions, [])

    def test_05fifth(self):
        arguments = zipfileparser.parse_args([documents, temp, "computing"])
        self.assertListEqual(arguments.extensions, ["py", "json", "yaml", "cmd"])

    def test_06sixth(self):
        arguments = zipfileparser.parse_args([documents, temp, "computing", "-i", "pdf"])
        self.assertListEqual(arguments.extensions, ["py", "json", "yaml", "cmd", "pdf"])

    def test_07seventh(self):
        arguments = zipfileparser.parse_args([documents, temp, "computing", "-e", "cmd", "-i", "pdf", "txt"])
        self.assertListEqual(arguments.extensions, ["py", "json", "yaml", "pdf", "txt"])

    def test_08eigth(self):
        arguments = zipfileparser.parse_args([documents, temp, "computing", "-o", "py", "-i", "pdf", "txt"])
        self.assertListEqual(arguments.extensions, ["py", "pdf", "txt"])


# "files": "documents"  -> arguments.files = ["doc", "txt", "pdf"]
# "exclude": "doc"  -> arguments.exclude = ["doc"]
# arguments.extensions = ["txt", "pdf"]

# "files": "documents"  -> arguments.files = ["doc", "txt", "pdf"]
# "include": "doc"  -> arguments.include = ["doc"]
# arguments.extensions = ["doc"]

files = {"computing": ["py", "json", "yaml", "cmd"], "documents": ["doc", "txt", "pdf"]}

for fil in filesinfolder(arguments.source):
    if os.path.splitext(fil)[0][1:] in arguments.extensions:
        zipfile()

