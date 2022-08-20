import re
import logging
from . import parser
from . import utils
from . import shared


# Drider click to see monster
name_toremove = re.compile("\s*click to see monster\s*$")
# Size/Type:	Large Aberration
# Medium-Size Undead
type_re = re.compile(
    "^Size/Type:\t(Fine|Diminutive|Tiny|Small|Medium|Large|Huge|Gargantuan|Colossal)\s+(.+)"
)
alt_type_re = re.compile(
    "^\s*(Fine|Diminutive|Tiny|Small|Medium|Large|Huge|Gargantuan|Colossal)(?:-[Ss]ize)?\s+(.+)"
)

# Hit Dice:	6d8+18 (45 hp)
hphd_re = re.compile(f"^Hit Dice:\s*{shared.DIE_SET}[^\(]*\((?P<hp>\d+) hp\)")

# Initiative:	+2
init_re = re.compile("^\s*Initiative:\s*([+-]?\d+)")

# Speed:	30 ft. (6 squares), climb 15 ft.
speed_re = re.compile("^\s*Speed:\s*(.+)")

# Armor Class:	17 (-1 size, +2 Dex, +6 natural), touch 11, flat-footed 15
ac_re = re.compile(
    f"^\s*(?:Armor Class|AC):\s*({shared.NUMBER_OR_DASH}+) \([^\)]*\),\s*touch\s*({shared.NUMBER_OR_DASH}+),\s*flat-footed\s*({shared.NUMBER_OR_DASH}+)"
)

# Base Attack/Grapple:	+4/+10
bab_re = re.compile(
    f"^\s*Base Attack/Grapple:\s+[+]?([\-\d]+)/[+]?({shared.NUMBER_OR_DASH}+)"
)

# Attack:	Dagger +5 melee (1d6+2/19-20) or bite +6 melee (1d4+1 plus poison) or shortbow +5 ranged (1d8/×3)
# Full Attack:	2 daggers +3 melee (1d6+2/19-20, 1d6+1/19-20) and bite +1 melee (1d4+1 plus poison); or shortbow +5 ranged (1d8/×3)

atk_re = re.compile("^\s*Attacks?:\s*(.+)")
full_atk_re = re.compile("^\s*Full Attack:\s*(.+)")

# Space/Reach:	10 ft./5 ft.
space_re = re.compile("^\s*Space/Reach:\s*([\d\-\/]+) ft./([\d]+) ft.")

# Special Attacks:	Spells, spell-like abilities, poison
# Special Qualities:	Darkvision 60 ft., spell resistance 17

special_atk_re = re.compile("^\s*Special Attacks:\s*(.+)")
special_qual_re = re.compile("^\s*Special Qualities:\s*(.+)")

# Saves:	Fort +5, Ref +4, Will +8
saves_re = re.compile(
    f"^\s*Saves:\s*Fort\s+({shared.BONUS_OR_DASH}),\s+Ref\s+({shared.BONUS_OR_DASH}),\s+Will\s+({shared.BONUS_OR_DASH})"
)

# Abilities:	Str 15, Dex 15, Con 16, Int 15, Wis 16, Cha 16
abilities_re = re.compile(
    f"^\s*Abilities:\s*Str\s+({shared.NUMBER_OR_DASH}+),\s+Dex ({shared.NUMBER_OR_DASH}+),\s+Con ({shared.NUMBER_OR_DASH}+),\s+Int ({shared.NUMBER_OR_DASH}+),\s+Wis ({shared.NUMBER_OR_DASH}+),\s+Cha ({shared.NUMBER_OR_DASH}+)"
)

# Skills:	Climb +14, Concentration +9, Hide +10, Listen +9, Move Silently +12, Spot +9
skills_re = re.compile("^\s*Skills:\s*(.*)")
# Feats:	Combat Casting, Two-Weapon Fighting, Weapon Focus (bite)
feats_re = re.compile("^\s*Feats:\s*(.*)")

generic_moves = r"(.+?) \(?(Su|Ex|Traits)\)?"
generic_moves_re = re.compile(generic_moves)
spells_known = r".*? Spells Known \([^\)]+\)"
moves_re = re.compile(
    f"^(?:{generic_moves}|{spells_known}|Spells|Spell-Like Abilities|Skills)"
)

# Alignment:	Always chaotic evil
alignment_re = re.compile("^\s*Alignment:\s*(.*)")


def name(charsheet, text, **kwargs):
    charsheet["name"] = utils.postchomp_regex(text, name_toremove)


def mtype(charsheet, rematch, **kwargs):
    charsheet["type"] = rematch.group(2)
    charsheet["size"] = rematch.group(1)


def hphd(charsheet, rematch, **kwargs):
    charsheet["hd"] = int(rematch.group(1))
    charsheet["hp"] = int(rematch.group("hp"))


def alignment(charsheet, rematch, **kwargs):
    CL = "N"
    GE = "N"
    desc = rematch.group(1)

    if "chaotic" in desc:
        CL = "C"
    elif "lawful" in desc:
        CL = "L"

    if "good" in desc:
        GE = "G"
    elif "evil" in desc:
        GE = "E"

    res = CL + GE
    if res == "NN":
        charsheet["alignment"] = "N"
    else:
        charsheet["alignment"] = res


def moves(charsheet, text, rematch, **kwargs):
    move = {"name": rematch.group(0), "type": "Misc"}

    gm = generic_moves_re.match(text)
    if gm:
        move["name"] = gm.group(1)
        move["type"] = gm.group(2)

    desc = utils.prechomp_regex(text, moves_re)
    desc = desc.strip()
    move["desc"] = desc
    mname = move["name"]
    charsheet["moves"][mname] = move


parsers = [
    parser.Parser("srd_name", name, index=0),
    parser.Parser("srd_type", mtype, regex=type_re),
    parser.Parser("srd_alt_type", mtype, index=1, regex=alt_type_re),
    parser.Parser("srd_hphd", hphd, regex=hphd_re),
    parser.Parser("srd_init", shared.re_first("init"), regex=init_re),
    parser.Parser("srd_speed", shared.speed, regex=speed_re),
    parser.Parser("srd_ac", shared.ac, regex=ac_re, line_dewrap=True),
    parser.Parser("srd_bab", shared.bab, regex=bab_re),
    parser.Parser("srd_atk", shared.re_first("attack"), regex=atk_re),
    parser.Parser("srd_full_atk", shared.re_first("fullAttack"), regex=full_atk_re),
    parser.Parser("srd_space", shared.space, regex=space_re),
    parser.Parser("srd_special_atk", shared.re_first("sa"), regex=special_atk_re),
    parser.Parser("srd_special_qual", shared.re_first("sq"), regex=special_qual_re),
    parser.Parser("srd_saves", shared.saves, regex=saves_re),
    parser.Parser("srd_abilities", shared.abilities, regex=abilities_re),
    parser.Parser("srd_skills", shared.skills, regex=skills_re),
    parser.Parser("srd_feats", shared.re_first("feats"), regex=feats_re),
    parser.Parser("srd_alignment", alignment, regex=alignment_re),
    parser.Parser(
        "srd_moves",
        moves,
        regex=moves_re,
        accumulate=True,
        accum_end_regex=shared.EMPTY_LINE,
    ),
]
