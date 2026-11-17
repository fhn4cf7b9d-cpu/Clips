#!/usr/bin/env python3
"""Viele Clips auf einmal: Layout + Untertitel + Piepton.

Aufruf: stapel.py auftrag.json
auftrag.json ist eine Liste wie:
  [{"nr": "09", "vorlage": "kamera-rechts", "hook1": "...", "hook2": "...",
    "start": 0, "dauer": 30, "hook_sek": 3}]
Quelle: gta6/quelle/<nr>-coachlim.mp4 und .words.json. Ausgabe: gta6/clips/<nr>-roh.mp4 und <nr>-fertig.mp4.
Fertige Clips werden uebersprungen. Eigene Ausschnitte: "cam", "inhalt", "oben_h" statt "vorlage".
"""
import json, os, subprocess, sys

# Ausschnitte in einem 1920x1080-Stream: Breite:Hoehe:X:Y
VORLAGEN = {
    # Facecam oben rechts (z. B. Elden Ring), Chat rechts wird weggeschnitten
    "kamera-rechts": {"cam": "592:328:1328:0", "inhalt": "908:1080:410:0", "oben_h": 640},
    # Facecam oben links, Shooter mit eingeblendeten Stream-Untertiteln unten (Valorant, CS2)
    "kamera-links-shooter": {"cam": "592:328:0:0", "inhalt": "908:940:600:0", "oben_h": 640},
    # Grosse Kamera oben rechts mit mehreren Leuten (Horror-Spiele), Kamera groesser
    "gruppe-rechts": {"cam": "680:380:1240:0", "inhalt": "908:1080:330:0", "oben_h": 800},
}

HIER = os.path.dirname(os.path.abspath(__file__))
WURZEL = os.path.dirname(HIER)
Q = os.path.join(WURZEL, "gta6", "quelle")
C = os.path.join(WURZEL, "gta6", "clips")


def main():
    auftraege = json.load(open(sys.argv[1], encoding="utf-8"))
    for a in auftraege:
        nr = a["nr"]
        v = dict(VORLAGEN.get(a.get("vorlage", ""), {}))
        v.update({k: a[k] for k in ("cam", "inhalt", "oben_h", "vollbild") if k in a})
        if not v.get("cam") and not v.get("vollbild"):
            print(f"{nr}: keine Vorlage und kein Ausschnitt, uebersprungen"); continue
        quelle = os.path.join(Q, f"{nr}-coachlim.mp4")
        roh = os.path.join(C, f"{nr}-roh.mp4")
        fertig = os.path.join(C, f"{nr}-fertig.mp4")
        if os.path.exists(fertig):
            print(f"{nr}: schon fertig"); continue
        if not os.path.exists(roh):
            ausschnitt = (["--vollbild", v["vollbild"]] if v.get("vollbild") else
                          ["--cam", v["cam"], "--inhalt", v["inhalt"], "--oben-h", str(v.get("oben_h", 640))])
            subprocess.run([sys.executable, os.path.join(HIER, "reaktions_layout.py"), "--quelle", quelle, *ausschnitt,
                            "--start", str(a.get("start", 0)), "--dauer", str(a["dauer"]),
                            "--hook1", a.get("hook1", ""), "--hook2", a.get("hook2", ""),
                            "--hook-sek", str(a.get("hook_sek", 3)), "--aus", roh], check=True)
        subprocess.run([sys.executable, os.path.join(HIER, "fertig_machen.py"), roh,
                        os.path.join(Q, f"{nr}-coachlim.words.json"), fertig,
                        "--start", str(a.get("start", 0))], check=True)


if __name__ == "__main__":
    main()
