# Layer 232 migration preservation review

Baseline: `5bceca7bf8535b8ed99f4322bc5f859b843e2c76`. Pinned Nagram target: `8f2a8a03aa7aec599150b09d302bfd5023283344`.

This review distinguishes baseline preservation from complete Nagram snapshot parity. The isolated migration imports the official updates through 13.1.1, while retaining the existing MSNgram custom implementation. It is not a wholesale replacement by the pinned Nagram snapshot.

## Baseline preservation evidence

The following tracked paths have no changes from the baseline after Java API reconciliation: `com/radolyn/ayugram`, `com/msngram`, `WebProxyTransport.java`, `WebProxyConnectionTester.java`, `FileUploadOperation.java`, and the launcher mipmap directories. The preservation auditor finds all 325 baseline settings and layer 232. The three textual setting differences (`hideAllTab`, `disableAvatarBlur`, `showReport`) and three hook-line differences have manual explanations in `core-migration-status.md`.

Ayu storage, deleted-message and edit-history implementation is unchanged. Controller/storage/ChatActivity capture and render hooks remain; a retained class or setting alone is not a runtime test. Ghost request interception remains in ConnectionsManager, with Ayu per-dialog rules unchanged. Upload boost is unchanged. Enhanced download mode explicitly opts out of the ordinary byte budget so its 512 KiB/eight-request policy survives. Ordinary downloads retain the upstream Java/JNI/native budgeting and eight download connections. Legacy voice recording remains selected when the MSNgram enhancement/custom-bitrate controls require it.

ProxySettings and all active proxy consumers now use typed settings. Legacy saved WebProxy preferences infer WEB from port zero and a nonempty secret. Transport/tester implementations are unchanged; startup and proxy switching still route through the local transport. Stale proxy-for-calls row references were removed because typed proxy settings now own that property.

Custom QR and forwarding Lottie callers use the new generated-resource constructor. Both round-video implementations implement the initial camera choice required by the existing chat control. Wallet authentication uses AndroidX's direct FingerprintManager compatibility callback for Android 8–10, retaining its own callback/cancellation and credential fallback without borrowing BotBiometry's activity callback; Android 11+ retains platform BiometricPrompt.

## Pinned target differences

The generated `tgnet/tl` tree and native ApiScheme/MTProtoScheme cpp+h match the pinned target exactly. TLRPC layer is 232, but the enclosing TLRPC file deliberately differs: MSNgram retains Ayu deleted-message flags and translated message/poll fields, its OSMDroid map integration and existing developer/bot-auth policy. The constructor/schema evolution comes from the actual official update chain.

Native networking differs from Nagram's custom snapshot: MSNgram retains ten-account static instances, ten proxy-check connections, ten-second proxy timeout and existing IPv4/IPv6 retry behavior. Nagram's 128-account dynamic allocation and session import/export additions are not part of this baseline-preservation migration. Download budgeting and TLSHello changes from the official chain are integrated. The custom group voice-engine include now follows the moved tgcalls submodule, and the group bitrate patch task is retained.

The target snapshot has 4,112 differing paths at source checkpoint `4f14b72ff550893dc97e62e46b0640817efb9f04`, including resources/build layout and different fork implementations. Full Nagram custom-feature parity is not established by the official-chain import or these selected comparisons. Do not describe the two source trees as identical.

## Validation limits

All 2,406 Java files parse with zero syntax errors; this is not compilation. Signed CI compiles Kotlin/Java, checks duplicate classes, then assembles each ABI and verifies signature, package, version, minimum SDK, label, icon resources, native libraries and WebProxy dex descriptors. Actual run conclusions and artifact checks must be recorded separately. Device checks remain necessary for upgrade/database migration, deleted/edited history, ghost behavior, accelerated downloads/uploads, both recorders, wallet unlock and WebProxy connectivity. No merge or publication is authorized.
