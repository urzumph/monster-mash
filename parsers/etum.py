import re
from . import parser
from . import utils

# Ster Longhorn, Minotaur Chief
def name(charsheet, text, **kwargs):
    charsheet["name"] = text.strip()


# CE Large monstrous humanoid
mtype_re = re.compile(
    "\s*((?:[CNL][GNE])|N) (Fine|Diminutive|Tiny|Small|Medium|Large|Huge|Gargantuan|Colossal) (.*)"
)


# hp 45 (6 HD)
hp_re = re.compile("\s*hp (\d+) (?:each )?\((\d+) HD\)\s*")


def hp(charsheet, rematch, **kwargs):
    charsheet["hp"] = int(rematch.group(1))
    charsheet["hd"] = int(rematch.group(2))


dr_re = re.compile("[;,\s]*(DR \d+/.*)$")


def dr(charsheet, rematch, **kwargs):
    charsheet["sq"] = rematch.group(1)


def mtype(charsheet, rematch, **kwargs):
    charsheet["alignment"] = rematch.group(1)
    charsheet["size"] = rematch.group(2)
    charsheet["type"] = rematch.group(3).strip()


# Init +0; Senses darkvision 60 ft., scent; Listen +11, Spot
# +11
# Languages Giant, Common
init_re = re.compile("^\s*Init ([+\-\–]\d+);")


def init(charsheet, rematch, **kwargs):
    charsheet["init"] = rematch.group(1)


# TODO: Needs either to be re-written to accumulate
# and set skills as well, or to have some kind of
# match-immediately-after matcher
# senses_re = re.compile("^\s*Senses (.+)(?!(;|Listen|Spot))")

# def senses(charsheet, rematch, **kwargs):
#    senses = rematch.group(1)
#    charsheet["senses"] = senses.rstrip(", ")

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


# Skills Intimidate +3, Listen +11, Search +4, Spot +11
skills_re = re.compile("^\s*Skills (.*)")
# Listen +11, Spot +11
skill_split_re = re.compile("^\s*(\w+) ([+\-]\d+)[,;]?\s*")


def skills(charsheet, rematch, **kwargs):
    text = rematch.group(1)
    rxi = utils.RegexIter(text, skill_split_re)
    for m in iter(rxi):
        charsheet["skills"][m.group(1)] = m.group(2)
    print("Left over from skills: ", rxi.remainder)


# Speed 30 ft. (6 squares)
speed_re = re.compile("^\s*Speed (.*)")
squares_re = re.compile("\s*\(\d+ squares\)")


def speed(charsheet, rematch, **kwargs):
    charsheet["speed"] = squares_re.sub("", rematch.group(1))


parsers = [
    parser.Parser("etum_name", name, index=0),
    parser.Parser("etum_hp", hp, regex=hp_re, bam=True),
    parser.Parser("etum_dr", dr, regex=dr_re),
    parser.Parser("etum_type", mtype, regex=mtype_re),
    parser.Parser("etum_init", init, regex=init_re, bam=True),
    parser.Parser("etum_ac", ac, regex=ac_re),
    parser.Parser("etum_saves", saves, regex=saves_re),
    parser.Parser("etum_space", space, regex=space_re),
    parser.Parser("etum_bab", bab, regex=bab_re),
    parser.Parser("etum_abilities", abilities, regex=abilities_re),
    parser.Parser("etum_skills", skills, regex=skills_re),
    parser.Parser("etum_speed", speed, regex=speed_re),
]
