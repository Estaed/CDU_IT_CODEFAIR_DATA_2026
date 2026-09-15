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
