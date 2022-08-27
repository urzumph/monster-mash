#!/usr/bin/python
import logging
import collections


class Fragment:
    def __init__(self, strfrag):
        self.matched = False
        self.matcher = None
        self.string = strfrag

    def register_match(self, mid):
        self.matched = True
        self.matcher = mid

    def as_dict(self):
        return {"string": self.string, "matched": self.matched, "matcher": self.matcher}

    def __str__(self):
        if self.matched:
            return f"'{self.string}' - Matched by {self.matcher}"
        else:
            return f"'{self.string}' - Unmatched"

    def __repr__(self):
        return f"Fragment({self.string})"


class Parser:
    def __init__(
        self,
        name,
        actuator,
        index=None,
        regex=None,
        accumulate=False,
        accum_end_regex=None,
        accum_include_end=False,
        bam=False,
        line_dewrap=False,
    ):
        self.name = name
        self._actuator = actuator
        self._index = index
        self._regex = regex
        self._rematch = None
        self.accumulater = accumulate
        self._end_regex = accum_end_regex
        self.accum_include_end = accum_include_end
        self.line_dewrap = line_dewrap
        if self.accumulater and not self._end_regex:
            raise ValueError("In accumulater mode, an end regex is required")
        # Break after match
        self.bam = bam
        if (self.accumulater and not self.accum_include_end) and self.bam:
            raise ValueError(
                "Cannot use non-inclusive accumulation and break-after-match together"
            )
        if self.accumulater and self.line_dewrap:
            raise ValueError("Cannot use accumulation and line-dewrap together")

    def match(self, idx, frag):
        logging.debug("%s.match(idx %d , frag %s)", self, idx, frag.string)
        self.text = ""
        # Multiple matches may be required.
        # Match logic is at least one, and all supplied match
        to_ret = False
        if self._index is not None:
            if idx == self._index:
                self.text = frag.string
                to_ret = True
            else:
                return False
        if self._regex is not None:
            m = self._regex.search(frag.string)
            if m:
                self._rematch = m
                if self.accumulater:
                    # When accumulating, we need to check if this match is single or multi-line.
                    # In multiline, we need the whole string even if the
                    # match did not cover the whole line.
                    self.text = frag.string
                    # In single-line, we need to remove everything after the end match
                    if self.end_match(frag):
                        self.text = self.text[0 : self._end_rematch.end()]
                else:
                    self.text = m.group(0)
                if len(self.text) == 0:
                    logging.warning(
                        "WARN: 0 length match during %s.match(idx %d , frag %s), returning no-match.",
                        self,
                        idx,
                        frag.string,
                    )
                    return False
                to_ret = True
            else:
                return False
        return to_ret

    def dewrap_match(self, idx, frag_one, frag_two):
        logging.debug(
            "%s.dewrap_match(idx %d , frag_one %s, frag_two %s)",
            self,
            idx,
            frag_one.string,
            frag_two.string,
        )
        matchable = frag_one.string + " " + frag_two.string
        self.text = ""
        if self._regex is None:
            raise TypeError(
                f"dewrap_match called on {self} which does not have a regex defined"
            )
        else:
            m = self._regex.search(matchable)
            if m:
                self._rematch = m
                self.text = m.group(0)
                end = self._rematch.end()
                frag_one.string = matchable[0:end]
                frag_two.string = matchable[end:]
                return True
        return False

    def actuate(self, charsheet):
        self._actuator(charsheet, text=self.text, rematch=self._rematch)

    def split(self, frag, end=False):
        """Given a fragment which this parser match()'d,
        modify the fragment to include only the matched text
        from the match() and return a new fragment containing
        all of the remaining text."""
        match = self._rematch
        if end:
            match = self._end_rematch
        if not match:
            logging.debug(
                "%s failed to split non-regex matched fragment %s (end=%s)",
                self,
                frag,
                end,
            )
            return False
        end = match.end()
        if end < len(frag.string):
            post = frag.string[end:]
            pre = frag.string[0:end]
            logging.debug(
                "%s splitting fragment %s to %s & %s", self, frag.string, pre, post
            )
            newfrag = Fragment(post)
            frag.string = pre
            return newfrag
        else:
            return False

    def end_match(self, frag):
        """Determine whether this fragment is matched by the ending regex
        and return the result. No further action is taken.
        As a special case, refuse to match the same exact text as both
        a start and end match."""
        self._end_rematch = self._end_regex.search(frag.string)
        if self._end_rematch and self._end_rematch.group(0) == self._rematch.group(0):
            return False
        return self._end_rematch

    def accumulate(self, idx, frag):
        """Determine whether the passed fragment is the end of the accumulated
        text, and if not add it to the gathered text of this parser."""
        self.end_match(frag)
        result = False
        if self._end_rematch:
            result = True
        if not result or self.accum_include_end:
            # if none already exists, force whitespace at line breaks
            if self.text[-1] != " ":
                self.text += " "
            to_append = frag.string
            # If we're going to break after this, we need to remove the non-matched post text, otherwise it will be included in the accumulation.
            if result and self.bam:
                to_append = frag.string[0 : self._end_rematch.end()]
            logging.debug(
                "Parser.accumulate(%s) appending %s to accummulation.",
                self.name,
                to_append,
            )
            self.text += to_append
        return result

    def __str__(self):
        return f"Parser({self.name})"

    def __repr__(self):
        return self.__str__()


