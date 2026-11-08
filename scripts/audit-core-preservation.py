#!/usr/bin/env python3
"""Report baseline settings/hooks and upstream core evidence; never infer feature parity."""
import argparse
import collections
import hashlib
import json
import re
import subprocess
from pathlib import Path

BASELINE = '5bceca7bf8535b8ed99f4322bc5f859b843e2c76'
UPSTREAM = '8f2a8a03aa7aec599150b09d302bfd5023283344'
CORE = [
    'TMessagesProj/src/main/java/org/telegram/tgnet/TLRPC.java',
    'TMessagesProj/src/main/java/org/telegram/messenger/MessagesController.java',
    'TMessagesProj/src/main/java/org/telegram/messenger/MessagesStorage.java',
    'TMessagesProj/src/main/java/org/telegram/messenger/FileLoader.java',
    'TMessagesProj/src/main/java/org/telegram/messenger/FileLoadOperation.java',
    'TMessagesProj/src/main/java/org/telegram/tgnet/ConnectionsManager.java',
    'TMessagesProj/jni/tgnet/ConnectionsManager.cpp',
    'TMessagesProj/jni/tgnet/MTProtoScheme.cpp',
    'TMessagesProj/jni/tgnet/ApiScheme.cpp',
    'TMessagesProj/src/main/java/org/telegram/ui/ChatActivity.java',
]
CONFIGS = [
    'TMessagesProj/src/main/kotlin/com/msngram/NaConfig.kt',
    'TMessagesProj/src/main/java/tw/nekomimi/nekogram/NekoConfig.java',
]
HOOK = re.compile(r'Ayu|ayu|[Gg]host|enhancedFileLoader|uploadBoost|WebProxy|webProxy|sendReadMessagePackets|sendReadStoriesPackets|sendOnlinePackets|sendUploadProgress')


def git(*args):
    return subprocess.check_output(['git', *args])


def snapshot(ref, path):
    result = subprocess.run(['git', 'show', f'{ref}:{path}'], capture_output=True)
    return result.stdout if result.returncode == 0 else None


def sources(ref):
    listing = git('ls-tree', '-r', ref, 'TMessagesProj/src/main', 'TMessagesProj/jni/tgnet').decode().splitlines()
    # One persistent object reader avoids thousands of git process launches.
    with subprocess.Popen(['git', 'cat-file', '--batch'], stdin=subprocess.PIPE, stdout=subprocess.PIPE) as reader:
        try:
            for entry in listing:
                metadata, path = entry.split('\t', 1)
                mode, kind, oid = metadata.split()
                if kind != 'blob' or not path.endswith(('.java', '.kt', '.cpp', '.h')):
                    continue
                reader.stdin.write((oid + '\n').encode())
                reader.stdin.flush()
                header = reader.stdout.readline().split()
                if len(header) != 3 or header[1] != b'blob':
                    raise RuntimeError(f'Unable to read audit source {ref}:{path}')
                data = reader.stdout.read(int(header[2]))
                if reader.stdout.read(1) != b'\n':
                    raise RuntimeError(f'Incomplete audit source {ref}:{path}')
                yield path, data.decode(errors='replace')
        finally:
            reader.stdin.close()
            reader.wait()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--candidate', default='HEAD')
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    refs = {'baseline': BASELINE, 'upstream': UPSTREAM, 'candidate': git('rev-parse', args.candidate).decode().strip()}
    settings = {}
    for path in CONFIGS:
        data = snapshot(BASELINE, path)
        if data is None:
            raise RuntimeError(f'Missing baseline settings file: {path}')
        text = data.decode()
        pattern = r'(?:val|ConfigItem)\s+(\w+)\s*=\s*addConfig\(\s*"([^"]+)"'
        for symbol, key in re.findall(pattern, text):
            settings[symbol] = {'preference_key': key, 'declaration': path, 'baseline_locations': [], 'candidate_locations': []}
    symbols = re.compile(r'\b(' + '|'.join(re.escape(s) for s in settings) + r')\b')
    hooks = {'baseline': [], 'candidate': []}
    for label in hooks:
        for path, text in sources(refs[label]):
            for number, line in enumerate(text.splitlines(), 1):
                location = {'path': path, 'line': number, 'source': line.strip()}
                if HOOK.search(line):
                    hooks[label].append(location)
                # Java callers use generated Kotlin getters.
                normalized = re.sub(r'get([A-Z])(\w*)\(', lambda m: m[1].lower() + m[2] + '(', line)
                for symbol in set(symbols.findall(normalized)):
                    settings[symbol][label + '_locations'].append(location)
    for entry in settings.values():
        before = {(v['path'], v['source']) for v in entry['baseline_locations']}
        after = {(v['path'], v['source']) for v in entry['candidate_locations']}
        entry['missing_baseline_occurrences'] = [{'path': p, 'source': s} for p, s in sorted(before - after)]
        entry['status'] = 'needs_review' if before - after else 'source_occurrences_retained_not_runtime_verified'
    core = {}
    for path in CORE:
        core[path] = {}
        for label, ref in refs.items():
            data = snapshot(ref, path)
            core[path][label] = None if data is None else {'sha256': hashlib.sha256(data).hexdigest(), 'layers': re.findall(r'\bLAYER\s*=\s*(\d+)', data.decode(errors='replace'))}
    candidate_layer = core[CORE[0]]['candidate']['layers']
    lost_hooks = sorted({(v['path'], v['source']) for v in hooks['baseline']} - {(v['path'], v['source']) for v in hooks['candidate']})
    result = {
        'refs': refs, 'core': core, 'settings': settings, 'hook_occurrences': hooks,
        'missing_baseline_hook_lines': [{'path': p, 'source': s} for p, s in lost_hooks],
        'settings_count': len(settings), 'settings_requiring_review': sum(bool(v['missing_baseline_occurrences']) for v in settings.values()),
        'protocol_layer_232': candidate_layer == ['232'],
        'preservation_proven': False,
        'release_decision': 'BLOCK_PENDING_MANUAL_HOOK_REVIEW_CORE_INTEGRATION_AND_SIGNED_BUILDS',
        'limitations': 'Line retention is an audit aid, not behavior proof. Review renamed/reworked hooks, database migration, UI bindings and native download scheduling; compile and verify both signed ARM APKs.'
    }
    Path(args.output).write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: result[k] for k in ['settings_count', 'settings_requiring_review', 'protocol_layer_232', 'release_decision']}))


if __name__ == '__main__':
    main()
