import re
from . import parser
from . import utils
from . import shared

# Chahir: Male human vampire Sor8; CR 10;
name_re = re.compile("^([^:]+): (([^;]+); )?CR \d+;")
# Medium-size outsider (chaotic, evil);
# Medium-size undead;
type_re = re.compile(
    "^\s*(Fine|Diminutive|Tiny|Small|Medium|Large|Huge|Gargantuan|Colossal)(?:-size)? ([^;]+);"
)


def name(charsheet, rematch, **kwargs):
    charsheet["name"] = rematch.group(1)


def mtype(charsheet, rematch, **kwargs):
    charsheet["type"] = rematch.group(2)
    charsheet["size"] = rematch.group(1)


parsers = [
    parser.Parser("cotsq_name", name, index=0, regex=name_re, bam=True),
    parser.Parser("cotsq_type", mtype, regex=type_re, bam=True),
]
