def strip_whitespace(val):
    return val.strip()


def is_string(val):
    if isinstance(val, str):
        return None
    else:
        return f"'{val}' is a {type(val)} - expected a string"


def is_nullable_number(val):
    permitted = "0123456789-—"
    if isinstance(val, int):
        return None
    if not isinstance(val, str):
        return f"Unexpected type {type(val)} - expected a nullable number"
    for c in val:
        if not c in permitted:
            return f"'{val}' contains character '{c}' which is not permitted for a nullable number"
    return None


def stringify(val):
    return str(val)


def is_subsheet(val):
    if isinstance(val, SubSheet):
        return None
    else:
        return f"'{val}' is a {type(val)} - expected a SubSheet"


class DataType:
    def __init__(self, retoucher, validator):
        self._retoucher = retoucher
        self._validator = validator

    def retouch(self, val):
        if self._retoucher is None:
            return val
        return self._retoucher(val)

    def validate(self, val):
        return self._validator(val)


class SubSheet:
    def __init__(self, dts):
        self._dts = dts
        self._values = dict()
        self._read = dict()

    def _check_assignment(self, key, value):
        dt = None
        if key in self._dts:
            dt = self._dts[key]
        elif "*" in self._dts:
            dt = self._dts["*"]
        else:
            raise TypeError(f"{key} is not a configured sheet attribute")

        validation = dt.validate(value)
        if validation is not None:
            raise ValueError(f"Failed to set {key} to '{value}': {validation}")
        return dt.retouch(value)

    def __getitem__(self, key):
        # TODO: Add logic for defaults here, maybe
        val = self._values[key]
        self._read[key] = True
        return val

    def __setitem__(self, key, value):
        result = self._check_assignment(key, value)
        self._values[key] = result

    def append():
        result = self._check_assignment(key, value)
        if not isinstance(self._values[key], list):
            raise TypeError(f"{key} is not an appendable key")
        self._values[key].append(result)


NULLABLE_NUMBER = DataType(stringify, is_nullable_number)

ARMOR_DATATYPES = {
    "base": NULLABLE_NUMBER,
    "touch": NULLABLE_NUMBER,
    "flat": NULLABLE_NUMBER,
}

CHARACTER_DATATYPES = {
    # TODO: Maybe include the roll20 field name so we can enumerate over them
    "name": DataType(strip_whitespace, is_string),
    "ac": DataType(None, is_subsheet),
    "skills": DataType(None, is_subsheet),
}


class Sheet(SubSheet):
    def __init__(self):
        super().__init__(CHARACTER_DATATYPES)
        self["ac"] = SubSheet(ARMOR_DATATYPES)
        self["skills"] = SubSheet({"*": NULLABLE_NUMBER})
