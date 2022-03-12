#!/usr/bin/python
# TODO: Proper logging to avoid print statements


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
        if self._index is not None:
            if idx == self._index:
                self.text = frag.string
                return True
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
                return True
        return False

    def actuate(self, charsheet):
        self._actuator(charsheet, text=self.text, rematch=self._rematch)

    def split(self, frag):
        """Given a fragment which this parser match()'d,
        modify the fragment to include only the matched text
        from the match() and return a new fragment containing
        all of the remaining text."""
        end = self._rematch.end()
        if end < len(frag.string):
            newfrag = Fragment(frag.string[end:])
            frag.string = frag.string[0:end]
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

    def parse(self, parsers, charsheet):
        for parser in parsers:
            accum = False
            end_accum = False
            for idx, frag in enumerate(self.frags):
                if accum:
                    # We have already matched and are accumulating
                    end_accum = parser.accumulate(idx, frag)
                    if end_accum:
                        parser.actuate(charsheet)
                        break
                    else:
                        frag.register_match(parser.name)
                else:
                    # Not accumulating (yet or at all)
                    match = parser.match(idx, frag)
                    if match:
                        frag.register_match(parser.name)
                        if parser.accumulater:
                            accum = True
                            continue
                        parser.actuate(charsheet)
                        if parser.bam:
                            remainder = parser.split(frag)
                            if remainder:
                                self.frags = (
                                    self.frags[0 : idx + 1]
                                    + [remainder]
                                    + self.frags[idx + 1 :]
                                )

                        break
            else:
                if accum:
                    # We accumulated all the way to the end of the document.
                    parser.actuate(charsheet)
                else:
                    print(f"Warning: No text matched parser {parser.name}")
