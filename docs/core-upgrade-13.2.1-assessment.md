# Official Telegram 13.2.1 upgrade assessment

Status: **source upgrade not integrated**. MSNgram remains on its existing 13.1.1/layer-232 core. No build, commit, push, release, clone, worktree, submodule initialization, or bulk Git blob hydration was performed. No application source, build configuration, version, signer, or existing user edit was changed by this assessment.

## Pinned inputs and scope

- Local branch: `migrate/msngram-full-13.1.1`.
- Local HEAD: `183d663c0401415409ec76530f7c82cd5145bae6`.
- Official 13.1.1 baseline: [`3de37c8cfb039452be7398909461da6288babf15`](https://github.com/DrKLO/Telegram/commit/3de37c8cfb039452be7398909461da6288babf15), version code 7237, layer 232.
- Official 13.2.0: [`55356b2a7b7e6d3d5ec188b54f0ce3e05c5e9601`](https://github.com/DrKLO/Telegram/commit/55356b2a7b7e6d3d5ec188b54f0ce3e05c5e9601).
- Official 13.2.1 target: [`7be672ead283d022812d75c729d3a04dd4c2a2c6`](https://github.com/DrKLO/Telegram/commit/7be672ead283d022812d75c729d3a04dd4c2a2c6), version code 7291, layer 233.

The abbreviated local `6a3a845db` is a Nagram snapshot and must not be used as the official Telegram comparison base. The correct official base above was confirmed through DrKLO/Telegram's commits API. GitHub's compare API reports 25 commits but returns only 300 changed files. Both recursive Git trees were fetched and checked for `truncated: false`; comparison of their blob/gitlink IDs gives the complete inventory below. These are source paths, not feature counts.

| Inventory | Count |
| --- | ---: |
| Changed paths | 4,739 |
| Added | 3,741 |
| Modified | 937 |
| Removed | 61 |
| Changed Java paths | 999 |
| New Java paths | 105 |
| Changed paths identical to official baseline in local HEAD | 621 |
| Changed paths differing from official baseline in local HEAD | 377 |
| Of those differing paths, Java paths | 350 |
| New upstream paths absent in local HEAD | 3,741 |

## Concrete integration blockers

These are unresolved integration work, not proof that migration is impossible. No partial layer/version bump was applied.

1. **Fork behavior conflicts require manual resolution.** Three-way previews used current worktree contents as ours, official 13.1.1 as base, and official 13.2.1 as theirs. `ChatActivity.java` has 21 conflict blocks, including custom formatting menu IDs/actions, selected-text behavior, centered-title margins, grouped menu icons, sticker import and translation behavior. `FileUploadOperation.java` has two blocks: MSNgram's `minUploadChunkSizeBoost` and `uploadBoost` selection conflict with upstream's new big-file chunk policy. `MediaController.java` has two blocks, including the guard selecting the legacy recorder for custom bitrate/noise enhancement and playback handling. Choosing either side wholesale would discard behavior.
2. **Cross-cutting source migrations are incomplete.** Upstream removes/replaces the old PiP implementations and `blur3/source/BlurredBackgroundSource*` classes, while the local custom ChatActivity uses those types. A clean merge of `TLRPC`, controller or native tgnet files alone would not establish compatibility of the full 999-path Java delta or the fork callers. The remaining 350 differing Java paths have not received a full manual merge/reachability review.
3. **Native dependency graph must move as a set.** Upstream CMake adds `twidget_target_sources` and switches Prisma from prebuilt `libprisma.a` to `add_subdirectory(prisma)`. The new twidget subtree has 3,627 changed paths totaling 43,184,156 target bytes. Its CMake explicitly requires QuickJS, widget_host.cpp, renderer.cpp and litehtml/document.cpp; the local twidget directory is absent. Upstream also changes four gitlinks (below), replaces 24 FFmpeg/libvpx archives, removes four Prisma archives, and adds FFmpeg patches. All target `.a` files in the delta total 36,308,814 bytes. These are inventory facts; this assessment did not download/initialize native dependencies or test their availability/buildability.
4. **Build/dependency reconciliation remains.** Preview conflicts exist in `TMessagesProj/build.gradle`, root `build.gradle` and `gradle.properties` (one block each). Official changes introduce Firebase BoM 34.19.0 / firebase-pnv and update Google Services/Crashlytics plugins. The fork's AGP/toolchain, package, stable signer, localization generators, `emoji.pack` noCompress rule, tgcalls bitrate patch and existing APK naming changes must be retained explicitly. Replacing official Gradle properties would also replace fork identity/version settings.
5. **Verification boundary.** No compilation or device behavior was exercised, as instructed. The existing fixtures verify the existing core only. Clean text merges in selected TLRPC/controller/storage/download/native files do not establish behavior or ABI compatibility. The protocol still reads layer 232 locally.

| Gitlink | Official 13.1.1 | Official 13.2.1 |
| --- | --- | --- |
| `TMessagesProj/jni/tgcalls` | `1398c1648f52666b3249111ec3c5b531946e41e4` | `545f5ae599f8282e1ae3f38aaff166d179d75703` |
| `TMessagesProj/jni/third_party/ffmpeg` | `45f1910444f34b02621f9f0426ea1a538a613c41` | `8dca1586f468bfcbb78ae3ed618af1361d9f140a` |
| `TMessagesProj/jni/third_party/libprisma` | `31a5d6fbbef8136e4a2b3adaf7b95e2ccaa7436d` | `94640c63c20eacdf70e37e23198d9ab53c802ebd` |
| `TMessagesProj/jni/third_party/libvpx` | `1024874c5919305883187e2953de8fcb4c3d7fa6` | `6df3ec34557879fff673706f4a1d9fbd0f3a6f0e` |

## Executed checks

- `python3 scripts/test-localization-generator.py`: PASS; 12,251 merged names, 740 custom names, 707 Persian overlay names.
- `python3 scripts/test-localization-runtime.py`: PASS; eight actual Java Locale cases (`id-ID`, `in-ID`, `id`, `in`, `id-US`, `en-GB`, unknown, null).
- `python3 scripts/test-webproxy-callbacks.py`: PASS; production tester exercised for ready timeout, stale ready, success, duplicate/late native callbacks, reused port, native timeout and zero-port startup.
- `GIT_NO_LAZY_FETCH=1 python3 scripts/audit-core-preservation.py --output .../core-preservation.json`: exit 0; 325 settings, layer 232, three textual setting-review flags (`disableAvatarBlur`, `showReport`, `hideAllTab`) and three missing exact hook lines. These are the pre-existing reviewed findings recorded in `core-migration-status.md`, not new upgrade regressions. The script deliberately sets preservation_proven=false and blocks release; its candidate is committed HEAD, not the dirty worktree.
- Initial status had 358 entries. SHA-256 was recorded for 357 file entries; every recorded original file remained byte-identical after the probes. The remaining status entry is the untracked `docs/branding/icon-variants/` directory, which was not touched. HEAD was unchanged. All merge previews were written outside the repository.

## Evidence and resumption

Task evidence directory: `/root/.hermes/cache/scratch/msngram-13.2.1-assessment/` (scratch retention is temporary).

- `complete-inventory.json`: complete path-level old/new SHA, mode, size, status and local-overlap classification.
- `3de37c8cfb039452be7398909461da6288babf15-tree.json`, `7be672ead283d022812d75c729d3a04dd4c2a2c6-tree.json`: full official recursive tree responses.
- `official-history.json`, `official-compare.json`: API provenance; compare response is capped and must not substitute for the complete inventory.
- `selected-merge-results.json`, `selected/*/{base,target,local,upstream.diff,merge-preview}`: 16 selected source/build probes, including concrete conflict markers. Preview outputs are not integrated sources.
- `fixtures.json`, `*.py.log`, `core-preservation.json`: executed check results.
- `initial-worktree.json`, `preserved-worktree.json`: original dirty-file hashes and post-probe comparison.
- `inventory.py`, `probe.py`, `verify.py`: reproducible assessment helpers, with no application-source writes.

At the recorded post-probe check, free space was 623,915,008 bytes (about 595 MiB), from 682,795,008 bytes initially. Evidence used approximately 50 MiB. Disk alone does not make the source upgrade impossible, but it rules out casual cloning, full Git hydration or local Android builds.

Resume with the complete inventory, resolving the fork behavior and full dependency graph before changing the layer/version. Preserve the original 358 edits and all existing Ghost/Ayu/history/WebProxy/download/upload/recorder settings and hooks. Build validation remains a separately authorized step. This document is an assessment and explicit handoff, not a completed 13.2.1 migration.
