#!/usr/bin/env python3
"""Wort-fuer-Wort-Untertitel (.ass) aus einer words.json von transkript.py.

Aufruf: untertitel_ass.py woerter.json aus.ass [--start SEK] [--ende SEK] [--zensur ja|nein]
  --start/--ende: Ausschnitt aus der Quelle; Zeiten werden auf den Clipstart (0) verschoben.
1 bis 3 Woerter je Einblendung, das gerade gesprochene Wort gelb, weiss mit schwarzem Rand.
"""
import argparse, json, re

ZENSUR = {  # Wortstamm -> Ersatz (Gross/Klein egal)
    "hurensohn": "H*rensohn", "nuttensohn": "N*ttensohn", "bastard": "B*stard",
    "fick": "F*ck", "fotze": "F*tze", "wichser": "W*chser", "missgeburt": "M*ssgeburt",
}


def zensiere(w):
    for stamm, ersatz in ZENSUR.items():
        if stamm in w.lower():
            return re.sub(stamm, ersatz, w, flags=re.I)
    return w


def zeit(t):
    t = max(0.0, t)
    h, r = divmod(t, 3600); m, s = divmod(r, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"


def gruppen(woerter, maxw=3, pause=0.6, maxz=15):
    g = []
    for w in woerter:
        neu = (not g or len(g[-1]) >= maxw
               or len(" ".join(x["w"] for x in g[-1])) + 1 + len(w["w"]) > maxz or w["s"] - g[-1][-1]["e"] > pause
               or re.search(r"[.!?,]$", g[-1][-1]["w"]))
        if neu:
            g.append([w])
        else:
            g[-1].append(w)
    return g


def main():
    p = argparse.ArgumentParser()
    p.add_argument("json"); p.add_argument("ass")
    p.add_argument("--start", type=float, default=0); p.add_argument("--ende", type=float, default=1e9)
    p.add_argument("--zensur", default="ja")
    a = p.parse_args()
    ws = [dict(w, s=w["s"] - a.start, e=w["e"] - a.start) for w in json.load(open(a.json, encoding="utf-8"))
          if w["s"] >= a.start and w["e"] <= a.ende and w["w"].strip()]
    for w in ws:
        w["w"] = w["w"].lstrip("-").strip()
        if a.zensur == "ja":
            w["w"] = zensiere(w["w"])

    kopf = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Wort,DejaVu Sans,88,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,7,2,2,60,60,480,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    zeilen = []
    gs = gruppen(ws)
    for n, g in enumerate(gs):
        ende_g = g[-1]["e"] + 0.15
        if n + 1 < len(gs):  # nie zwei Einblendungen gleichzeitig
            ende_g = min(ende_g, gs[n + 1][0]["s"])
        for i, w in enumerate(g):
            von = w["s"]
            bis = g[i + 1]["s"] if i + 1 < len(g) else ende_g
            text = " ".join(("{\\c&H00FFFF&}" + x["w"] + "{\\c&HFFFFFF&}") if j == i else x["w"]
                            for j, x in enumerate(g))
            zeilen.append(f"Dialogue: 0,{zeit(von)},{zeit(bis)},Wort,,0,0,0,,{text}")
    open(a.ass, "w", encoding="utf-8").write(kopf + "\n".join(zeilen) + "\n")
    print(f"{a.ass}: {len(zeilen)} Einblendungen")


if __name__ == "__main__":
    main()
