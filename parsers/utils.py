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


def prechomp_regex(string, regex):
    m = regex.match(string)
    if not m:
        return string
    else:
        return string[len(m.group(0)) :]


def split_from(string, regex):
    m = regex.search(string)
    if m:
        return string[0 : m.start()], string[m.start() :]
    else:
        return string, ""


def maybe_int(text):
    toret = text
    try:
        toret = int(text)
    except ValueError:
        pass
    return toret
