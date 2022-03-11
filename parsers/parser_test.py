import unittest
import re
from . import parser


class TestParser(unittest.TestCase):
    def expect_frag_a(self, charsheet, text, **kwargs):
        self.assertEqual(text, "a")

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
        pobj = parser.Parser("test regex", self.expect_frag_a, regex=matcher)
        self.assertEqual(pobj.match(0, frag), True)
        # Ignore the index if one isn't provided
        self.assertEqual(pobj.match(1, frag), True)

    def test_document(self):
        pobj = parser.Parser("test parser", self.expect_frag_a, index=0)
        doc = parser.Document(["a", "b"])
        doc.parse([pobj], None)
        self.assertEqual(f"{doc}", "'a' - Matched by test parser\n'b' - Unmatched\n")


if __name__ == "__main__":
    unittest.main()
