#!/usr/bin/env python3
"""Execute the production WEB tester with deterministic UI/transport seams."""
from pathlib import Path
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
sources = {
'org/telegram/messenger/AndroidUtilities.java': '''package org.telegram.messenger;
import java.util.*;
public class AndroidUtilities {
 public static List<Runnable> delayed = new ArrayList<>();
 public static void runOnUIThread(Runnable r) { r.run(); }
 public static void runOnUIThread(Runnable r, long delay) { delayed.add(r); }
 public static void cancelRunOnUIThread(Runnable r) { delayed.remove(r); }
 public static void fireNext() { delayed.remove(0).run(); }
}''',
'org/telegram/tgnet/RequestTimeDelegate.java': 'package org.telegram.tgnet; public interface RequestTimeDelegate { void run(long value); }',
'org/telegram/utils/proxy/ProxySettings.java': '''package org.telegram.utils.proxy;
public class ProxySettings {
 public enum Type { WEB }
 public Type getType() { return Type.WEB; }
 public boolean isValid() { return true; }
 public String getAddress() { return "fixture.example"; }
 public String getSecret() { return "fixture"; }
}''',
'org/telegram/utils/proxy/WebProxyTransport.java': '''package org.telegram.utils.proxy;
import java.util.*;
public class WebProxyTransport {
 public static List<ReadyCallback> ready = new ArrayList<>();
 public static int stops, starts;
 public static boolean failStart;
 public interface ReadyCallback { void onReady(); }
 public static int startConnectionCheck(String a, String s, ReadyCallback r) {
  starts++; ready.add(r); return failStart ? 0 : 12345;
 }
 public static void stopConnectionCheck() { stops++; }
}''',
'Fixture.java': '''import java.util.*;
import org.telegram.messenger.AndroidUtilities;
import org.telegram.utils.proxy.*;
import org.telegram.tgnet.RequestTimeDelegate;
public class Fixture {
 public static void main(String[] args) {
  WebProxyConnectionTester tester = WebProxyConnectionTester.getInstance();
  List<Long> results = new ArrayList<>();
  List<RequestTimeDelegate> nativeCallbacks = new ArrayList<>();
  ProxySettings settings = new ProxySettings();
  WebProxyConnectionTester.TestImplementation impl = (s,p,d) -> nativeCallbacks.add(d);
  tester.checkProxy(settings, results::add, impl);
  tester.checkProxy(settings, results::add, impl);
  WebProxyTransport.ready.get(0).onReady();
  AndroidUtilities.fireNext(); // first request times out before its delayed ready callback
  require(results.equals(Arrays.asList(-1L)), "timeout result");
  require(WebProxyTransport.starts == 2, "second request starts");
  AndroidUtilities.fireNext(); // stale first ready callback
  require(nativeCallbacks.isEmpty(), "stale ready must not check second request");
  WebProxyTransport.ready.get(1).onReady();
  AndroidUtilities.delayed.remove(0); // remove second ready timeout to advance 500ms callback
  AndroidUtilities.fireNext();
  require(nativeCallbacks.size() == 1, "second native check");
  RequestTimeDelegate second = nativeCallbacks.get(0);
  second.run(42);
  require(results.equals(Arrays.asList(-1L,42L)), "second succeeds");
  int stopped = WebProxyTransport.stops;
  second.run(99); // duplicate native completion
  require(WebProxyTransport.stops == stopped && results.size() == 2, "duplicate completion ignored");

  tester.checkProxy(settings, results::add, impl);
  WebProxyTransport.ready.get(2).onReady();
  AndroidUtilities.delayed.remove(0);
  AndroidUtilities.fireNext();
  RequestTimeDelegate old = nativeCallbacks.get(1);
  tester.checkProxy(settings, results::add, impl);
  AndroidUtilities.fireNext(); // native timeout starts next request with reused port
  stopped = WebProxyTransport.stops;
  old.run(1);
  require(WebProxyTransport.stops == stopped, "late completion must not stop reused-port request");
  require(results.equals(Arrays.asList(-1L,42L,-1L)), "no late result");
  AndroidUtilities.fireNext(); // next ready timeout drains queue
  WebProxyTransport.failStart = true;
  tester.checkProxy(settings, results::add, impl);
  require(results.equals(Arrays.asList(-1L,42L,-1L,-1L,-1L)), "zero-port startup reports failure");
  System.out.println("PASS: production WebProxyConnectionTester: ready timeout, stale ready, success, duplicate/late native callbacks, reused port, native timeout, zero-port startup");
 }
 static void require(boolean ok, String message) { if (!ok) throw new AssertionError(message); }
}'''
}
with tempfile.TemporaryDirectory(prefix='proxy-fixture-') as directory:
    directory = Path(directory)
    sources['org/telegram/utils/proxy/WebProxyConnectionTester.java'] = (root / 'TMessagesProj/src/main/java/org/telegram/utils/proxy/WebProxyConnectionTester.java').read_text()
    paths = []
    for name, content in sources.items():
        path = directory / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        paths.append(str(path))
    subprocess.run(['javac', '-d', str(directory), *paths], check=True)
    subprocess.run(['java', '-cp', str(directory), 'Fixture'], check=True)
