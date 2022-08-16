import json
import re


def retouch_dashes(val):
    if isinstance(val, str):
        return re.sub("[–—]", "-", val)
    else:
        return val


def strip_whitespace(val):
    return val.strip()


def is_string(val):
    if isinstance(val, str):
        return None
    else:
        return f"'{val}' is a {type(val)} - expected a string"


def is_integer(val):
    if isinstance(val, int):
        return None
    else:
        try:
            parsed = int(retouch_dashes(val))
        except:
            return f"'{val}' failed to parse as an integer"
    return None


def is_nullable_number(val):
    permitted = "+0123456789-—"
    if isinstance(val, int):
        return None
    if not isinstance(val, str):
        return f"Unexpected type {type(val)} - expected a nullable number"
    for c in val:
        if not c in permitted:
            return f"'{val}' contains character '{c}' which is not permitted for a nullable number"
    return None


def valid_alignment(val):
    if not isinstance(val, str):
        return f"'{val}' is a {type(val)} - expected a str"
    if val == "N":
        return None
    elif len(val) == 2:
        if val[0] in "CNL" and val[1] in "GNE":
            return None
    else:
        return f"{val} is not a valid alignment"


VALID_SIZES = [
    "Fine",
    "Diminutive",
    "Tiny",
    "Small",
    "Medium",
    "Large",
    "Huge",
    "Gargantuan",
    "Colossal",
]


def valid_size(val):
    if val in VALID_SIZES:
        return None
    else:
        return f"{val} is not a valid size"


# https://www.d20srd.org/srd/combat/movementPositionAndDistance.htm
DEFAULT_SPACE_REACH = {
    "Fine": {"space": "1/2", "reach": 0},
    "Diminutive": {"space": 1, "reach": 0},
    "Tiny": {"space": "2 1/2", "reach": 0},
    "Small": {"space": 5, "reach": 5},
    "Medium": {"space": 5, "reach": 5},
    "Large": {"space": 10, "reach": 5},
    "Huge": {"space": 15, "reach": 10},
    "Gargantuan": {"space": 20, "reach": 15},
    "Colossal": {"space": 30, "reach": 20},
}


def default_space_reach(sheet, key):
    try:
        size = sheet["size"]
        return DEFAULT_SPACE_REACH[size][key]
    except KeyError:
        return None


def default_space(sheet):
    return default_space_reach(sheet, "space")


def default_reach(sheet):
    return default_space_reach(sheet, "reach")


def empty_string(sheet):
    return ""


def stringify(val):
    return str(val)


def is_subsheet(val):
    if isinstance(val, SubSheet):
        return None
    else:
        return f"'{val}' is a {type(val)} - expected a SubSheet"


def is_type(val):
    if not isinstance(val, dict):
        return f"Tried to set unexpected type: {type(val)} to a move"
    if "type" in val:
        if val["type"] not in ["Su", "Ex", "Traits", "Misc"]:
            return f"Unexpected move type: {val['type']}"
    else:
        return "Move is missing a type"

    if "desc" not in val:
        return "Move is missing a description"
    elif not isinstance(val["desc"], str):
        return f"Unexpected type of description: {type(val['desc'])}"

    if "name" not in val:
        return "Move is missing a name"
    elif not isinstance(val["name"], str):
        return f"Unexpected type of name: {type(val['name'])}"


class DataType:
    def __init__(self, retoucher, validator, default=None, mandatory=True):
        self._retoucher = retoucher
        self._validator = validator
        self._default = default
        self.mandatory = mandatory

    def retouch(self, val):
        if self._retoucher is None:
            return val
        return self._retoucher(val)

    def validate(self, val):
        return self._validator(val)

    def default(self, sheet):
        if self._default is None:
            return None
        return self._default(sheet)


