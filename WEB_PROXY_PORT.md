# MSNgram WEB Proxy port

This fork adds the WEB Proxy implementation from [NextAlone/Nagram](https://github.com/NextAlone/Nagram) to [risin42/NagramX](https://github.com/risin42/NagramX).

Reference commit: `87863c8a57854c739e1452e56591c07ea52415d3`.

The following files are copied byte-for-byte from that reference:

- `TMessagesProj/src/main/java/org/telegram/utils/proxy/ProxySettings.java`
- `TMessagesProj/src/main/java/org/telegram/utils/proxy/WebProxyTransport.java`
- `TMessagesProj/src/main/java/org/telegram/utils/proxy/WebProxyConnectionTester.java`

The surrounding integration is adapted to MSNgram’s inherited `SharedConfig.ProxyInfo` model. WEB proxies are stored using port `0` with a nonempty secret, which preserves the existing proxy-list serialization format. SOCKS5 and MTProto proxies keep their existing format. The local bridge port is resolved at connection time and is never persisted as the remote endpoint.

Open Settings → Data and Storage → Proxy Settings → Add Proxy → WEB Proxy. Enter a compatible WEB proxy server address and its 16-byte MTProxy secret. Ordinary HTTP/SOCKS proxy servers cannot substitute for a WEB proxy endpoint. Import and sharing support `https://t.me/webproxy?...` and `tg://webproxy?...` links.

As in the upstream implementation, this is an experimental transport using an HTTPS page in a private WebView. A recent Android System WebView is required; upstream describes it as intended for foreground testing. Background delivery and device-specific behavior need real-device testing.

The **MSNgram Release APKs** GitHub Actions workflow builds signed ARM32 and ARM64 APKs on `dev` pushes or manual dispatch. MSNgram uses `com.msngram.messenger` and the stable fork signing key. It installs separately from the earlier WebProxy package. The workflow verifies build artifacts without publishing a GitHub release.

Validation performed during the port: byte equality for all three upstream files, XML parsing, and `git diff --check`. Build and live connection results must be checked separately. No live WEB proxy endpoint or Android device was supplied for an end-to-end connection test.

Original project license and attribution are retained.
