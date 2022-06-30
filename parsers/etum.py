import re
from . import parser
from . import utils
from . import shared

# Init +0; Senses darkvision 60 ft., scent; Listen +11, Spot
# +11
# Languages Giant, Common
init_re = re.compile("^\s*Init ([+\-\–]\d+);")
senses_re = re.compile("^\s*Senses ")
senses_end_re = re.compile("(;|Listen|Spot)")
senses_accum_end_re = re.compile("^(Languages|AC)")
lang_re = re.compile("^Languages ")
# Skills Intimidate +3, Listen +11, Search +4, Spot +11
skills_re = re.compile("^\s*Skills (.*)")
# Melee mwk greataxe +11/+6 (3d6+7/×3) and
# gore +5 (1d8+3)
# Space 10 ft.; Reach 10 ft.
attack_re = re.compile("^\s*(Melee |Ranged )")
# Space 10 ft.; Reach 10 ft.
space_re = re.compile("^\s*Space ([\d\-\/]+) ft.; Reach ([\d]+)")
# Feats Great Fortitude, Power Attack, Track
feats_re = re.compile("^\s*Feats ")
# Confusing Gaze (Su) Confusion as the spell, 30 feet, caster
# level 12th, Will DC 16 negates.
special_re = re.compile("^(.+?) \((Su|Ex)\) ")
# Base Atk +6; Grp +15
bab_re = re.compile(f"^\s*Base Atk [+]?([\-\d]+); Grp [+]?({shared.NUMBER_OR_DASH}+)")


# Ster Longhorn, Minotaur Chief
def name(charsheet, text, **kwargs):
    charsheet["name"] = text.strip()


# CE Large monstrous humanoid
mtype_re = re.compile(
    f"\s*({shared.ALIGNMENT}) (Fine|Diminutive|Tiny|Small|Medium|Large|Huge|Gargantuan|Colossal) (.*)"
)


# hp 45 (6 HD)
hp_re = re.compile("\s*hp (\d+) (?:each )?\((\d+) HD\)\s*")


def hp(charsheet, rematch, **kwargs):
    charsheet["hp"] = int(rematch.group(1))
    charsheet["hd"] = int(rematch.group(2))


dr_re = re.compile("[;,\s]*(DR \d+/.*)$")


def mtype(charsheet, rematch, **kwargs):
    charsheet["alignment"] = rematch.group(1)
    charsheet["size"] = rematch.group(2)
    charsheet["type"] = rematch.group(3).strip()


def senses(charsheet, text, **kwargs):
    text = utils.prechomp_regex(text, senses_re)
    senses, remainder = utils.split_from(text, senses_end_re)
    charsheet["senses"] = senses.rstrip(", ")
    remainder = remainder.lstrip("; ")
    remainder = remainder.replace("\n", " ")
    shared.inner_skills(charsheet, remainder)


# AC 19, touch 13, flat-footed —; natural cunning
ac_re = re.compile("^\s*AC ([\d\—]+), touch ([\d\—]+), fl\s*at-footed ([\d\—]+)")


# Fort +6, Ref +5, Will +5
saves_re = re.compile(
    f"^\s*Fort ({shared.BONUS_OR_DASH}), Ref ({shared.BONUS_OR_DASH}), Will ({shared.BONUS_OR_DASH})"
)


def attack(charsheet, text, **kwargs):
    text = utils.prechomp_regex(text, attack_re)
    charsheet["attack"] = text
    charsheet["fullAttack"] = text


# Abilities Str 21, Dex 10, Con 15, Int 10, Wis 10, Cha 8
abilities_re = re.compile(
    f"^\s*Abilities Str ({shared.NUMBER_OR_DASH}+), Dex ({shared.NUMBER_OR_DASH}+), Con ({shared.NUMBER_OR_DASH}+), Int ({shared.NUMBER_OR_DASH}+), Wis ({shared.NUMBER_OR_DASH}+), Cha ({shared.NUMBER_OR_DASH}+)"
)


def feats(charsheet, text, **kwargs):
    text = utils.prechomp_regex(text, feats_re)
    charsheet["feats"] = text


# Speed 30 ft. (6 squares)
speed_re = re.compile("^\s*Speed (.*)")


def special(charsheet, text, rematch, **kwargs):
    mname = rematch.group(1)
    move = {"name": mname, "type": rematch.group(2)}
    desc = utils.prechomp_regex(text, special_re)
    desc = desc.rstrip()
    move["desc"] = desc
    charsheet["moves"][mname] = move


parsers = [
    parser.Parser("etum_name", name, index=0),
    parser.Parser("etum_hp", hp, regex=hp_re, bam=True),
    parser.Parser("etum_dr", shared.re_first("sq"), regex=dr_re),
    parser.Parser("etum_type", mtype, regex=mtype_re),
    parser.Parser("etum_init", shared.re_first("init"), regex=init_re, bam=True),
    parser.Parser(
        "etum_senses",
        senses,
        regex=senses_re,
        accumulate=True,
        accum_end_regex=senses_accum_end_re,
    ),
    parser.Parser("etum_ac", shared.ac, regex=ac_re),
    parser.Parser("etum_saves", shared.saves, regex=saves_re),
    parser.Parser(
        "etum_attack",
        attack,
        regex=attack_re,
        accumulate=True,
        accum_end_regex=space_re,
    ),
    parser.Parser("etum_space", shared.space, regex=space_re),
    parser.Parser("etum_bab", shared.bab, regex=bab_re),
    parser.Parser("etum_abilities", shared.abilities, regex=abilities_re),
    parser.Parser(
        "etum_feats",
        feats,
        regex=feats_re,
        accumulate=True,
        accum_end_regex=skills_re,
    ),
    parser.Parser("etum_skills", shared.skills, regex=skills_re),
    parser.Parser("etum_speed", shared.speed, regex=speed_re),
    parser.Parser(
        "etum_special",
        special,
        regex=special_re,
        accumulate=True,
        accum_end_regex=special_re,
    ),
]
