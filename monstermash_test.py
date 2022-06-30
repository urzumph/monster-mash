import os
import unittest
from tests import ParserTest
import monstermash

files = filter(lambda x: x.endswith(".txt"), os.listdir("tests/"))
files = map(lambda x: x[:-4], files)


class TestMonsterMashParser(ParserTest):
    name = "MonsterMash"
    parsers = None
    tests = files

    def genericParserFunction(self, tarr):
        return monstermash.parse(tarr)


if __name__ == "__main__":
    unittest.main()
