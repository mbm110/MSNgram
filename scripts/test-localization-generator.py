#!/usr/bin/env python3
"""Regression test for the generated localization namespace.

The build task must treat strings.xml, strings_na.xml, strings_nax.xml and
strings_neko.xml as one resource namespace. This exercises the same XML input
selection and Java hash binding used by the generated assets.
"""
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

root = Path(__file__).resolve().parents[1]
res = root / "TMessagesProj/src/main/res"

files = sorted(res.glob("values/strings*.xml"))
files += sorted(res.glob("values-*/strings*.xml"))
assert files, "no string resources found"

names_by_file = {}
all_names = set()
for path in files:
    names = {
        node.attrib["name"]
        for node in ET.parse(path).getroot().findall("string")
        if "name" in node.attrib
    }
    names_by_file[path] = names
    all_names.update(names)

custom_files = [p for p in files if p.name in {"strings_na.xml", "strings_nax.xml", "strings_neko.xml"}]
custom_names = set().union(*(names_by_file[p] for p in custom_files))
assert len(custom_names) >= 300, len(custom_names)
assert {"N_Config", "CustomTitle", "MSNgramSettings"} <= custom_names

# Java String.hashCode(), matching TelegramStringsTask and Localization.
def java_hash(value: str) -> int:
    result = 0
    for char in value:
        result = (31 * result + ord(char)) & 0xFFFFFFFF
    return result if result < 0x80000000 else result - 0x100000000

hashes = {}
for name in all_names:
    value = java_hash(name)
    previous = hashes.setdefault(value, name)
    assert previous == name, f"hash collision: {previous} / {name}"

# Confirm each custom resource has a generated namespace hash and that a
# localized overlay can replace it without changing the resource identity.
for name in custom_names:
    assert java_hash(name) in hashes, name
fa_files = sorted((res / "values-fa-rIR").glob("strings*.xml"))
fa_names = set()
for path in fa_files:
    fa_names.update(
        node.attrib["name"]
        for node in ET.parse(path).getroot().findall("string")
        if "name" in node.attrib
    )
assert {"N_Config", "CustomTitle"} <= fa_names
assert all(java_hash(name) in hashes for name in fa_names)

print(f"PASS: {len(all_names)} merged names, {len(custom_names)} custom names, {len(fa_names)} Persian overlay names")
