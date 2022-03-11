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

    def __str__(self):
        if self.matched:
            return f"'{self.string}' - Matched by {self.matcher}"
        else:
            return f"'{self.string}' - Unmatched"


class Parser:
    def __init__(
        self, name, actuator, index=None, regex=None, accumulater=False, bam=False
    ):
        self.name = name
        self._actuator = actuator
        self._index = index
        self._regex = regex
        self._rematch = None
        self.accumulater = accumulater
        # Break after match
        self.bam = bam

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
                self.text = m.group(0)
                return True
        return False

    def actuate(self, charsheet):
        self._actuator(charsheet, text=self.text, rematch=self._rematch)


class Document:
    def __init__(self, strarray):
        self.frags = []
        for s in strarray:
            self.frags.append(Fragment(s))

    def __str__(self):
        s = ""
        for f in self.frags:
            s += f"{f}\n"
        return s

    def parse(self, parsers, charsheet):
        for parser in parsers:
            for idx, frag in enumerate(self.frags):
                match = parser.match(idx, frag)
                if match:
                    frag.register_match(parser.name)
                    # TODO: handle accumulation, BAM
                    parser.actuate(charsheet)
                    break
