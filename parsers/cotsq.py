import re
import logging
from . import parser
from . import utils
from . import shared

# Chahir: Male human vampire Sor8; CR 10;
name_re = re.compile("^([^:]+): (([^;]+\d[^;]*); )?(CR \d+;)?")
# Medium-size outsider (chaotic, evil);
# Medium-size undead;
type_re = re.compile(
    "^\s*(Fine|Diminutive|Tiny|Small|Medium|Large|Huge|Gargantuan|Colossal)(?:-size)?\s+([^;]+);"
)
# HD 10d8+10;
# HD 3d8+9 plus 4d10+12; #TODO: Fix HD count
hd_re = re.compile(f"^\s*HD\s*{shared.DIE_SET}( plus {shared.DIE_SET})*;")
# hp 66;
# hp 69, 62;
hp_re = re.compile("^\s*hp\s*(\d+)[^;]*;")
# Init +8;
init_re = re.compile("^\s*Init\s*([+-]?\d+);")
# Spd 30 ft.;
speed_re = re.compile("^\s*Spd\s*([^;]+);")
# AC 23, touch 15, flat-footed 19;
ac_re = re.compile(
    f"^\s*AC\s*({shared.NUMBER_OR_DASH}+),\s*touch\s*({shared.NUMBER_OR_DASH}+),\s*flat-footed\s*({shared.NUMBER_OR_DASH}+)[^;]*;"
)

# AL CE; SV Fort +3, Ref +9, Will +11;
alignment_re = re.compile(f"^\s*AL\s*({shared.ALIGNMENT});")
saves_re = re.compile(
    f"^\s*SV\s*Fort\s+({shared.BONUS_OR_DASH}),\s+Ref\s+({shared.BONUS_OR_DASH}),\s+Will\s+({shared.BONUS_OR_DASH});"
)
# Str 14, Dex 18, Con —, Int 10, Wis 14, Cha 22.
abilities_re = re.compile(
    f"^\s*Str\s+({shared.NUMBER_OR_DASH}+),\s+Dex ({shared.NUMBER_OR_DASH}+),\s+Con ({shared.NUMBER_OR_DASH}+),\s+Int ({shared.NUMBER_OR_DASH}+),\s+Wis ({shared.NUMBER_OR_DASH}+),\s+Cha ({shared.NUMBER_OR_DASH}+)[\.;]"
)
moves_re = re.compile("^(.+?) \(?(Su|Ex|Traits)\)?:")

# Skills and Feats:
saf_re = re.compile("^\s*Skills and Feats:")
saf_end_re = re.compile("\.")
skill_split_re = re.compile("^,?\s*(\w+(?: [\(\)\w]+)?)\s+([+\-]\d+)")
skill_note_re = re.compile("\s*\([^\)]*\)")
feat_start_re = re.compile(";\s*")

# Atk
atk_re = re.compile("^\s*Atk (?!Options)")

# SA/SQ
saq_re = re.compile("^\s*(S[AQ])\s")
saq_end_re = re.compile(";")


def name(charsheet, rematch, **kwargs):
    charsheet["name"] = rematch.group(1)


def mtype(charsheet, rematch, **kwargs):
    charsheet["type"] = rematch.group(2)
    charsheet["size"] = rematch.group(1)


def hd(charsheet, rematch, **kwargs):
    charsheet["hd"] = int(rematch.group(1))


def hp(charsheet, rematch, **kwargs):
    charsheet["hp"] = int(rematch.group(1))


def init(charsheet, rematch, **kwargs):
    charsheet["init"] = rematch.group(1)


def speed(charsheet, rematch, **kwargs):
    charsheet["speed"] = rematch.group(1)


def alignment(charsheet, rematch, **kwargs):
    charsheet["alignment"] = rematch.group(1)


def saf(charsheet, text, **kwargs):
    to_parse = utils.prechomp_regex(text, saf_re)
    to_parse = utils.undo_word_wrap(to_parse)
    logging.debug("cotsq.saf: post-undo_word_wrap: %s", to_parse)
    rxi = utils.RegexIter(to_parse, skill_split_re, [skill_note_re])
    for m in iter(rxi):
        charsheet["skills"][m.group(1)] = m.group(2)
    to_parse = utils.prechomp_regex(rxi.remainder, feat_start_re)
    charsheet["feats"] = to_parse.rstrip(". ")


def atk(charsheet, text, **kwargs):
    txt = utils.prechomp_regex(text, atk_re)
    txt = utils.undo_word_wrap(txt)
    txt = txt.rstrip(";")
    charsheet["attack"] = txt
    charsheet["fullAttack"] = txt


def saq(charsheet, text, rematch, **kwargs):
    index = rematch.group(1).lower()
    fixed = utils.prechomp_regex(text, saq_re)
    fixed = utils.undo_word_wrap(fixed)
    fixed = fixed.rstrip(";")
    charsheet[index] = fixed


def moves(charsheet, text, rematch, **kwargs):
    mname = rematch.group(1)
    move = {"name": mname, "type": rematch.group(2)}
    desc = utils.prechomp_regex(text, moves_re)
    desc = desc.strip()
    move["desc"] = desc
    charsheet["moves"][mname] = move


parsers = [
    parser.Parser("cotsq_name", name, index=0, regex=name_re, bam=True),
    parser.Parser("cotsq_type", mtype, regex=type_re, bam=True, line_dewrap=True),
    parser.Parser("cotsq_hd", hd, regex=hd_re, bam=True, line_dewrap=True),
    parser.Parser("cotsq_hp", hp, regex=hp_re, bam=True, line_dewrap=True),
    parser.Parser("cotsq_init", init, regex=init_re, bam=True, line_dewrap=True),
    parser.Parser("cotsq_speed", speed, regex=speed_re, bam=True, line_dewrap=True),
    parser.Parser("cotsq_ac", shared.ac, regex=ac_re, bam=True, line_dewrap=True),
    parser.Parser(
        "cotsq_atk",
        atk,
        regex=atk_re,
        accumulate=True,
        accum_end_regex=shared.RE_SEMICOLON,
        accum_include_end=True,
        bam=True,
    ),
    parser.Parser(
        "cotsq_saq",
        saq,
        regex=saq_re,
        accumulate=True,
        accum_end_regex=saq_end_re,
        accum_include_end=True,
        bam=True,
    ),
    parser.Parser(
        "cotsq_alignment", alignment, regex=alignment_re, bam=True, line_dewrap=True
    ),
    parser.Parser(
        "cotsq_saves", shared.saves, regex=saves_re, bam=True, line_dewrap=True
    ),
    parser.Parser(
        "cotsq_abilities",
        shared.abilities,
        regex=abilities_re,
        bam=True,
        line_dewrap=True,
    ),
    parser.Parser(
        "cotsq_saf",
        saf,
        regex=saf_re,
        accumulate=True,
        accum_end_regex=saf_end_re,
        accum_include_end=True,
        bam=True,
    ),
    parser.Parser(
        "cotsq_moves",
        moves,
        regex=moves_re,
        accumulate=True,
        accum_end_regex=moves_re,
    ),
]
