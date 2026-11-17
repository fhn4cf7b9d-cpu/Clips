#!/usr/bin/env python3
"""Reaktions-Layout 1080x1920: Streamer oben, Inhalt unten, zwei Hook-Boxen an der Naht.

Zwei Arten von Quelle:
  A) Eine Datei (Stream mit Facecam und Inhalt im selben Bild):
     --quelle stream.mp4 --cam B:H:X:Y --inhalt B:H:X:Y   (Breite:Hoehe:X:Y in Pixeln, wie ffmpeg-crop)
  B) Zwei Dateien (Reaktion und Originalvideo getrennt):
     --oben reaktion.mp4 --unten original.mp4   (Ton kommt von --oben)

Gemeinsam:
  --start 00:12:30 --dauer 45 --hook1 "Zitat" --hook2 "Zuspitzung" --aus clips/01-roh.mp4
  --hook-sek 3  (wie lange die Hooks stehen bleiben, 0 = ganzer Clip)

Nur Material schneiden, das eine Kampagne oder der Rechteinhaber erlaubt.
Farb-Emojis kann ffmpeg-drawtext nicht zeichnen: Emojis in der Caption setzen, nicht im Hook.
"""
import argparse, os, subprocess, sys, tempfile, textwrap

B, H = 1080, 1920
OBEN_H = 640            # oberes Drittel fuer die Reaktion
UNTEN_H = H - OBEN_H    # 1280 fuer den Inhalt
SCHRIFTEN = [
    os.environ.get("HOOK_FONT", ""),
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial Black.ttf",
    "/Library/Fonts/Arial Black.ttf",
    "C:/Windows/Fonts/ariblk.ttf",
]


def schrift():
    for f in SCHRIFTEN:
        if f and os.path.exists(f):
            return f
    sys.exit("Keine Schrift gefunden. Setz HOOK_FONT auf eine .ttf-Datei.")


def fuellen(label_in, label_out, breite, hoehe):
    # proportional skalieren, dann beschneiden: nie verzerren
    return (f"[{label_in}]scale={breite}:{hoehe}:force_original_aspect_ratio=increase,"
            f"crop={breite}:{hoehe},setsar=1[{label_out}]")


def textbox(datei, font, y, groesse, textfarbe, boxfarbe, zeit):
    esc = lambda p: p.replace("\\", "/").replace(":", "\\:").replace("'", "\\'")
    return (f"drawtext=fontfile='{esc(font)}':textfile='{esc(datei)}':fontsize={groesse}:"
            f"fontcolor={textfarbe}:box=1:boxcolor={boxfarbe}:boxborderw=22:line_spacing=10:"
            f"x=(w-text_w)/2:y={y}{zeit}")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--quelle"); p.add_argument("--cam"); p.add_argument("--inhalt")
    p.add_argument("--oben"); p.add_argument("--unten")
    p.add_argument("--start", default="0"); p.add_argument("--dauer", type=float, required=True)
    p.add_argument("--hook1", default=""); p.add_argument("--hook2", default="")
    p.add_argument("--hook-sek", type=float, default=0)
    p.add_argument("--aus", required=True)
    p.add_argument("--oben-h", type=int, default=640, help="Hoehe des oberen Teils (Standard 640)")
    p.add_argument("--vollbild", help="Nur ein Ausschnitt B:H:X:Y aus --quelle, auf 1080x1920 gefuellt (Handkamera, IRL)")
    a = p.parse_args()
    global OBEN_H, UNTEN_H
    OBEN_H = max(320, min(1600, a.oben_h)) // 2 * 2
    UNTEN_H = H - OBEN_H

    if not 5 <= a.dauer <= 180:
        sys.exit("Dauer bitte zwischen 5 und 180 Sekunden.")
    if os.path.exists(a.aus):
        sys.exit(f"{a.aus} gibt es schon. Ich überschreibe nichts.")

    if a.quelle and a.vollbild:
        eingaben = ["-ss", a.start, "-t", str(a.dauer), "-i", a.quelle]
        filt = [f"[0:v]crop={a.vollbild}[v0]", fuellen("v0", "st", B, H)]
        OBEN_H = 650  # Hooks im oberen Drittel
    elif a.quelle and a.cam and a.inhalt:
        eingaben = ["-ss", a.start, "-t", str(a.dauer), "-i", a.quelle]
        filt = [f"[0:v]split=2[c0][i0]",
                f"[c0]crop={a.cam}[c1]", fuellen("c1", "cam", B, OBEN_H),
                f"[i0]crop={a.inhalt}[i1]", fuellen("i1", "inh", B, UNTEN_H)]
    elif a.oben and a.unten:
        eingaben = ["-ss", a.start, "-t", str(a.dauer), "-i", a.oben,
                    "-ss", a.start, "-t", str(a.dauer), "-i", a.unten]
        filt = [fuellen("0:v", "cam", B, OBEN_H), fuellen("1:v", "inh", B, UNTEN_H)]
    else:
        sys.exit("Entweder --quelle mit --cam und --inhalt, oder --oben und --unten angeben.")

    if not a.vollbild:
        filt.append("[cam][inh]vstack=inputs=2[st]")
    letzte = "st"
    tmp = tempfile.mkdtemp(prefix="hook_")
    font = schrift()
    zeit = f":enable='lt(t,{a.hook_sek})'" if a.hook_sek > 0 else ""
    boxen = []
    y = OBEN_H - 90  # Hook sitzt auf der Naht, wie im Vorbild
    for nr, (txt, tf, bf) in enumerate([(a.hook1, "black", "white"), (a.hook2, "white", "0xE8333A")]):
        if not txt.strip():
            continue
        zeilen = textwrap.wrap(txt, 22)
        d = os.path.join(tmp, f"h{nr}.txt")
        open(d, "w", encoding="utf-8").write("\n".join(zeilen))
        boxen.append(textbox(d, font, y, 62, tf, bf, zeit))
        y += len(zeilen) * 72 + 60
    if boxen:
        filt.append(f"[{letzte}]" + ",".join(boxen) + "[v]")
        letzte = "v"

    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-n", *eingaben,
           "-filter_complex", ";".join(filt), "-map", f"[{letzte}]", "-map", "0:a?",
           "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", a.aus]
    os.makedirs(os.path.dirname(os.path.abspath(a.aus)), exist_ok=True)
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError:
        if os.path.exists(a.aus):
            os.remove(a.aus)  # halbe Datei nicht liegen lassen
        sys.exit("ffmpeg ist abgebrochen. Ausschnitte und Quelle pruefen.")
    print(f"Fertig: {a.aus}")


if __name__ == "__main__":
    main()
