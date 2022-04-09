#!/usr/bin/python
import logging


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


class Parser:
    def __init__(
        self,
        name,
        actuator,
        index=None,
        regex=None,
        accumulate=False,
        accum_end_regex=None,
        bam=False,
    ):
        self.name = name
        self._actuator = actuator
        self._index = index
        self._regex = regex
        self._rematch = None
        self.accumulater = accumulate
        self._end_regex = accum_end_regex
        if self.accumulater and not self._end_regex:
            raise ValueError("In accumulater mode, an end regex is required")
        # Break after match
        self.bam = bam
        if self.accumulater and self.bam:
            raise ValueError("Cannot use accumulation and break-after-match together")

    def match(self, idx, frag):
        self.text = ""
        # Multiple matches may be required.
        # Match logic is ANY OF
        to_ret = False
        if self._index is not None:
            if idx == self._index:
                self.text = frag.string
                to_ret = True
        if self._regex is not None:
            m = self._regex.search(frag.string)
            if m:
                self._rematch = m
                if self.accumulater:
                    # When accumulating, we need the whole string even if the
                    # match did not cover the whole line.
                    self.text = frag.string
                else:
                    self.text = m.group(0)
                to_ret = True
        return to_ret

    def actuate(self, charsheet):
        self._actuator(charsheet, text=self.text, rematch=self._rematch)

    def split(self, frag):
        """Given a fragment which this parser match()'d,
        modify the fragment to include only the matched text
        from the match() and return a new fragment containing
        all of the remaining text."""
        if not self._rematch:
            logging.debug(
                "%s failed to split non-regex matched fragment %s", self, frag
            )
            return False
        end = self._rematch.end()
        if end < len(frag.string):
            pre = frag.string[end:]
            post = frag.string[0:end]
            logging.debug(
                "%s splitting fragment %s to %s & %s", self, frag.string, pre, post
            )
            newfrag = Fragment(pre)
            frag.string = post
            return newfrag
        else:
            return False

    def accumulate(self, idx, frag):
        """Determine whether the passed fragment is the end of the accumulated
        text, and if not add it to the gathered text of this parser."""
        m = self._end_regex.search(frag.string)
        if m:
            return True
        else:
            # if none already exists, force whitespace at line breaks
            if self.text[-1] != " ":
                self.text += " "
            self.text += frag.string
        return False

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

    def __str__(self):
        s = ""
        for f in self.frags:
            s += f"{f}\n"
        return s

    def single_pass(self, parser, charsheet, offset):
        logging.debug(
            "Document.single_pass starting on parser %s with offset %d",
            parser.name,
            offset,
        )
        accum = False
        end_accum = False
        for idx, frag in enumerate(self.frags[offset:], offset):
            # print(f"enumerate: idx: {idx} frag: {frag}")
            if accum:
                # We have already matched and are accumulating
                end_accum = parser.accumulate(idx, frag)
                if end_accum:
                    # print("accum actuate")
                    parser.actuate(charsheet)
                    # Returned index needs to be last of the matching lines for this pass.
                    return idx - 1
                else:
                    frag.register_match(parser.name)
            else:
                # Not accumulating (yet or at all)
                match = parser.match(idx, frag)
                if match:
                    logging.debug(
                        "Document.single_pass %s match at idx %d / frag %s",
                        parser,
                        idx,
                        frag.string,
                    )
                    frag.register_match(parser.name)
                    if parser.accumulater:
                        accum = True
                        continue
                    # print("non-accum actuate")
                    parser.actuate(charsheet)
                    if parser.bam:
                        remainder = parser.split(frag)
                        if remainder:
                            self.frags = (
                                self.frags[0 : idx + 1]
                                + [remainder]
                                + self.frags[idx + 1 :]
                            )

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
                print(f"Warning: No text matched parser {parser.name}")