class SubSheet:
    def __init__(self, dts):
        self._dts = dts
        self._values = dict()
        self._read = dict()

    def _get_dt(self, key):
        dt = None
        if key in self._dts:
            dt = self._dts[key]
        elif "*" in self._dts:
            dt = self._dts["*"]
        else:
            raise KeyError(f"{key} is not a configured sheet attribute")
        return dt

    def _check_assignment(self, key, value):
        dt = self._get_dt(key)
        validation = dt.validate(value)
        if validation is not None:
            raise ValueError(f"Failed to set {key} to '{value}': {validation}")
        return dt.retouch(value)

    def __getitem__(self, key):
        val = None
        if key in self._values:
            val = self._values[key]
            self._read[key] = True
            return val

        dt = self._get_dt(key)
        if dt is None:
            raise KeyError(
                f"Unable to find datatype for key {key} when checking for default values"
            )
        val = dt.default(self)
        if val is not None:
            self._read[key] = True
            return val
        raise KeyError(f"Key {key} not set and no default available")

    def __setitem__(self, key, value):
        result = self._check_assignment(key, value)
        self._values[key] = result

    def __contains__(self, item):
        return item in self._values

    def __eq__(self, other):
        if not isinstance(other, SubSheet):
            return False
        else:
            return self._values == other._values

    def __str__(self):
        return str(self._values)

    def __repr__(self):
        return self.__str__()

    def append():
        result = self._check_assignment(key, value)
        if not isinstance(self._values[key], list):
            raise TypeError(f"{key} is not an appendable key")
        self._values[key].append(result)

    def items(self):
        return self._values.items()

    def compare(self, target, res=""):
        for k, v in self.items():
            if isinstance(v, SubSheet):
                # target[k] may exist as SubSheet
                if k in target:
                    res += f"Checking SubSheet with key {k} >\n"
                    res = self[k].compare(target[k], res)
                    res += "< Return from SubSheet Check\n"
                else:
                    res += f"Key {k} missing in target. Expected to be a SubSheet\n"
            else:
                if not k in target:
                    res += f"Key {k} missing in rhs. Expected to be {v}\n"
                elif target[k] != v:
                    res += f"Key {k} got lhs value {v} != rhs {target[k]}\n"
        for k, v in target.items():
            if not k in self._values:
                res += (
                    f"Key {k} exists in rhs, but missing in lhs. Expected value: {v}\n"
                )
        return res

    def is_complete(self):
        for key, dt in self._dts.items():
            if not dt.mandatory:
                continue
            if key == "*":
                continue
            try:
                val = self.__getitem__(key)
                if not val:
                    print(f"{key} was falsey, sheet not complete")
                    return False  # Not truthy
                elif isinstance(val, SubSheet):
                    if not val.is_complete():
                        return False
            except KeyError:
                print(f"{key} was missing, sheet not complete")
                return False
        return True


NULLABLE_NUMBER = DataType(stringify, is_nullable_number)
OPTIONAL_NULLABLE_NUMBER = DataType(
    stringify, is_nullable_number, default=empty_string, mandatory=False
)
INTEGER = DataType(retouch_dashes, is_integer)
SUBSHEET = DataType(None, is_subsheet)
ARBITRARY_STRING = DataType(strip_whitespace, is_string)
OPTIONAL_ARBITRARY_STRING = DataType(
    strip_whitespace, is_string, default=empty_string, mandatory=False
)

ABILITIES_DATATYPES = {
    "str": NULLABLE_NUMBER,
    "dex": NULLABLE_NUMBER,
    "con": NULLABLE_NUMBER,
    "int": NULLABLE_NUMBER,
    "wis": NULLABLE_NUMBER,
    "cha": NULLABLE_NUMBER,
}

SAVES_DATATYPES = {
    "fort": INTEGER,
    "ref": INTEGER,
    "will": INTEGER,
}

ARMOR_DATATYPES = {
    "base": NULLABLE_NUMBER,
    "touch": NULLABLE_NUMBER,
    "flat": NULLABLE_NUMBER,
}


CHARACTER_DATATYPES = {
    # TODO: Maybe include the roll20 field name so we can enumerate over them
    "name": ARBITRARY_STRING,
    "hp": INTEGER,
    "hd": INTEGER,
    "alignment": DataType(strip_whitespace, valid_alignment),
    # TODO: Maybe want to Capital Case this as well
    "size": DataType(strip_whitespace, valid_size),
    "type": ARBITRARY_STRING,
    "init": INTEGER,
    "senses": OPTIONAL_ARBITRARY_STRING,
    "attack": ARBITRARY_STRING,
    "fullAttack": ARBITRARY_STRING,
    "space": DataType(None, is_integer, default=default_space),
    "reach": DataType(None, is_integer, default=default_reach),
    "bab": OPTIONAL_NULLABLE_NUMBER,
    "grapple": OPTIONAL_NULLABLE_NUMBER,
    "feats": OPTIONAL_ARBITRARY_STRING,
    "speed": ARBITRARY_STRING,  # Possibly multiple types of string
    "ac": SUBSHEET,
    "skills": SUBSHEET,
    "saves": SUBSHEET,
    "abilities": SUBSHEET,
    "moves": SUBSHEET,
    "sa": OPTIONAL_ARBITRARY_STRING,
    "sq": OPTIONAL_ARBITRARY_STRING,
}


def load_recursive(target, inval):
    for k, v in inval.items():
        if isinstance(v, dict):
            # target[k] may exist as SubSheet
            if k in target:
                load_recursive(target[k], inval[k])
            else:
                new_target = dict()
                load_recursive(new_target, inval[k])
                target[k] = new_target
        else:
            target[k] = v


class Sheet(SubSheet):
    def __init__(self):
        super().__init__(CHARACTER_DATATYPES)
        self["ac"] = SubSheet(ARMOR_DATATYPES)
        self["skills"] = SubSheet({"*": NULLABLE_NUMBER})
        self["saves"] = SubSheet(SAVES_DATATYPES)
        self["abilities"] = SubSheet(ABILITIES_DATATYPES)
        self["moves"] = SubSheet({"*": DataType(None, is_type)})

    def from_json(self, path):
        jval = json.loads(path)
        load_recursive(self, jval)
