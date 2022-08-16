import re


class RegexIter:
    def __init__(self, string, regex, junk=[]):
        self.remainder = string
        self.regex = regex
        self.junk = junk

    def __iter__(self):
        return self

    def __next__(self):
        m = self.regex.match(self.remainder)
        if not m:
            # Check for junk
            for j in self.junk:
                jm = j.match(self.remainder)
                if jm:
                    # Found junk
                    self.remainder = self.remainder[len(jm.group(0)) :]
                    return self.__next__()
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


def postchomp_regex(string, regex):
    m = regex.search(string)
    if not m:
        return string
    else:
        return string[: -len(m.group(0))]


def split_from(string, regex):
    m = regex.search(string)
    if m:
        return string[0 : m.start()], string[m.start() :]
    else:
        return string, ""


def maybe_int(text):
    toret = text
    toparse = text
    if isinstance(toparse, str):
        toparse = re.sub("[–—]", "-", toparse)
        toparse = toparse.replace("Ø", "0")
    try:
        toret = int(toparse)
    except ValueError:
        pass
    return toret


word_wrap = re.compile("(\w)- ")


def undo_word_wrap(text):
    text = text.replace("\n", "")
    return word_wrap.sub("\g<1>", text)
