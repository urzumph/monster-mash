import unittest
from tests import ParserTest
from . import etum


class TestEtumParser(ParserTest):
    name = "etum"
    parsers = etum.parsers
    tests = ParserTest.with_prefix("etum_")


if __name__ == "__main__":
    unittest.main()
