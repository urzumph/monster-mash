from . import utils
import logging
import re

# Regular expression reusable fragments
NUMBER_OR_DASH = "[–—\-\dØ]"
ALIGNMENT = "(?:[CNL][GNE])|N"
BONUS_OR_DASH = "[\+\-]?[\d\—Ø]+"
DIE_SET = "(\d+)d\d+[+-–]?\d*"


# Pre-defined regular expressions
RE_SEMICOLON = re.compile(";")
SKILL_SPLIT = re.compile("^\s*(.+?)\s*([+\-]\d+)[,;]?\s*")
SQUARES = re.compile("\s*\(\d+ squares\)")
EMPTY_LINE = re.compile("^\s*$")
COLON = re.compile(":")

# Functions


def re_first(key):
    def assign_first(charsheet, rematch, **kwargs):
        charsheet[key] = rematch.group(1)

    return assign_first


def ac(charsheet, rematch, **kwargs):
    charsheet["ac"]["base"] = rematch.group(1)
    charsheet["ac"]["touch"] = rematch.group(2)
    charsheet["ac"]["flat"] = rematch.group(3)


def saves(charsheet, rematch, **kwargs):
    charsheet["saves"]["fort"] = rematch.group(1)
    charsheet["saves"]["ref"] = rematch.group(2)
    charsheet["saves"]["will"] = rematch.group(3)


def abilities(charsheet, rematch, **kwargs):
    charsheet["abilities"]["str"] = utils.maybe_int(rematch.group(1))
    charsheet["abilities"]["dex"] = utils.maybe_int(rematch.group(2))
    charsheet["abilities"]["con"] = utils.maybe_int(rematch.group(3))
    charsheet["abilities"]["int"] = utils.maybe_int(rematch.group(4))
    charsheet["abilities"]["wis"] = utils.maybe_int(rematch.group(5))
    charsheet["abilities"]["cha"] = utils.maybe_int(rematch.group(6))


def bab(charsheet, rematch, **kwargs):
    charsheet["bab"] = utils.maybe_int(rematch.group(1))
    charsheet["grapple"] = utils.maybe_int(rematch.group(2))


def space(charsheet, rematch, **kwargs):
    charsheet["space"] = rematch.group(1)
    charsheet["reach"] = rematch.group(2)


def inner_skills(charsheet, text, **kwargs):
    logging.debug(f"shared.inner_skills(charsheet, '{text}')")
    rxi = utils.RegexIter(text, SKILL_SPLIT)
    for m in iter(rxi):
        charsheet["skills"][m.group(1)] = m.group(2)


def skills(charsheet, rematch, **kwargs):
    inner_skills(charsheet, rematch.group(1))


def speed(charsheet, rematch, **kwargs):
    charsheet["speed"] = SQUARES.sub("", rematch.group(1))


def discard(charsheet, text, **kwargs):
    logging.debug("shared.discard: discarding '%s'", text)


def cotsq_space(charsheet, rematch, **kwargs):
    first = int(rematch.group(1))
    second = int(rematch.group(2))
    charsheet["space"] = max(first, second)
    charsheet["reach"] = utils.maybe_int(rematch.group(3))
