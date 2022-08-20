import re
import logging
from . import parser
from . import utils
from . import shared

line_re = re.compile("^\s*[^:]+:\s*")

type_re = re.compile(
    "^Size/Type:\t(Fine|Diminutive|Tiny|Small|Medium|Large|Huge|Gargantuan|Colossal)\s+(.+)"
)
alt_type_re = re.compile(
    "^\s*(Fine|Diminutive|Tiny|Small|Medium|Large|Huge|Gargantuan|Colossal)(?:-[Ss]ize)?\s+(.+)"
)

hphd_re = re.compile(f"^Hit Dice:\s*{shared.DIE_SET}[^\(]*\((?P<hp>\d+) hp\)")

init_re = re.compile("^\s*Initiative:\s*([+-]?\d+)")

speed_re = re.compile("^\s*Speed:\s*(.+)")

ac_re = re.compile(
    f"^\s*(?:Armor Class|AC):\s*({shared.NUMBER_OR_DASH}+) \([^\)]*\),\s*touch\s*({shared.NUMBER_OR_DASH}+),\s*flat-footed\s*({shared.NUMBER_OR_DASH}+)"
)

bab_re = re.compile(
    f"^\s*Base Attack/Grapple:\s+[+]?([\-\d]+)/[+]?({shared.NUMBER_OR_DASH}+)"
)

atk_re = re.compile("^\s*Attacks?:\s*(.+)")
full_atk_re = re.compile("^\s*Full Attack:\s*(.+)")
damage_re = re.compile("^\s*Damage:\s*(.+)")

space_re = re.compile("^\s*Face/Reach:\s*(\d+)\s+ft\.\s+by\s+(\d+)\s+ft\./(\d+)\s+ft\.")

special_atk_re = re.compile("^\s*Special Attacks:\s*")
special_qual_re = re.compile("^\s*Special Qualities:\s*")

saves_re = re.compile(
    f"^\s*Saves:\s*Fort\s+({shared.BONUS_OR_DASH}),\s+Ref\s+({shared.BONUS_OR_DASH}),\s+Will\s+({shared.BONUS_OR_DASH})"
)

abilities_re = re.compile(
    f"^\s*Abilities:\s*Str\s+({shared.NUMBER_OR_DASH}+),\s+Dex ({shared.NUMBER_OR_DASH}+),\s+Con ({shared.NUMBER_OR_DASH}+),\s+Int ({shared.NUMBER_OR_DASH}+),\s+Wis ({shared.NUMBER_OR_DASH}+),\s+Cha ({shared.NUMBER_OR_DASH}+)"
)

skills_re = re.compile("^\s*Skills:\s*")
skill_verify_re = re.compile("^\s*(.{1,15})\s*([+\-]\d+),\s*")
feats_re = re.compile("^\s*Feats:\s*")

generic_moves = r"(.+?) \((Su|Ex|Traits)\)"
generic_moves_re = re.compile(generic_moves)
spells_known = r".*? Spells Known \([^\)]+\)"
moves_re = re.compile(
    f"^(?:{generic_moves}|{spells_known}|Spells|Spell-Like Abilities|Skills):\s*"
)

# Alignment:	Always chaotic evil
alignment_re = re.compile("^\s*Alignment:\s*(.*)")


def name(charsheet, text, **kwargs):
    charsheet["name"] = text.strip()


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


def add_move(charsheet, name, typ, raw):
    move = {"name": name, "type": typ}
    desc = raw.strip()
    move["desc"] = utils.undo_word_wrap(desc)
    charsheet["moves"][name] = move


leading_junk_re = re.compile(r":\s*")


def moves(charsheet, text, rematch, **kwargs):
    raw = utils.prechomp_regex(text, moves_re)
    raw = utils.prechomp_regex(raw, leading_junk_re)
    if skill_verify_re.match(raw):
        return
    gm = generic_moves_re.match(text)
    if gm:
        add_move(charsheet, gm.group(1), gm.group(2), raw)
    else:
        add_move(
            charsheet,
            utils.postchomp_regex(rematch.group(0), leading_junk_re),
            "Misc",
            raw,
        )


def skills(charsheet, text, **kwargs):
    to_parse = utils.prechomp_regex(text, skills_re)
    to_parse = utils.undo_word_wrap(to_parse)
    if not skill_verify_re.match(to_parse):
        return
    shared.inner_skills(charsheet, to_parse)


def feats(charsheet, text, **kwargs):
    to_store = utils.prechomp_regex(text, feats_re)
    to_store = utils.undo_word_wrap(to_store)
    charsheet["feats"] = to_store


def damage(charsheet, rematch, **kwargs):
    charsheet["attack"] += " (" + rematch.group(1) + ")"


def saq(charsheet, text, rematch, **kwargs):
    if "attack" in rematch.group(0).lower():
        index = "sa"
        to_store = utils.prechomp_regex(text, special_atk_re)
    else:
        index = "sq"
        to_store = utils.prechomp_regex(text, special_qual_re)
    to_store = utils.undo_word_wrap(to_store)
    to_store = to_store.rstrip(";")
    charsheet[index] = to_store


parsers = [
    parser.Parser("cotsq_long_name", name, index=0),
    parser.Parser("cotsq_long_type", mtype, regex=type_re),
    parser.Parser("cotsq_long_alt_type", mtype, index=1, regex=alt_type_re),
    parser.Parser("cotsq_long_hphd", hphd, regex=hphd_re),
    parser.Parser("cotsq_long_init", shared.re_first("init"), regex=init_re),
    parser.Parser("cotsq_long_speed", shared.speed, regex=speed_re),
    parser.Parser("cotsq_long_ac", shared.ac, regex=ac_re, line_dewrap=True),
    parser.Parser("cotsq_long_bab", shared.bab, regex=bab_re),
    parser.Parser("cotsq_long_atk", shared.re_first("attack"), regex=atk_re),
    parser.Parser("cotsq_long_dmg", damage, regex=damage_re),
    parser.Parser(
        "cotsq_long_full_atk", shared.re_first("fullAttack"), regex=full_atk_re
    ),
    parser.Parser("cotsq_long_space", shared.cotsq_space, regex=space_re),
    parser.Parser(
        "cotsq_long_special_atk",
        saq,
        regex=special_atk_re,
        accumulate=True,
        accum_end_regex=line_re,
    ),
    parser.Parser(
        "cotsq_long_special_qual",
        saq,
        regex=special_qual_re,
        accumulate=True,
        accum_end_regex=line_re,
    ),
    parser.Parser("cotsq_long_saves", shared.saves, regex=saves_re),
    parser.Parser("cotsq_long_abilities", shared.abilities, regex=abilities_re),
    parser.Parser(
        "cotsq_long_skills",
        skills,
        regex=skills_re,
        accumulate=True,
        accum_end_regex=line_re,
    ),
    parser.Parser(
        "cotsq_long_feats",
        feats,
        regex=feats_re,
        accumulate=True,
        accum_end_regex=line_re,
    ),
    parser.Parser("cotsq_long_alignment", alignment, regex=alignment_re),
    parser.Parser(
        "cotsq_long_moves",
        moves,
        regex=moves_re,
        accumulate=True,
        accum_end_regex=line_re,
    ),
]
