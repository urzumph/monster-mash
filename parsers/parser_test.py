import unittest
import re
from . import parser


class TestParser(unittest.TestCase):
    def setUp(self):
        self.call_count = {}

    def add_call(self, func):
        if func in self.call_count:
            self.call_count[func] += 1
        else:
            self.call_count[func] = 1

    def expect_a(self, charsheet, text, **kwargs):
        self.add_call("expect_a")
        self.assertEqual(text, "a")

    def expect_numbers(self, charsheet, text, **kwargs):
        self.add_call("expect_numbers")
        self.assertEqual(text, "012 345 678")

    def test_fragment(self):
        frag = parser.Fragment("a")
        self.assertEqual(frag.matched, False)
        self.assertEqual(f"{frag}", "'a' - Unmatched")
        frag.register_match("test matcher")
        self.assertEqual(frag.matched, True)
        self.assertEqual(f"{frag}", "'a' - Matched by test matcher")

    def test_parser_match_idx(self):
        frag = parser.Fragment("a")
        pobj = parser.Parser("test parser", None, index=0)
        self.assertEqual(pobj.match(0, frag), True)
        self.assertEqual(pobj.match(1, frag), False)

    def test_parser_match_re(self):
        frag = parser.Fragment("a")
        matcher = re.compile("^a$")
        pobj = parser.Parser("test regex", self.expect_a, regex=matcher)
        self.assertEqual(pobj.match(0, frag), True)
        # Ignore the index if one isn't provided
        self.assertEqual(pobj.match(1, frag), True)
        # N.B. Since we never call actuate we can't test call counts here.

    def test_parser_bam(self):
        doc = parser.Document(["012", "abc"])
        matcher = re.compile("^a")
        pobj = parser.Parser("test", self.expect_a, regex=matcher, bam=True)
        doc.parse([pobj], None)
        self.assertEqual(
            doc.stats(),
            [
                {"string": "012", "matched": False, "matcher": None},
                {"string": "a", "matched": True, "matcher": "test"},
                {"string": "bc", "matched": False, "matcher": None},
            ],
        )
        self.assertEqual(self.call_count.get("expect_a", 0), 1)

    def test_parser_accum(self):
        doc = parser.Document(["012", "345", "678", "abc"])
        matcher = re.compile("^\d")
        end_matcher = re.compile("^[a-z]")
        pobj = parser.Parser(
            "test",
            self.expect_numbers,
            regex=matcher,
            accumulate=True,
            accum_end_regex=end_matcher,
        )
        doc.parse([pobj], None)
        self.assertEqual(
            doc.stats(),
            [
                {"string": "012", "matched": True, "matcher": "test"},
                {"string": "345", "matched": True, "matcher": "test"},
                {"string": "678", "matched": True, "matcher": "test"},
                {"string": "abc", "matched": False, "matcher": None},
            ],
        )
        self.assertEqual(self.call_count.get("expect_numbers", 0), 1)

    def test_parser_accum_no_end_match(self):
        doc = parser.Document(["012", "345", "678"])
        matcher = re.compile("^\d")
        end_matcher = re.compile("^[a-z]")
        pobj = parser.Parser(
            "test",
            self.expect_numbers,
            regex=matcher,
            accumulate=True,
            accum_end_regex=end_matcher,
        )
        doc.parse([pobj], None)
        self.assertEqual(
            doc.stats(),
            [
                {"string": "012", "matched": True, "matcher": "test"},
                {"string": "345", "matched": True, "matcher": "test"},
                {"string": "678", "matched": True, "matcher": "test"},
            ],
        )
        self.assertEqual(self.call_count.get("expect_numbers", 0), 1)

    def test_document(self):
        pobj = parser.Parser("test parser", self.expect_a, index=0)
        doc = parser.Document(["a", "b"])
        doc.parse([pobj], None)
        self.assertEqual(f"{doc}", "'a' - Matched by test parser\n'b' - Unmatched\n")
        self.assertEqual(
            doc.stats(),
            [
                {"string": "a", "matched": True, "matcher": "test parser"},
                {"string": "b", "matched": False, "matcher": None},
            ],
        )
        self.assertEqual(self.call_count.get("expect_a", 0), 1)


if __name__ == "__main__":
    unittest.main()
