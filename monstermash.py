#!/usr/bin/python
import sys
import re
import math
import parsers
import char
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service

chrome_service = Service("/snap/bin/chromium.chromedriver")

MODES = [parsers.etum_mode, parsers.cotsq_mode]


def parse(intext):
    best_result = None
    best_score = -1

    for m in MODES:
        result = char.Sheet()
        doc = parsers.Document(intext)
        doc.parse(m, result)
        score = doc.score()
        if score > best_score:
            best_result = result
            best_score = score

    return best_result


if __name__ == "__main__":
    chrome_options = webdriver.chrome.options.Options()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    # Change chrome driver path accordingly
    # chrome_driver = "/snap/bin/chromium.chromedriver"
    driver = webdriver.Chrome(service=chrome_service, options=chrome_options)


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
    intval = None
    if isinstance(val, int):
        intval = val
    else:
        try:
            intval = int(val)
        except ValueError:
            pass

    if intval is None:
        return "-"
    else:
        return math.floor((intval - 10) / 2)


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
    # Special Qualities
    set_in_roll20("attr_npcspecialqualities", details, "sq")
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

    if details["senses"]:
        desc = "Senses: " + details["senses"] + "\n"
        set_val("attr_npcdescr", desc)

    skills = ""
    for k, v in details["skills"].items():
        skills += k + ": " + v + "; "
    set_val("attr_npcskills", skills)

    combatdesc = ""
    for k, m in details["moves"].items():
        combatdesc += f'{m["name"]} ({m["type"]})\n'
        combatdesc += "-" * 10 + "\n"
        combatdesc += m["desc"] + "\n\n"
    set_val("attr_npccombatdescr", combatdesc)


if __name__ == "__main__":
    print("Connected to: ", driver.title)
    accumulated = []
    for line in sys.stdin:
        accumulated.append(line)

    current = parse(accumulated)
    print(current)
    send_to_browser(current)
    print("Send to browser complete")
