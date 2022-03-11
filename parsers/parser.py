#!/usr/bin/python


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
    def __init__(self, name, actuator, index=None, accumulater=False, bam=False):
        self.name = name
        self._actuator = actuator
        self._index = index
        self.accumulater = accumulater
        # Break after match
        self.bam = bam

    def match(self, idx, frag):
        self.text = ""
        if self._index is not None:
            if idx == self._index:
                self.text = frag.string
                return True
        return False

    def actuate(self, charsheet):
        self._actuator(self.text, charsheet)


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
