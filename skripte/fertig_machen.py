#!/usr/bin/env python3
"""Rohclip -> fertiger Clip: Wort-Untertitel einbrennen und Schimpfwoerter im Ton wegpiepen.

Aufruf: fertig_machen.py <nr>-roh.mp4 woerter.json <nr>-fertig.mp4 [--start SEK] [--piep nein]
Die .ass-Datei landet neben der Ausgabe (<nr>.ass). Zeiten in woerter.json beziehen sich auf die Quelle,
--start ist der Clipstart in der Quelle (Standard 0).
"""
import argparse, json, os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from untertitel_ass import ist_schimpfwort

p = argparse.ArgumentParser()
p.add_argument("roh"); p.add_argument("json"); p.add_argument("aus")
p.add_argument("--start", type=float, default=0); p.add_argument("--piep", default="ja")
a = p.parse_args()
if os.path.exists(a.aus):
    sys.exit(f"{a.aus} gibt es schon. Ich überschreibe nichts.")

ordner = os.path.dirname(os.path.abspath(a.aus))
ass = os.path.join(ordner, os.path.basename(a.aus).replace("-fertig.mp4", "") + ".ass")
subprocess.run([sys.executable, os.path.join(os.path.dirname(__file__), "untertitel_ass.py"),
                a.json, ass, "--start", str(a.start)], check=True)

dauer = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", a.roh],
                             capture_output=True, text=True, check=True).stdout)
stellen = []
if a.piep == "ja":
    for w in json.load(open(a.json, encoding="utf-8")):
        s, e = w["s"] - a.start, w["e"] - a.start
        if ist_schimpfwort(w["w"]) and e > 0 and s < dauer:
            stellen.append((max(0, s), min(dauer, e)))  # genau so lang wie das Wort
an = "+".join(f"between(t,{s:.2f},{e:.2f})" for s, e in stellen) or "0"
audio = (f"[0:a]volume=0:enable='{an}'[stumm];"
         f"aevalsrc='0.25*sin(2*PI*1000*t)*gt({an},0)':s=48000:c=stereo:d={dauer:.2f}[piep];"
         f"[stumm][piep]amix=inputs=2:normalize=0:duration=first[a]")
video = f"[0:v]ass='{os.path.basename(ass)}'[v]"
cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-n", "-i", os.path.abspath(a.roh),
       "-filter_complex", video + ";" + audio, "-map", "[v]", "-map", "[a]",
       "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k",
       "-movflags", "+faststart", os.path.abspath(a.aus)]
try:
    subprocess.run(cmd, check=True, cwd=ordner)  # relativer ass-Pfad: kein Aerger mit C: unter Windows
except subprocess.CalledProcessError:
    if os.path.exists(a.aus):
        os.remove(a.aus)
    sys.exit("ffmpeg ist abgebrochen.")
print(f"Fertig: {a.aus} ({len(stellen)} Piepser)")
