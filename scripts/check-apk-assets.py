#!/usr/bin/env python3
"""Regression checks for assets that are memory-mapped at runtime."""
import struct
import sys
import zipfile
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit(f"usage: {sys.argv[0]} APK")
    apk = Path(sys.argv[1])
    with zipfile.ZipFile(apk) as archive:
        try:
            info = archive.getinfo("assets/emoji.pack")
        except KeyError as exc:
            raise AssertionError("APK is missing assets/emoji.pack") from exc
        assert info.compress_type == zipfile.ZIP_STORED, (
            f"assets/emoji.pack must be ZIP_STORED, got method {info.compress_type}"
        )
        assert info.file_size >= 32, f"emoji.pack is too small: {info.file_size}"
        payload = archive.read(info)

    assert payload[:4] == b"EPK3", f"unexpected emoji.pack magic: {payload[:4]!r}"
    version, entry_size = struct.unpack_from("<HH", payload, 4)
    assert version in (2, 3), f"unsupported emoji.pack version {version}"
    assert entry_size == 20, f"unexpected emoji.pack entry size {entry_size}"
    declared_size = struct.unpack_from("<I", payload, 24)[0]
    assert declared_size == len(payload), (
        f"emoji.pack header size {declared_size} != payload size {len(payload)}"
    )
    assert info.header_offset >= 0
    print(
        f"emoji.pack: ZIP_STORED, {len(payload)} bytes, EPK3 v{version}, "
        f"entry size {entry_size}, readable"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
