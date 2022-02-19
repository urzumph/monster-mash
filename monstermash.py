#!/usr/bin/python
import sys
import re
import math
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


def accum_until(fr, until, intext):
    acc = ""
    i = fr
    while i < len(intext) and not until.search(intext[i]):
        acc += intext[i].strip() + " "
        i += 1
    return acc.rstrip()


def prechomp_regex(string, regex):
    m = regex.match(string)
    if not m:
        return string, m
    else:
        return string[len(m.group(0)) :], m


# Ster Longhorn, Minotaur Chief
def name(obj, intext):
    obj["name"] = intext[0].strip()
    return obj


def etum_dr(obj, intext):
    obj["sq"] = intext.lstrip(";, ")
    return obj


# hp 45 (6 HD)
etum_hp_re = re.compile("\s*hp (\d+) (?:each )?\((\d+) HD\)\s*(.*)?")


def etum_hp(obj, intext):
    for line in intext:
        m = etum_hp_re.match(line)
        if m:
            obj["hp"] = int(m.group(1))
            obj["hd"] = int(m.group(2))
            if len(m.group(3)) > 0:
                obj = etum_dr(obj, m.group(3))
    return obj


# CE Large monstrous humanoid
etum_type_re = re.compile(
    "\s*((?:[CNL][GNE])|N) (Fine|Diminutive|Tiny|Small|Medium|Large|Huge|Gargantuan|Colossal) (.*)"
)


def etum_type(obj, intext):
    for line in intext:
        m = etum_type_re.match(line)
        if m:
            obj["alignment"] = m.group(1)
            obj["size"] = m.group(2)
            obj["type"] = m.group(3).strip()
    return obj


# Senses darkvision 60 ft., scent; Listen +11, Spot +11
etum_senses_re = re.compile("^\s*Senses (.+)")
etum_senses_end_re = re.compile("(;|Listen|Spot)")


def etum_senses(obj, text):
    remainder, m = prechomp_regex(text, etum_senses_re)
    if not m:
        return obj, text
    else:
        senses = m.group(1)
        n = etum_senses_end_re.search(senses)
        if n:
            obj["senses"] = senses[0 : n.start()].rstrip(", ")
            remainder = remainder + senses[n.start() :]
        else:
            obj["senses"] = m.group(1)
        return obj, remainder


# Listen +11, Spot +11
skills_re = re.compile("^\s*(\w+) ([+\-]\d+)[,;]?\s*")


def skills(obj, text):
    remainder, m = prechomp_regex(text, skills_re)
    while m:
        obj["skills"][m.group(1)] = m.group(2)
        remainder, m = prechomp_regex(remainder, skills_re)
    return obj, remainder


# Init +0; Senses darkvision 60 ft., scent; Listen +11, Spot
# +11
# Languages Giant, Common
etum_init_re = re.compile("^\s*Init ([+\-\–]\d+);")
etum_lang_re = re.compile("^Languages ")


def etum_init(obj, intext):
    for i in range(0, len(intext)):
        remainder, m = prechomp_regex(intext[i], etum_init_re)
        if m:
            obj["init"] = m.group(1)
            accum = remainder + " " + accum_until(i + 1, etum_lang_re, intext)
            accum = accum.rstrip()
            obj, accum = etum_senses(obj, accum)
            obj, accum = skills(obj, accum)
            break
    return obj


# AC 19, touch 13, flat-footed —; natural cunning
etum_ac_re = re.compile("^\s*AC ([\d\—]+), touch ([\d\—]+), flat-footed ([\d\—]+)")


def etum_ac(obj, intext):
    for line in intext:
        m = etum_ac_re.match(line)
        if m:
            obj["ac"]["base"] = m.group(1)
            obj["ac"]["touch"] = m.group(2)
            obj["ac"]["flat"] = m.group(3)
            break
    return obj


# Fort +6, Ref +5, Will +5
etum_saves_re = re.compile(
    "^\s*Fort ([+\-]?[\d\—]+), Ref ([+\-]?[\d\—]+), Will ([+\-]?[\d\—]+)"
)


def etum_saves(obj, intext):
    for line in intext:
        m = etum_saves_re.match(line)
        if m:
            obj["saves"]["fort"] = m.group(1)
            obj["saves"]["ref"] = m.group(2)
            obj["saves"]["will"] = m.group(3)
            break
    return obj


# Melee mwk greataxe +11/+6 (3d6+7/×3) and
# gore +5 (1d8+3)
# Space 10 ft.; Reach 10 ft.
etum_attack_re = re.compile("^\s*Melee ")
etum_attack_stop_re = re.compile("^Space ")


