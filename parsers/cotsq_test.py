import unittest
from tests import ParserTest
from . import cotsq


class TestCotsqParser(ParserTest):
    name = "cotsq"
    parsers = cotsq.parsers
    tests = ParserTest.with_prefix("cotsq_")


if __name__ == "__main__":
    unittest.main()
