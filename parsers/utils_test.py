import unittest
import re
from . import utils


class TestUtils(unittest.TestCase):
    def test_regexiter(self):
        rxi = utils.RegexIter("a=1,b=2,potato", re.compile("(\w)=(\d),?"))
        count = 0
        for m in iter(rxi):
            if count == 0:
                self.assertEqual(m.group(1), "a")
                self.assertEqual(m.group(2), "1")
            if count == 1:
                self.assertEqual(m.group(1), "b")
                self.assertEqual(m.group(2), "2")
            if count > 1:
                self.fail(f"Got unexpected count: {count}")
            count += 1
        self.assertEqual(rxi.remainder, "potato")

    def test_prechomp_regex(self):
        s = "pre post"
        r = re.compile("^pre ?")
        result = utils.prechomp_regex(s, r)
        self.assertEqual(result, "post")
        r = re.compile("potato")
        result = utils.prechomp_regex(s, r)
        self.assertEqual(result, s)

    def test_postchomp_regex(self):
        s = "pre post"
        r = re.compile(" post\s*$")
        result = utils.postchomp_regex(s, r)
        self.assertEqual(result, "pre")
        r = re.compile(" potato\s*$")
        result = utils.prechomp_regex(s, r)
        self.assertEqual(result, s)

    def test_split_from(self):
        s = "pre post"
        r = re.compile(" ")
        left, right = utils.split_from(s, r)
        self.assertEqual(left, "pre")
        self.assertEqual(right, " post")
        r = re.compile("potato")
        left, right = utils.split_from(s, r)
        self.assertEqual(left, s)
        self.assertEqual(right, "")

    def test_maybe_int(self):
        s = "-"
        r = utils.maybe_int(s)
        self.assertEqual(s, r)
        s = "10"
        r = utils.maybe_int(s)
        self.assertEqual(r, 10)

    def test_undo_word_wrap(self):
        s = "word-\n wrap"
        r = utils.undo_word_wrap(s)
        self.assertEqual(r, "wordwrap")
