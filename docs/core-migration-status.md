# Telegram 13.1.1 migration status: blocked

Authoritative MSNgram baseline: `5bceca7bf8535b8ed99f4322bc5f859b843e2c76`.
Pinned Nagram target: `8f2a8a03aa7aec599150b09d302bfd5023283344`.

The existing `83a214bd79db34524fc005528e06bf5a4941e6a5` build is not a migrated core: its TLRPC is layer 229 and MessagesController and native ConnectionsManager match the old baseline. Do not merge or publish it as Telegram 13.1.1.

## Current isolated implementation

Branch `migrate/msngram-full-13.1.1` starts from the authoritative baseline. Commit `3c43b53a5` ports the real upstream `62b56a07c` Telegram 12.10.1 prerequisite. It keeps MSNgram configuration/build identity, public FileLog initialization and date format, centered pinned-chat avatar behavior and hide-all-tabs behavior while incorporating the upstream fixes. This commit has not been compiled and is not a release candidate. Layer remains 229.

A full recursive snapshot merge using Nagram 12.10.0 `4e1a61eca` as an explicit content base produced 429 conflicted files and 1,935 conflict blocks. It is not an ancestral merge base. That experiment was reset without committing conflict resolutions, rather than accepting either fork wholesale. A subsequent sequential 12.10.2 import exposed 46 conflicted files; that experiment was also reset. Current index is clean after the prerequisite commit and audit additions.

## Preservation evidence and next gates

Run `python3 scripts/audit-core-preservation.py --output /path/to/report.json`. It enumerates baseline NaConfig/NekoConfig preference keys and their old/new source locations, Ayu/ghost/download/WebProxy hooks, and hashes/layers for protocol, controllers, storage, downloads, native types and ChatActivity. Missing occurrences require review. Retained lines alone cannot establish behavior preservation; the script deliberately blocks release.

Preserve all baseline features. In particular:

- `EnableSaveDeletedMessages`, `EnableSaveEditsHistory`, media-saving options and per-dialog exclusions: retain Ayu database schema, capture/update/delete storage/controller hooks and deleted/history ChatActivity actions and rendering.
- `enhancedFileLoader`: retain FileLoadOperation's switch from 128 KiB / 4 requests to 512 KiB / 8 requests and integrate it with upstream byte budgets and native scheduling. Retain `uploadBoost` too.
- Ghost settings `sendReadMessagePackets`, `sendReadStoriesPackets`, `sendOnlinePackets`, `sendUploadProgress`, offline/mark-read behavior and locked/per-dialog overrides: retain their request interception and UI bindings.
- Retain all other baseline preferences, including filters, bookmarks, translations/LLM, local appearance/premium behavior, push support and every settings activity.
- Retain WebProxy transport, testing, URI parsing, settings/persistence and links. Upstream 12.10.2 replaces ProxyInfo fields with typed ProxySettings; migrate NagramX callers and serialized/preference data coherently.
- Retain package `com.msngram.messenger`, MSNgram names and approved M assets, stable signer SHA-256 `2a6ad2b3b9326cc6b0cd85063da46230ddc5587511cb978e862918384913efaa`.

Remaining official updates after the first prerequisite, in order: `163356809`, `9552e5541`, `c84801762`, `dc780e81e`, `f2908b141`, `5e56d3434`, `368b6b7fd`, `9e430b103`, `f32ffeec7`, `0aae95980`, `4de548e79`, `3de37c8cf`. These commits alone are not the entire pinned snapshot: integrate their intervening dependencies, submodule revisions, native/layout/build coupling and pinned upstream changes with explicit custom-difference review. The 13.1.1 commit by itself changes only 25 files and cannot update this old baseline.

Before release, establish layer 232, account for upstream core deltas and every justified custom difference, review the feature-key-to-hook mapping, run Kotlin/Java/duplicate-class CI preflight and signed ARM32/ARM64 assembly, and verify package, signer, branding, ABI libraries and WebProxy descriptors from both APKs. No build was dispatched for this incomplete branch; no merge or publication is authorized by this status file.
