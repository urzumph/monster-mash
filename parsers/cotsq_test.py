import unittest
from tests import ParserTest
from . import cotsq


class TestCotsqParser(ParserTest):
    name = "cotsq"
    parsers = cotsq.parsers
    tests = ["cotsq_chahir", "cotsq_maurezhi", "cotsq_statue"]


if __name__ == "__main__":
    unittest.main()
