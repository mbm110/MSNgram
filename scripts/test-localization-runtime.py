#!/usr/bin/env python3
"""Compile and exercise the Java locale lookup with real java.util.Locale.

Before generation, read the Java fragments emitted by the Kotlin task. In CI,
pass the actual generated LocalizationUtils.java to test the Gradle output.
"""
from pathlib import Path
import json
import re
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
TASK = ROOT / 'buildSrc/src/main/kotlin/org/telegram/tasks/localization/GenerateLocalizationUtilsJavaTask.kt'


def emitted_lookup():
    source = TASK.read_text()
    plugin = (ROOT / 'buildSrc/src/main/kotlin/org/telegram/plugin/TelegramBuildPlugin.kt').read_text()
    match = re.search(r'include\("(values-\*/strings[^\"]*)"\)', plugin)
    assert match, 'localization input pattern missing'
    pattern = match.group(1)
    tags = {'en'}
    for path in (ROOT / 'TMessagesProj/src/main/res').glob(pattern):
        qualifier = path.parent.name.removeprefix('values-')
        tags.add(qualifier[2:].replace('+', '-') if qualifier.startswith('b+') else qualifier.replace('-r', '-'))
    tags = sorted(tags)
    assert 'in-ID' in tags, 'Indonesian custom-only resource directory missing from generator inputs'

    def asset(tag):
        return 'localization_' + re.sub('[^a-z0-9_]', '_', tag.lower()) + '.bin'

    def literal(line, tag='', legacy=''):
        value = line.split('java.appendLine(', 1)[1].rsplit(')', 1)[0]
        value = value.replace('${tag.substring(3)}', tag[3:])
        value = value.replace('${getLocalizationAssetName(tag)}', asset(tag))
        value = value.replace('${getLocalizationAssetName(legacyIndonesianTag)}', asset(legacy))
        return json.loads(value)

    # Use the actual emitted alias templates; removing either exact or language
    # alias from the task makes its corresponding executable assertion fail.
    alias_lines = [line.strip() for line in source.splitlines() if 'java.appendLine(' in line and ('case \\"id' in line or 'case \\"in\\"' in line)]
    exact = []
    fallback = []
    for tag in tags:
        exact.append(f'case {json.dumps(tag)}: return {json.dumps(asset(tag))};')
        if '-' not in tag:
            fallback.append(f'case {json.dumps(tag)}: return {json.dumps(asset(tag))};')
    legacy = 'in' if 'in' in tags else next((tag for tag in tags if tag.startswith('in-')), '')
    for line in alias_lines:
        if '${tag.substring(3)}' in line:
            exact.extend(literal(line, tag) for tag in tags if tag.startswith('in-'))
        elif 'legacyIndonesianTag' in line:
            # One occurrence is in the exact switch and one in the language switch.
            (exact if not any('case "id"' in x for x in exact) else fallback).append(literal(line, legacy=legacy))
        else:
            fallback.append(literal(line))
    return '''package org.telegram.localization;
import java.util.Locale;
public final class LocalizationUtils {
 public static String getLocalizationAsset(Locale locale) {
  if (locale == null) return null;
  switch (locale.toLanguageTag()) { %s }
  switch (locale.getLanguage()) { %s default: return null; }
 }
}
''' % ('\n'.join(exact), '\n'.join(fallback))


HARNESS = '''import java.util.Locale;
import org.telegram.localization.LocalizationUtils;
public class LocaleLookupFixture {
 public static void main(String[] args) {
  check(new Locale("id", "ID"), "localization_in_id.bin");
  check(new Locale("in", "ID"), "localization_in_id.bin");
  check(new Locale("id"), "localization_in_id.bin");
  check(new Locale("in"), "localization_in_id.bin");
  check(new Locale("id", "US"), "localization_in_id.bin");
  check(new Locale("en", "GB"), "localization_en.bin");
  check(Locale.forLanguageTag("zz-ZZ"), null);
  check(null, null);
  System.out.println("PASS: 8 Java Locale cases (id-ID, in-ID, id, in, id-US, en-GB, unknown, null)");
 }
 static void check(Locale locale, String expected) {
  String actual = LocalizationUtils.getLocalizationAsset(locale);
  if (!java.util.Objects.equals(actual, expected)) throw new AssertionError(locale + ": expected=" + expected + " actual=" + actual);
 }
}
'''

with tempfile.TemporaryDirectory(prefix='locale-fixture-') as directory:
    directory = Path(directory)
    generated = Path(sys.argv[1]) if len(sys.argv) > 1 else directory / 'LocalizationUtils.java'
    if len(sys.argv) == 1:
        generated.write_text(emitted_lookup())
    harness = directory / 'LocaleLookupFixture.java'
    harness.write_text(HARNESS)
    subprocess.run(['javac', '-encoding', 'UTF-8', '-d', str(directory), str(generated), str(harness)], check=True)
    subprocess.run(['java', '-cp', str(directory), 'LocaleLookupFixture'], check=True)
