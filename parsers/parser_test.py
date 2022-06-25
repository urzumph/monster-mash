import unittest
import re
from . import parser


class TestParser(unittest.TestCase):
    def setUp(self):
        self.call_count_dict = {}
        self.maxDiff = None

    def add_call(self, func):
        if func in self.call_count_dict:
            self.call_count_dict[func] += 1
        else:
            self.call_count_dict[func] = 1

    def call_count(self):
        return self.call_count_dict.get(self.id(), 0)

    # Create a function for use as a callback which:
    # 1) Verifies that the provided text was as expected.
    # 2) Adds to the callback counter for this function.
    def expect(self, val):
        def expect_closure(charsheet, text, **kwargs):
            self.add_call(self.id())
            self.assertEqual(text, val)

        return expect_closure

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
        pobj = parser.Parser("test regex", self.expect("a"), regex=matcher)
        self.assertEqual(pobj.match(0, frag), True)
        # Ignore the index if one isn't provided
        self.assertEqual(pobj.match(1, frag), True)
        # N.B. Since we never call actuate we can't test call counts here.

    def test_parser_bam(self):
        doc = parser.Document(["012", "abc"])
        matcher = re.compile("^a")
        pobj = parser.Parser(self.id(), self.expect("a"), regex=matcher, bam=True)
        doc.parse([pobj], None)
        self.assertEqual(
            doc.stats(),
            [
                {"string": "012", "matched": False, "matcher": None},
                {"string": "a", "matched": True, "matcher": self.id()},
                {"string": "bc", "matched": False, "matcher": None},
            ],
        )
        self.assertEqual(self.call_count(), 1)

    def test_parser_accum(self):
        doc = parser.Document(["012", "345", "678", "abc"])
        matcher = re.compile("^\d")
        end_matcher = re.compile("^[a-z]")
        pobj = parser.Parser(
            self.id(),
            self.expect("012 345 678"),
            regex=matcher,
            accumulate=True,
            accum_end_regex=end_matcher,
        )
        doc.parse([pobj], None)
        self.assertEqual(
            doc.stats(),
            [
                {"string": "012", "matched": True, "matcher": self.id()},
                {"string": "345", "matched": True, "matcher": self.id()},
                {"string": "678", "matched": True, "matcher": self.id()},
                {"string": "abc", "matched": False, "matcher": None},
            ],
        )
        self.assertEqual(self.call_count(), 1)

    def test_parser_accum_no_end_match(self):
        doc = parser.Document(["012", "345", "678"])
        matcher = re.compile("^\d")
        end_matcher = re.compile("^[a-z]")
        pobj = parser.Parser(
            "test",
            self.expect("012 345 678"),
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
        self.assertEqual(self.call_count(), 1)

    def test_parser_accum_multi_match(self):
        doc = parser.Document(["012", "345", "678", "a", "012", "345", "678", "b"])
        matcher = re.compile("^\d")
        end_matcher = re.compile("^[a-z]")
        pobj = parser.Parser(
            "test",
            self.expect("012 345 678"),
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
                {"string": "a", "matched": False, "matcher": None},
                {"string": "012", "matched": True, "matcher": "test"},
                {"string": "345", "matched": True, "matcher": "test"},
                {"string": "678", "matched": True, "matcher": "test"},
                {"string": "b", "matched": False, "matcher": None},
            ],
        )
        self.assertEqual(self.call_count(), 2)

    def test_parser_accum_multi_match_no_end(self):
        doc = parser.Document(["012", "345", "678", "a", "012", "345", "678"])
        matcher = re.compile("^\d")
        end_matcher = re.compile("^[a-z]")
        pobj = parser.Parser(
            "test",
            self.expect("012 345 678"),
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
                {"string": "a", "matched": False, "matcher": None},
                {"string": "012", "matched": True, "matcher": "test"},
                {"string": "345", "matched": True, "matcher": "test"},
                {"string": "678", "matched": True, "matcher": "test"},
            ],
        )
        self.assertEqual(self.call_count(), 2)

    def test_parser_dewrap(self):
        doc = parser.Document(["012", "34;a", "bcd"])
        matcher = re.compile("^[\d\s]{4,}")
        pobj = parser.Parser(
            "test", self.expect("012 34"), regex=matcher, line_dewrap=True
        )
        doc.parse([pobj], None)
        self.assertEqual(
            doc.stats(),
            [
                {"string": "012 34", "matched": True, "matcher": "test"},
                {"string": ";a", "matched": False, "matcher": None},
                {"string": "bcd", "matched": False, "matcher": None},
            ],
        )
        self.assertEqual(self.call_count(), 1)

    def test_parser_accum_include_end(self):
        doc = parser.Document(["012", "345", "678;a", "bcd"])
        matcher = re.compile("\d+")
        end_matcher = re.compile(";")
        pobj = parser.Parser(
            self.id(),
            self.expect("012 345 678;"),
            regex=matcher,
            accumulate=True,
            accum_end_regex=end_matcher,
            accum_include_end=True,
            bam=True,
        )
        doc.parse([pobj], None)
        self.assertEqual(
            doc.stats(),
            [
                {"string": "012", "matched": True, "matcher": self.id()},
                {"string": "345", "matched": True, "matcher": self.id()},
                {"string": "678;", "matched": True, "matcher": self.id()},
                {"string": "a", "matched": False, "matcher": None},
                {"string": "bcd", "matched": False, "matcher": None},
            ],
        )
        self.assertEqual(self.call_count(), 1)

    def test_parser_accum_one_line(self):
        doc = parser.Document(["678;a", "bcd"])
        matcher = re.compile("\d+")
        end_matcher = re.compile(";")
        pobj = parser.Parser(
            self.id(),
            self.expect("678;"),
            regex=matcher,
            accumulate=True,
            accum_end_regex=end_matcher,
            accum_include_end=True,
            bam=True,
        )
        doc.parse([pobj], None)
        self.assertEqual(
            doc.stats(),
            [
                {"string": "678;", "matched": True, "matcher": self.id()},
                {"string": "a", "matched": False, "matcher": None},
                {"string": "bcd", "matched": False, "matcher": None},
            ],
        )
        self.assertEqual(self.call_count(), 1)

    def test_parser_multi_logic(self):
        hit_re = re.compile("^012")
        miss_re = re.compile("[abc]+")
        ## Index ONLY
        doc = parser.Document(["012", "abc", "678"])
        pobj = parser.Parser(self.id() + "_INDEX_ONLY", self.expect("012"), index=0)
        doc.parse([pobj], None)
        self.assertEqual(
            doc.stats(),
            [
                {
                    "string": "012",
                    "matched": True,
                    "matcher": self.id() + "_INDEX_ONLY",
                },
                {"string": "abc", "matched": False, "matcher": None},
                {"string": "678", "matched": False, "matcher": None},
            ],
        )
        ## REGEX ONLY
        doc = parser.Document(["012", "abc", "678"])
        pobj = parser.Parser(
            self.id() + "_REGEX_ONLY",
            self.expect("012"),
            regex=hit_re,
        )
        doc.parse([pobj], None)
        self.assertEqual(
            doc.stats(),
            [
                {
                    "string": "012",
                    "matched": True,
                    "matcher": self.id() + "_REGEX_ONLY",
                },
                {"string": "abc", "matched": False, "matcher": None},
                {"string": "678", "matched": False, "matcher": None},
            ],
        )
        ## BOTH, MATCH BOTH
        doc = parser.Document(["012", "abc", "678"])
        pobj = parser.Parser(
            self.id() + "_FULL_MATCH",
            self.expect("012"),
            index=0,
            regex=hit_re,
        )
        doc.parse([pobj], None)
        self.assertEqual(
            doc.stats(),
            [
                {
                    "string": "012",
                    "matched": True,
                    "matcher": self.id() + "_FULL_MATCH",
                },
                {"string": "abc", "matched": False, "matcher": None},
                {"string": "678", "matched": False, "matcher": None},
            ],
        )
        ## BOTH, MATCH RE ONLY
        doc = parser.Document(["012", "abc", "678"])
        pobj = parser.Parser(
            self.id() + "_HALF_MATCH_RE",
            self.expect("012"),
            index=1,
            regex=hit_re,
        )
        doc.parse([pobj], None)
        self.assertEqual(
            doc.stats(),
            [
                {"string": "012", "matched": False, "matcher": None},
                {"string": "abc", "matched": False, "matcher": None},
                {"string": "678", "matched": False, "matcher": None},
            ],
        )
        ## BOTH, MATCH INDEX ONLY
        doc = parser.Document(["012", "abc", "678"])
        pobj = parser.Parser(
            self.id() + "_HALF_MATCH_IDX",
            self.expect("012"),
            index=0,
            regex=miss_re,
        )
        doc.parse([pobj], None)
        self.assertEqual(
            doc.stats(),
            [
                {"string": "012", "matched": False, "matcher": None},
                {"string": "abc", "matched": False, "matcher": None},
                {"string": "678", "matched": False, "matcher": None},
            ],
        )
        self.assertEqual(self.call_count(), 3)

    def test_document(self):
        pobj = parser.Parser("test parser", self.expect("a"), index=0)
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
        self.assertEqual(doc.score(), 1 / 2)
        self.assertEqual(self.call_count(), 1)


if __name__ == "__main__":
    unittest.main()
