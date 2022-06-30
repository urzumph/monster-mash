import unittest
from tests import ParserTest
from . import srd


class TestSrdParser(ParserTest):
    name = "srd"
    parsers = srd.parsers
    tests = ["srd_drider"]


if __name__ == "__main__":
    unittest.main()
