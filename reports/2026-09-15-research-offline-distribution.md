# Research — handing Crosscheck to a phone with no internet, and offline messaging

Checked 2026-09-15 (Eko, Fable 5.1) with the `research` skill. Reports only; decisions are
Tarik's and land in `docs/PRD.md` via `create-prd`/`create-architecture`, not here.

Question behind it: Tarik wants direction 1 for the last two weeks ("make the app arrive without
the internet and impress the judges with it"), not direction 2 ("grow the app, dynamic map").
Messaging is still on the table.

## Measured here first

| Artefact | Bytes | gzip -9 | xz -9e |
|---|---|---|---|
| `dist/index.html` (whole app, pack inlined) | 318,741 | 32,099 | 25,236 |
| `data/out/data_pack.json` alone | 260,161 | 17,262 | — |

So the *entire* app is 32 KB compressed. One static QR code holds at most 2,953 bytes (version
40, level L), so "the app inside a QR" is at least 11 version-40 codes, which phone cameras do
not read reliably. That literal idea is dead; the number itself is a pitch line.

Today the Share screen's QR encodes `APP_URL` (GitHub Pages), which **needs the internet and
Pages is not enabled yet** (`constants.md`). The QR on an offline-first app currently requires
a connection. That contradiction is the thing to fix.

## Claims, checked

### C1. A received `.html` file runs its JavaScript on an iPhone — **contradicted**
- Apple Community thread, 2025-07-21/22: "you can no longer open an HTML file directly with
  Safari (or Firefox) in iOS 18.5 … Quick Look is as close as you can get and it will not run
  JavaScript." <https://discussions.apple.com/thread/256102223>
- Vela Docs guide (2026): "Apple does not currently document a universal Open in Safari route
  for a local HTML file." <https://docs.vela.partners/blog/how-to-open-html-file-on-iphone>
- No source found saying iOS 26 reversed this. **TBD — needs validation on a real iPhone**
  (AirDrop `crosscheck.html`, open it, see whether the tabs render).
- **What it changes:** PRD §6 "phone-to-phone transfer by share sheet, opens in flight mode"
  holds on Android and probably fails on iPhone. Half the judges' phones are likely iPhones.
  Any file-based transfer (Quick Share, AirDrop, animated QR) hits this wall on iOS. The two
  routes that survive on iPhone are: a page served over `http://` from a local hotspot (real
  Safari, JS runs, Add to Home Screen works) and a PWA installed once from a URL.

### C2. A received `.html` runs in Chrome on Android — **confirmed, with a caveat**
- Chrome opens `content://` HTML from Files with JS and CSS once storage permission is granted;
  relative links to sibling files break since Android 10, which does not affect a single-file
  app. <https://support.google.com/chrome/thread/3131802?hl=en>,
  <https://www.quora.com/Why-cant-Chrome-read-a-local-HTML-file-on-Android>
- **What it changes:** Android-to-Android file share is a real path today.

### C3. Quick Share and AirDrop now interoperate without the internet — **confirmed (device-gated)**
- 9to5Google 2026-06-03: Pixel 10/9/9a/8a, Galaxy S26/S25/S24 (One UI 8.5), Z Fold/Flip 6–7,
  Xiaomi 17T Pro, OnePlus 15, Oppo Find X9, Vivo X300, Honor Magic V6. Both sides must be in
  "Everyone" mode. <https://9to5google.com/2026/06/03/android-airdrop-list-of-supported-devices/>
- MacRumors 2026-02-11 and 2026-05-12 corroborate the rollout.
  <https://www.macrumors.com/2026/02/11/airdrop-quick-share-interoperability-more-phones/>
- Non-supported Androids fall back to a QR that shares **via the cloud** (internet).
- **What it changes:** the transfer works; the file then meets C1 on the iPhone side.

### C4. Animated QR transfers a 32 KB file phone-to-phone in the browser — **confirmed**
- Decimen Optical Transfer, repo `bashalarmistalt/decimen-optical-transfer`, benchmark record
  2026-08-09 (v0.4.0): 199.2 KB/s sustained phone-to-phone, sender and receiver are plain web
  pages, camera permission only, fountain (LT) coded. AGPL-3.0 from v0.4.0; v0.3.0 and below
  MIT. Safari needs the WASM zxing path (no `BarcodeDetector`). Not encrypted.
  <https://github.com/bashalarmistalt/decimen-optical-transfer>,
  Tom's Hardware coverage (2026), explainx.ai write-up 2026-07-30.
- Older art: txqr (Go, 2018), qram (Digital Bazaar), qrs.
- **What it changes:** the receiver still needs a decoder page first (fetched once from a URL,
  so one internet touch), and the received file meets C1 on iPhone. Spectacular on stage,
  Android-only in practice, and AGPL is a licence we must not inline. Stretch goal at best.

### C5. An ESP32 or Pi captive-portal hotspot hands the app to any phone that joins — **confirmed**
- Standard pattern (PirateBox lineage): device runs an AP, a DNS server answering every name
  with itself, and an HTTP server that returns the page for `/generate_204`,
  `/hotspot-detect.html` etc.; the OS pops the "sign in to network" sheet automatically.
  <https://medium.com/engineering-iot/creating-a-captive-portal-on-esp32-a-complete-guide-9853a1534153>,
  <https://dev.to/devasservice/how-to-build-a-captive-portal-in-esp32-with-micropython-2dc1>,
  Pi Zero 2 W rebuild 2025 <https://github.com/teklynk/piratebox>
- Caveats from the Wireless Broadband Alliance and Apple forums: iOS opens the portal in the
  Captive Network Assistant, a mini WebKit view with no localStorage, no persistence, closes on
  app switch, and a **128 KB limit on the initial HTML resource** (2019 source; compressed vs
  uncompressed **TBD**; we are 318 KB raw / 32 KB gzipped). Android uses a Chrome Custom Tab,
  far more capable. <https://captivebehavior.wballiance.com/>,
  <https://enterprisenetworkingatlarge.wordpress.com/2019/03/30/the-128kb-limit-on-captive-portals-the-ios-misery/>
- The usual escape: the portal page says "tap Cancel → Use Without Internet, then open your
  browser"; DNS still answers every name, so real Safari/Chrome load the app, JS runs, and
  Add to Home Screen keeps it after the phone leaves the Wi-Fi.
- A phone hotspot cannot do this without root (Termux-Hotspot needs hostapd); an ESP32
  (~AUD 10–15, 4 MB flash) or a Pi Zero 2 W can.
- **What it changes:** this is the one route that reaches iPhone and Android with zero
  internet, and the QR on the Share screen can become a `WIFI:S:Crosscheck;T:nopass;;` join
  code that both cameras understand natively. It is also a real recommendation: a clinic or
  store could run the same box.

### C6. Web NFC can carry the app — **contradicted**
- NTAG216 holds 888 bytes; Web NFC is Chrome-on-Android only, no iOS path.
  <https://developer.chrome.com/docs/capabilities/nfc>, <https://nfcfyi.com/guide/web-nfc-api-guide/>
- A tag can only carry a URL, which needs the internet. Rejected.

### C7. Two browsers can message with no server at all — **still contradicted** (BACKLOG 2026-09-12 stands)
- qwbp (MIT, spec CC BY 4.0, iOS Safari 14.5+, Chrome Android 80+): WebRTC signalling by QR
  in 55–100 bytes, **but** the data path needs "Same Wi-Fi/LAN" or STUN (internet).
  <https://github.com/magarcia/qwbp>, <https://github.com/fta2012/serverless-webrtc-qrcode>
- With the C5 hotspot as the LAN, two phones could pair by QR and chat over a DataChannel
  with no internet and no server process. Whether the ESP32 soft-AP isolates clients from each
  other is **TBD**. Range is the Wi-Fi room. It is a demo, not a service.

### C8. Off-grid community messaging exists as licence-free hardware in Australia — **confirmed**
- Meshtastic: 915 MHz ANZ ISM band under ACMA LIPD class licence, 5–15 km node to node,
  AES-256 channels, phone app over Bluetooth, web client, ~200-byte payload per packet.
  <https://wireless.org.au/meshtastic/>, <https://meshtastic.org/docs/overview/>,
  <https://meshtastic.discourse.group/t/whats-the-text-limit/11440>; AU retailers stock
  nodes (Zero Disaster Australia, Bendigo Aerial).
- Serval Project (Flinders University, SA): Android mesh voice/text since 2010, tested at
  Arkaroola; page last updated 2020-09-23, maintenance status **unknown**.
  <https://www.flinders.edu.au/about/making-a-difference/serval-project>
- **What it changes:** the honest form of "messaging" for this project is a **recommendation
  with a size proof**: the Task-13 SMS text must fit one Meshtastic packet (≤200 bytes) to
  claim "the verdict travels over a community mesh". Building it means buying two nodes
  (shipping risk before 2026-10-07) and it sits outside the software gate.

## Where this belongs
- C1, C3: PRD §6 manual checklist (the iPhone case needs a test line and probably a rewrite).
- C5: a new PRD decision, if chosen — QR content (`WIFI:` join vs URL), a hardware line item,
  and a `pipeline`-independent `scripts/` or `hardware/` folder for the ESP32 firmware and its
  gzipped copy of `dist/index.html`. Part 2 "Entry points" would gain one line.
- C7, C8: PRD §8 stays as is; Recommendations section of the report gains Meshtastic/Serval
  with the ≤200-byte proof; optionally a Task for a "mesh-size" statement.
- C4, C6: nowhere; recorded here so they are not researched twice.
