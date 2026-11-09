# MSNgram

<p align="center"><img src="docs/branding/MSNgram.png" width="192" alt="MSNgram ribbon M icon"></p>

MSNgram is an Android Telegram client based on [Nagram X](https://github.com/risin42/NagramX), with the WEB Proxy transport ported from [Nagram](https://github.com/NextAlone/Nagram).

- Telegram messaging with inherited customization and privacy settings.
- SOCKS5, MTProto and WEB Proxy connections.
- WEB Proxy import and sharing through `tg://webproxy` and `https://t.me/webproxy` links.
- Cyan, blue, and teal folded-ribbon M launcher icons and notification branding.

[Source](https://github.com/mbm110/MSNgram) · [Releases](https://github.com/mbm110/MSNgram/releases) · [Transport notes](WEB_PROXY_PORT.md)

## Installation identity

MSNgram uses the application ID `com.msngram.messenger`, version `13.1.2` (1270). It retains the package and signing key used by the previous MSNgram release, so compatible updates can be installed without removing the existing app. The release signing certificate SHA-256 is:

```text
2A:6A:D2:B3:B9:32:6C:C6:B0:CD:85:06:3D:A4:62:30:DD:C5:58:75:11:CB:97:8E:86:29:18:38:49:13:EF:AA
```

Existing release APKs retain their original names and contents. This source rebrand does not replace those binaries. The original upstream application has a different package/signing identity.

## WEB Proxy

Open Settings → Data and Storage → Proxy Settings → Add Proxy → WEB Proxy. Supply a compatible WEB Proxy server and its 16-byte MTProxy secret. Ordinary HTTP or SOCKS servers do not provide this transport.

A recent Android System WebView is required for WEB Proxy connections; see [WEB_PROXY_PORT.md](WEB_PROXY_PORT.md).

## Development

```bash
git clone --recursive --shallow-submodules https://github.com/mbm110/MSNgram.git
```

The dedicated **MSNgram Release APKs** workflow (`.github/workflows/webproxy.yml`) runs on pushes to `dev` or manual dispatch. It builds ARM32 and ARM64 signed APKs and checks the application label, package, signing certificate and native libraries. Building requires the existing `WEBPROXY_KEYSTORE_BASE64`, `WEBPROXY_KEYSTORE_PASSWORD` and `WEBPROXY_KEY_ALIAS` repository secrets. Preserve that signing key for installation updates. Do not commit keys or credentials.

For an independent fork, obtain Telegram API credentials from [my.telegram.org](https://my.telegram.org/auth), configure the properties expected by `TMessagesProj/build.gradle`, and use your own Firebase configuration where needed. The bundled Firebase project is inherited from upstream, with client package matching adjusted for this fork. Renaming the client package does not register a Firebase app; configure a project you control for production push delivery. Automatic upstream APK updates are disabled because their installation identity differs from MSNgram.

## Credits and license

MSNgram preserves the original project license and upstream contributions. See [LICENSE](LICENSE). Upstream channel and translation links in the About screen are labeled as upstream resources.

- [Telegram for Android](https://github.com/DrKLO/Telegram)
- [Nagram X](https://github.com/risin42/NagramX)
- [Nagram](https://github.com/NextAlone/Nagram)
- [AyuGram](https://github.com/AyuGram/AyuGram4A)
- [Cherrygram](https://github.com/arsLan4k1390/Cherrygram)
- [Dr4iv3rNope](https://github.com/Dr4iv3rNope/NotSoAndroidAyuGram)
- [exteraGram](https://github.com/exteraSquad/exteraGram)
- [Nekogram](https://github.com/Nekogram/Nekogram)
- [OctoGram](https://github.com/OctoGramApp/OctoGram)
