import re
from . import parser

# Ster Longhorn, Minotaur Chief
def name(charsheet, text, **kwargs):
    charsheet["name"] = text.strip()


# CE Large monstrous humanoid
mtype_re = re.compile(
    "\s*((?:[CNL][GNE])|N) (Fine|Diminutive|Tiny|Small|Medium|Large|Huge|Gargantuan|Colossal) (.*)"
)


def mtype(charsheet, rematch, **kwargs):
    charsheet["alignment"] = rematch.group(1)
    charsheet["size"] = rematch.group(2)
    charsheet["type"] = rematch.group(3).strip()


# AC 19, touch 13, flat-footed —; natural cunning
ac_re = re.compile("^\s*AC ([\d\—]+), touch ([\d\—]+), flat-footed ([\d\—]+)")


def ac(charsheet, rematch, **kwargs):
    charsheet["ac"]["base"] = rematch.group(1)
    charsheet["ac"]["touch"] = rematch.group(2)
    charsheet["ac"]["flat"] = rematch.group(3)


# Fort +6, Ref +5, Will +5
saves_re = re.compile(
    "^\s*Fort ([+\-]?[\d\—]+), Ref ([+\-]?[\d\—]+), Will ([+\-]?[\d\—]+)"
)


def saves(charsheet, rematch, **kwargs):
    charsheet["saves"]["fort"] = rematch.group(1)
    charsheet["saves"]["ref"] = rematch.group(2)
    charsheet["saves"]["will"] = rematch.group(3)


# Space 10 ft.; Reach 10 ft.
space_re = re.compile("^\s*Space ([\d]+) ft.; Reach ([\d]+)")


def space(charsheet, rematch, **kwargs):
    charsheet["space"] = int(rematch.group(1))
    charsheet["reach"] = int(rematch.group(2))


# Base Atk +6; Grp +15
bab_re = re.compile("^\s*Base Atk [+]?([\-\d]+); Grp [+]?([\-\d]+)")


def bab(charsheet, rematch, **kwargs):
    charsheet["bab"] = int(rematch.group(1))
    charsheet["grapple"] = int(rematch.group(2))


# Abilities Str 21, Dex 10, Con 15, Int 10, Wis 10, Cha 8
abilities_re = re.compile(
    "^\s*Abilities Str (\d+), Dex (\d+), Con (\d+), Int (\d+), Wis (\d+), Cha (\d+)"
)


def abilities(charsheet, rematch, **kwargs):
    charsheet["abilities"]["str"] = int(rematch.group(1))
    charsheet["abilities"]["dex"] = int(rematch.group(2))
    charsheet["abilities"]["con"] = int(rematch.group(3))
    charsheet["abilities"]["int"] = int(rematch.group(4))
    charsheet["abilities"]["wis"] = int(rematch.group(5))
    charsheet["abilities"]["cha"] = int(rematch.group(6))


# Speed 30 ft. (6 squares)
speed_re = re.compile("^\s*Speed (.*)")
squares_re = re.compile("\s*\(\d+ squares\)")


def speed(charsheet, rematch, **kwargs):
    charsheet["speed"] = squares_re.sub("", rematch.group(1))


parsers = [
    parser.Parser("etum_name", name, index=0),
    parser.Parser("etum_type", mtype, regex=mtype_re),
    parser.Parser("etum_ac", ac, regex=ac_re),
    parser.Parser("etum_saves", saves, regex=saves_re),
    parser.Parser("etum_space", space, regex=space_re),
    parser.Parser("etum_bab", bab, regex=bab_re),
    parser.Parser("etum_abilities", abilities, regex=abilities_re),
]
