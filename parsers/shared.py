from . import utils
import re

# Regular expression reusable fragments
NUMBER_OR_DASH = "[–—\-\d]"
ALIGNMENT = "(?:[CNL][GNE])|N"
BONUS_OR_DASH = "[+\-]?[\d\—]+"
DIE_SET = "(\d+)d\d+[+-]?\d*"

# Pre-defined regular expressions
RE_SEMICOLON = re.compile(";")

# Functions


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