def etum_attack(obj, intext):
    for i in range(0, len(intext)):
        remainder, m = prechomp_regex(intext[i], etum_attack_re)
        if m:
            accum = (
                remainder.rstrip()
                + " "
                + accum_until(i + 1, etum_attack_stop_re, intext)
            )
            accum = accum.strip()
            obj["attack"] = accum
            obj["fullAttack"] = accum
            break
    return obj


# Space 10 ft.; Reach 10 ft.
etum_space_re = re.compile("^\s*Space ([\d]+) ft.; Reach ([\d]+)")


def etum_space(obj, intext):
    for line in intext:
        m = etum_space_re.match(line)
        if m:
            obj["space"] = int(m.group(1))
            obj["reach"] = int(m.group(2))
            break
    return obj


# Base Atk +6; Grp +15
etum_bab_re = re.compile("^\s*Base Atk [+]?([\-\d]+); Grp [+]?([\-\d]+)")


def etum_bab(obj, intext):
    for line in intext:
        m = etum_bab_re.match(line)
        if m:
            obj["bab"] = int(m.group(1))
            obj["grapple"] = int(m.group(2))
            break
    return obj


# Abilities Str 21, Dex 10, Con 15, Int 10, Wis 10, Cha 8
etum_abilities_re = re.compile(
    "^\s*Abilities Str (\d+), Dex (\d+), Con (\d+), Int (\d+), Wis (\d+), Cha (\d+)"
)


def etum_abilities(obj, intext):
    for line in intext:
        m = etum_abilities_re.match(line)
        if m:
            obj["abilities"]["str"] = int(m.group(1))
            obj["abilities"]["dex"] = int(m.group(2))
            obj["abilities"]["con"] = int(m.group(3))
            obj["abilities"]["int"] = int(m.group(4))
            obj["abilities"]["wis"] = int(m.group(5))
            obj["abilities"]["cha"] = int(m.group(6))
            break
    return obj


# Feats Great Fortitude, Power Attack, Track
etum_feats_re = re.compile("^\s*Feats (.*)")
etum_feats_end_re = re.compile("^Skills ")


def etum_feats(obj, intext):
    for i in range(0, len(intext)):
        remainder, m = prechomp_regex(intext[i], etum_feats_re)
        if m:
            obj["feats"] = m.group(1)
            accum = remainder + " " + accum_until(i + 1, etum_feats_end_re, intext)
            accum = accum.rstrip()
            obj["feats"] += accum
            break
    return obj


# Skills Intimidate +3, Listen +11, Search +4, Spot +11
etum_skills_re = re.compile("^\s*Skills (.*)")


def etum_skills(obj, intext):
    for line in intext:
        m = etum_skills_re.match(line)
        if m:
            obj, _ = skills(obj, m.group(1))
            break
    return obj


squares_re = re.compile("\s*\(\d+ squares\)")


def strip_squares(intext):
    return squares_re.sub("", intext)


# Speed 30 ft. (6 squares)
etum_speed_re = re.compile("^\s*Speed (.*)")


def etum_speed(obj, intext):
    for line in intext:
        m = etum_speed_re.match(line)
        if m:
            obj["speed"] = strip_squares(m.group(1))
    return obj


etum_special_re = re.compile("^(.+?) \((Su|Ex)\) ")


def etum_special(obj, intext):
    for i in range(0, len(intext)):
        remainder, m = prechomp_regex(intext[i], etum_special_re)
        if m:
            move = {"name": m.group(1), "type": m.group(2)}
            accum = remainder + " " + accum_until(i + 1, etum_special_re, intext)
            accum = accum.rstrip()
            move["desc"] = accum
            obj["moves"].append(move)
    return obj


def parse(intext):
    result = dict()
    result["skills"] = dict()
    result["ac"] = dict()
    result["saves"] = dict()
    result["abilities"] = dict()
    result["moves"] = []
    result = name(result, intext)
    result = etum_hp(result, intext)
    result = etum_type(result, intext)
    result = etum_init(result, intext)
    result = etum_ac(result, intext)
    result = etum_saves(result, intext)
    result = etum_attack(result, intext)
    result = etum_space(result, intext)
    result = etum_bab(result, intext)
    result = etum_abilities(result, intext)
    result = etum_feats(result, intext)
    result = etum_skills(result, intext)
    result = etum_speed(result, intext)
    result = etum_special(result, intext)
    return result


