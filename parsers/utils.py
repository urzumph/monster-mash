class RegexIter:
    def __init__(self, string, regex):
        self.remainder = string
        self.regex = regex

    def __iter__(self):
        return self

    def __next__(self):
        m = self.regex.match(self.remainder)
        if not m:
            raise StopIteration
        else:
            self.remainder = self.remainder[len(m.group(0)) :]
            return m
