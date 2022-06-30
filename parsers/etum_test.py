import unittest
from tests import ParserTest
from . import etum


class TestEtumParser(ParserTest):
    name = "etum"
    parsers = etum.parsers
    tests = ["etum_minotaurchief", "etum_psihulk"]


if __name__ == "__main__":
    unittest.main()