if __name__ == "__main__":
    chrome_options = webdriver.chrome.options.Options()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    # Change chrome driver path accordingly
    chrome_driver = "/snap/bin/chromium.chromedriver"
    driver = webdriver.Chrome(chrome_driver, chrome_options=chrome_options)


def iframe_switch():
    switched = False
    iframes = driver.find_elements(By.TAG_NAME, "iframe")
    for f in iframes:
        title = f.get_attribute("title")
        if title.startswith("Character sheet for"):
            driver.switch_to.frame(f)
            switched = True
    if not switched:
        print("Failed to find character sheet window! aborting.")
    return switched


def set_val(name, val):
    elem = driver.find_element("name", name)
    # Select all before sending stuff, allows us to override previous inputs
    elem.send_keys(Keys.CONTROL + "a")
    elem.send_keys(val)


def set_in_roll20(name, details, index):
    try:
        val = details[index]
    except KeyError:
        print("Failed to set ", name, " missing key: ", index)
        return
    set_val(name, val)


def calc_ability_mod(val):
    return math.floor((val - 10) / 2)


def send_to_browser(details):
    if not iframe_switch():
        return
    set_in_roll20("attr_npcname", details, "name")
    set_val("attr_npchitpoints", str(details["hp"]))
    set_val("attr_npchitpoints_max", str(details["hp"]))
    set_val("attr_npchitdie", str(details["hd"]))
    set_in_roll20("attr_npcalignment", details, "alignment")
    set_in_roll20("attr_npctype", details, "type")
    set_in_roll20("attr_npcinit", details, "init")
    # AC
    set_val("attr_npcarmorclass", str(details["ac"]["base"]))
    set_val("attr_npctoucharmorclass", str(details["ac"]["touch"]))
    set_val("attr_npcflatfootarmorclass", str(details["ac"]["flat"]))
    # Saves
    # TODO - alter set_in_roll20 to permit an array of indexes and KeyError check the whole set
    set_in_roll20("attr_npcfortsave", details["saves"], "fort")
    set_in_roll20("attr_npcrefsave", details["saves"], "ref")
    set_in_roll20("attr_npcwillsave", details["saves"], "will")
    # Attacks
    set_in_roll20("attr_npcfullattack", details, "fullAttack")
    set_in_roll20("attr_npcattack", details, "attack")
    # Space / Reach
    set_val("attr_npcspace", str(details["space"]))
    set_val("attr_npcreach", str(details["reach"]))
    # BAB / Grapple
    set_val("attr_npcbaseatt", str(details["bab"]))
    set_val("attr_npcgrapple", str(details["grapple"]))
    # Abilities & Ability Mods
    set_val("attr_npcstr", str(details["abilities"]["str"]))
    set_val("attr_npcstr-mod", str(calc_ability_mod(details["abilities"]["str"])))
    set_val("attr_npcdex", str(details["abilities"]["dex"]))
    set_val("attr_npcdex-mod", str(calc_ability_mod(details["abilities"]["dex"])))
    set_val("attr_npccon", str(details["abilities"]["con"]))
    set_val("attr_npccon-mod", str(calc_ability_mod(details["abilities"]["con"])))
    set_val("attr_npcint", str(details["abilities"]["int"]))
    set_val("attr_npcint-mod", str(calc_ability_mod(details["abilities"]["int"])))
    set_val("attr_npcwis", str(details["abilities"]["wis"]))
    set_val("attr_npcwis-mod", str(calc_ability_mod(details["abilities"]["wis"])))
    set_val("attr_npccha", str(details["abilities"]["cha"]))
    set_val("attr_npccha-mod", str(calc_ability_mod(details["abilities"]["cha"])))
    # Feats
    set_in_roll20("attr_npcfeats", details, "feats")
    # Speed
    set_in_roll20("attr_npcspeed", details, "speed")

    desc = "Senses: " + details["senses"] + "\n"
    set_val("attr_npcdescr", desc)

    skills = ""
    for k, v in details["skills"].items():
        skills += k + ": " + v + "; "
    set_val("attr_npcskills", skills)


# TODO "size": "Large",

if __name__ == "__main__":
    print("Connected to: ", driver.title)
    accumulated = []
    for line in sys.stdin:
        if line.rstrip().upper() == "EXIT":
            sys.exit(0)
        elif line.rstrip().upper() == "END":
            current = parse(accumulated)
            print(current)
            send_to_browser(current)
            accumulated = []
        else:
            accumulated.append(line)
