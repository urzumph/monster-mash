import unittest
from tests import ParserTest
from . import cotsq_long


class TestSrdParser(ParserTest):
    name = "cotsq_long"
    parsers = cotsq_long.parsers
    tests = ["cotsqlong_vampiredrider"]


if __name__ == "__main__":
    unittest.main()
