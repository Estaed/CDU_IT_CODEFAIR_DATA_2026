# Spike: WebRTC DataChannel over a phone hotspot, no internet

This spike proves whether two phones (Android Chrome, iPhone Safari) joined to one
phone's personal hotspot can open a direct WebRTC DataChannel and chat without any
internet access, using no STUN/TURN server. A laptop on the same hotspot runs
`serve.py` only to relay the SDP offer/answer during the handshake; in production
that handshake is done by QR codes instead, so this server is test scaffolding, not
part of the product.

Run: `PYTHONUTF8=1 .venv/Scripts/python reports/spike-webrtc-hotspot/serve.py`

Phone steps: turn on phone A's personal hotspot (Wi-Fi, no internet backhaul needed);
join the laptop and phone B to that hotspot; run the command above on the laptop and
open the printed `http://<ip>:8000/` URL on both phones; press "I am A (offer)" on
phone A and "I am B (answer)" on phone B; once status says CONNECTED, chat both ways;
then Ctrl+C the server on the laptop and keep chatting to prove the path is
phone-to-phone, not routed through the laptop.

Result reading: if the channel reaches CONNECTED and messages keep flowing after the
server is killed, phone-to-phone WebRTC works on that hotspot with no STUN/TURN. If it
stays stuck on "checking" or reaches "failed", the hotspot is isolating clients from
each other or blocking mDNS candidate resolution; tick "Reveal real IPs" (grants a
throwaway microphone permission, stopped immediately) before pressing A/B and retry to
see whether real host IPs succeed where `.local` mDNS names did not.

## Manual mode (no laptop)

This proves the same thing with no laptop and no server at all: the SDP offer/answer
is carried by hand through a messaging app instead of `serve.py`. Everything runs from
`index.html` opened directly as a `file://` page.

1. Get `index.html` onto both phones (Quick Share, WhatsApp, email to self, any way)
   and open it in Chrome on each (Files app → open with Chrome, or Chrome's own
   Downloads screen).
2. Phone A turns its personal hotspot on. Phone B joins that hotspot's Wi-Fi.
3. On phone A, in the "Manual mode" section, tap **A: create offer**. Wait for the
   offer JSON to fill the first textarea, then tap **Copy offer** (this selects the
   textarea and uses `document.execCommand("copy")`, since the Clipboard API is not
   available on `file://`; if copy fails for any reason the text is already selected,
   so a long-press → Copy works too). Send that text to phone B, e.g. a WhatsApp
   "message to self" opened on both phones, or any chat both phones can see.
4. On phone B, paste the offer text into the "paste offer" textarea and tap
   **B: paste offer, create answer**. Wait for the answer JSON to fill the next
   textarea, tap **Copy answer**, and send that text back to phone A the same way.
5. On phone A, paste the answer text into the last textarea and tap
   **A: paste answer**.
6. Watch the status line: once it reads **CONNECTED**, the chat box below is live —
   type in both phones and confirm each message arrives on the other. CONNECTED means
   the hotspot allows its two clients to reach each other directly; nothing else is in
   the path.
7. If the status stays on "checking" or reaches "failed", the hotspot is isolating
   clients from one another or blocking mDNS candidate resolution. Tick "Reveal real
   IPs" (grants a throwaway microphone permission, stopped immediately) on both phones
   first, then repeat steps 3-5 with a fresh offer/answer to see whether real host IPs
   succeed where `.local` mDNS names did not.
8. The messaging app used to carry the offer/answer text needs the hotspot's mobile
   data only during that handshake (steps 3-5), to actually send and receive the
   WhatsApp messages. Once status reads CONNECTED, switch phone A's mobile data off:
   the data channel does not use it, so chat must keep working with the hotspot's
   mobile data off, proving the path is phone-to-phone Wi-Fi only.