class Document:
    def __init__(self, strarray):
        self.frags = []
        for s in strarray:
            self.frags.append(Fragment(s))

    def stats(self):
        res = []
        for f in self.frags:
            res.append(f.as_dict())
        return res

    def score(self):
        num = 0
        denum = 0
        for f in self.frags:
            denum += len(f.string)
            if f.matched:
                num += len(f.string)
        return num / denum

    def __str__(self):
        s = ""
        for f in self.frags:
            s += f"{f}\n"
        return s

    def do_bam(self, parser, idx, accum_end):
        if not parser.bam:
            logging.debug("Document.do_bam skipping bam for non-bam parser: %s", parser)
            return
        frag = self.frags[idx]
        remainder = parser.split(frag, accum_end)
        logging.debug("Document.do_bam before: %s", self.frags)
        if remainder:
            self.frags = self.frags[0 : idx + 1] + [remainder] + self.frags[idx + 1 :]
        logging.debug("Document.do_bam after: %s", self.frags)

    def single_pass(self, parser, charsheet, offset):
        logging.debug(
            "Document.single_pass starting on parser %s with offset %d",
            parser.name,
            offset,
        )
        accum = False
        end_accum = False
        for idx, frag in enumerate(self.frags[offset:], offset):
            logging.debug(f"Document.single_pass enumerate: idx: {idx} frag: {frag}")
            if accum:
                # We have already matched and are accumulating
                end_accum = parser.accumulate(idx, frag)
                if end_accum:
                    logging.debug(
                        "Document.single_pass end_accum found for parser %s with idx %d, frag %s",
                        parser.name,
                        idx,
                        frag.string,
                    )
                    # Returned index needs to be last of the matching lines for this pass.
                    last = idx - 1
                    if parser.accum_include_end:
                        frag.register_match(parser.name)
                        self.do_bam(parser, idx, True)
                        last = idx

                    parser.actuate(charsheet)
                    return last
                else:
                    frag.register_match(parser.name)

            else:
                # Not accumulating (yet or at all)
                match = parser.match(idx, frag)
                if not match and parser.line_dewrap and (idx + 1) < len(self.frags):
                    match = parser.dewrap_match(idx, frag, self.frags[idx + 1])
                if match:
                    logging.debug(
                        "Document.single_pass %s match at idx %d / frag %s",
                        parser,
                        idx,
                        frag.string,
                    )
                    frag.register_match(parser.name)
                    single_line_accum = False
                    if parser.accumulater:
                        em = parser.end_match(frag)
                        logging.debug(
                            "Document.single_pass single_line_accum check: %s",
                            em,
                        )
                        if em:
                            single_line_accum = True
                        else:
                            accum = True
                            continue
                    logging.debug(
                        "Document.single_pass single line actuate starting for %s",
                        parser,
                    )
                    self.do_bam(parser, idx, single_line_accum)
                    parser.actuate(charsheet)
                    return idx
        else:
            if accum:
                # We accumulated all the way to the end of the document.
                parser.actuate(charsheet)
            return None

    def parse(self, parsers, charsheet):
        logging.debug("Document.parse started with parsers: %s", parsers)
        for parser in parsers:
            logging.debug("Document.parse starting parser: %s", parser.name)
            logging.debug("Current doc state:\n%s", self)
            start = 0
            matched = False
            while start is not None and start < len(self.frags):
                # print(f"Starting at: {start} - {self.frags[start]}")
                end = self.single_pass(parser, charsheet, start)
                # print(f"end = {end}")
                if end is not None:
                    matched = True
                    start = end + 1
                else:
                    start = None
            if not matched:
                logging.debug("Warning: No text matched parser %s", parser.name)
