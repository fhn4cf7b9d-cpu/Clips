#!/usr/bin/env python3
"""Eigenes Erklaervideo 1080x1920 aus skript.json: Neon-Grafiken, KI-Stimme (Piper), Wort-Untertitel.

Aufruf (mit dem Python aus werkzeuge/): fakten_video.py gta6/eigene/<name>/skript.json
Ergebnis: <ordner>/video.mp4. Hinweis fuer TikTok: Beim Hochladen den Schalter fuer KI-Inhalte einschalten.
"""
import json, math, os, random, subprocess, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont

B, H, FPS = 1080, 1920, 30
HIER = os.path.dirname(os.path.abspath(__file__))
WURZEL = os.path.dirname(HIER)
STIMME = os.path.join(WURZEL, "werkzeuge", "stimmen", "de_DE-thorsten-high.onnx")
PIPER = os.path.join(WURZEL, "werkzeuge", "bin", "piper")
FETT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(g):
    return ImageFont.truetype(FETT, g)


def hintergrund(seed):
    random.seed(seed)
    img = Image.new("RGB", (B, H))
    d = ImageDraw.Draw(img)
    horizont = 1180
    oben, mitte, unten = (24, 6, 48), (196, 30, 120), (255, 150, 60)
    for y in range(horizont):  # Himmel: Lila -> Pink -> Orange
        t = y / horizont
        a, b, u = (oben, mitte, t / 0.6) if t < 0.6 else (mitte, unten, (t - 0.6) / 0.4)
        d.line([(0, y), (B, y)], fill=tuple(int(a[i] + (b[i] - a[i]) * u) for i in range(3)))
    for _ in range(90):  # Sterne
        x, y = random.randint(0, B), random.randint(0, 500)
        d.point((x, y), fill=(255, 255, 255))
    # Sonne mit Streifen
    sonne = Image.new("RGBA", (B, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sonne)
    r, cx, cy = 300, B // 2, horizont - 40
    for y in range(cy - r, cy + 1):
        t = (y - (cy - r)) / r
        farbe = (255, int(230 - 120 * t), int(90 - 40 * t), 255)
        w = int(math.sqrt(max(0, r * r - (y - cy) ** 2)))
        if t > 0.45 and int((y - cy) / 14) % 2 == 0:
            continue
        sd.line([(cx - w, y), (cx + w, y)], fill=farbe)
    glow = sonne.filter(ImageFilter.GaussianBlur(40))
    img.paste(glow, (0, 0), glow); img.paste(sonne, (0, 0), sonne)
    # Boden mit Neon-Gitter
    d.rectangle([0, horizont, B, H], fill=(14, 4, 30))
    for i in range(-14, 15):
        d.line([(B // 2 + i * 40, horizont), (B // 2 + i * 260, H)], fill=(0, 220, 255), width=3)
    y, s = horizont, 8
    while y < H:
        d.line([(0, y), (B, y)], fill=(255, 40, 160), width=3)
        y += s; s = int(s * 1.35) + 4
    # Palmen links und rechts: gebogener, schmaler werdender Stamm, haengende Blaetter
    dunkel = (12, 0, 24)
    for x0, sp in ((70, 1), (B - 70, -1)):
        hoehe = 760
        punkte = []
        for k in range(0, 61):
            t = k / 60
            x = x0 + sp * (150 * t * t)
            y = horizont + 40 - hoehe * t
            punkte.append((x, y)); r = 22 - 12 * t
            d.ellipse([x - r, y - r, x + r, y + r], fill=dunkel)
        kx, ky = punkte[-1]
        for winkel in (-170, -140, -110, -70, -40, -10, 20, 160, 200):
            a = math.radians(winkel)
            oben_rand, unten_rand = [], []
            for k in range(0, 21):
                t = k / 20
                l = 230 * t
                x = kx + l * math.cos(a)
                y = ky + l * math.sin(a) * 0.5 + 140 * t * t
                breite = 26 * math.sin(math.pi * t) + 2
                nx, ny = -math.sin(a), math.cos(a)
                oben_rand.append((x + nx * breite, y + ny * breite * 0.6))
                unten_rand.append((x - nx * breite, y - ny * breite * 0.6))
            d.polygon(oben_rand + unten_rand[::-1], fill=dunkel)
    return img


def text_mitte(d, y, text, f, fill, stroke=8, sfill=(0, 0, 0)):
    w = d.textbbox((0, 0), text, font=f, stroke_width=stroke)[2]
    d.text(((B - w) // 2, y), text, font=f, fill=fill, stroke_width=stroke, stroke_fill=sfill)


def szene_bild(sz, nr, pfad):
    img = hintergrund(nr)
    d = ImageDraw.Draw(img)
    # Label-Pille
    f = font(54)
    w = d.textbbox((0, 0), sz["label"], font=f)[2]
    x = (B - w) // 2
    d.rounded_rectangle([x - 34, 230, x + w + 34, 320], radius=45, fill=(0, 230, 255))
    d.text((x, 240), sz["label"], font=f, fill=(20, 0, 40))
    # Grosser Text, passend skaliert
    g = 170
    while g > 70 and d.textbbox((0, 0), sz["gross"], font=font(g), stroke_width=10)[2] > B - 80:
        g -= 6
    # Neon-Schein
    schein = Image.new("RGBA", (B, H), (0, 0, 0, 0))
    ImageDraw.Draw(schein).text(((B - d.textbbox((0, 0), sz["gross"], font=font(g))[2]) // 2, 420),
                                 sz["gross"], font=font(g), fill=(255, 60, 200, 255))
    schein = schein.filter(ImageFilter.GaussianBlur(18))
    img.paste(schein, (0, 0), schein)
    d = ImageDraw.Draw(img)
    text_mitte(d, 420, sz["gross"], font(g), (255, 255, 255), stroke=10, sfill=(120, 0, 90))
    k = 54
    while k > 30 and d.textbbox((0, 0), sz["klein"], font=font(k), stroke_width=6)[2] > B - 60:
        k -= 2
    text_mitte(d, 440 + g + 30, sz["klein"], font(k), (255, 240, 120), stroke=6)
    img.save(pfad)


def norm(w):
    return "".join(ch for ch in w.lower() if ch.isalnum())


def ausrichten(gehoert, soll):
    """Untertitel-Woerter aus dem Skript, Zeiten aus dem Transkript (difflib), Luecken interpoliert."""
    import difflib
    a = [norm(w["w"]) for w in gehoert]; b = [norm(w) for w in soll]
    zeiten = [None] * len(soll)
    for blk in difflib.SequenceMatcher(None, a, b, autojunk=False).get_matching_blocks():
        for k in range(blk.size):
            g = gehoert[blk.a + k]; zeiten[blk.b + k] = (g["s"], g["e"])
    # Luecken gleichmaessig zwischen bekannten Nachbarn verteilen
    i = 0
    while i < len(soll):
        if zeiten[i] is not None:
            i += 1; continue
        j = i
        while j < len(soll) and zeiten[j] is None:
            j += 1
        von = zeiten[i - 1][1] if i > 0 else 0.0
        bis = zeiten[j][0] if j < len(soll) else gehoert[-1]["e"]
        schritt = max(0.05, (bis - von) / (j - i))
        for k in range(i, j):
            zeiten[k] = (von + (k - i) * schritt, von + (k - i + 1) * schritt)
        i = j
    return [{"w": w, "s": round(s, 2), "e": round(e, 2), "p": 1.0} for w, (s, e) in zip(soll, zeiten)]


def lauf(cmd, **kw):
    subprocess.run(cmd, check=True, **kw)


def main():
    skript_pfad = sys.argv[1]
    ordner = os.path.dirname(os.path.abspath(skript_pfad))
    tmp = os.path.join(ordner, "bau"); os.makedirs(tmp, exist_ok=True)
    skript = json.load(open(skript_pfad, encoding="utf-8"))
    teile = []
    for i, sz in enumerate(skript["szenen"]):
        wav = os.path.join(tmp, f"s{i}.wav"); png = os.path.join(tmp, f"s{i}.png"); mp4 = os.path.join(tmp, f"s{i}.mp4")
        lauf([PIPER, "-m", STIMME, "-f", wav, "--sentence_silence", "0.25"], input=sz["sprache"].encode(),
             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        dauer = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", wav],
                                     capture_output=True, text=True).stdout) + 0.35
        szene_bild(sz, i, png)
        n = int(dauer * FPS)
        zoom = f"zoompan=z='1+0.06*on/{n}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={n}:s={B}x{H}:fps={FPS}"
        lauf(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-i", png, "-i", wav, "-filter_complex",
              f"[0:v]scale={B*2}:{H*2},{zoom},fade=t=in:st=0:d=0.25,format=yuv420p[v];[1:a]apad,atrim=0:{dauer:.2f},aresample=48000[a]",
              "-map", "[v]", "-map", "[a]", "-t", f"{dauer:.2f}", "-c:v", "libx264", "-crf", "20", "-c:a", "aac", mp4])
        teile.append(mp4)
        print(f"Szene {i}: {dauer:.1f} s")
    liste = os.path.join(tmp, "liste.txt")
    open(liste, "w").write("".join(f"file '{p}'\n" for p in teile))
    roh = os.path.join(tmp, "roh.mp4")
    lauf(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", liste, "-c", "copy", roh])
    # Wort-Untertitel aus der eigenen Stimme
    lauf([sys.executable, os.path.join(HIER, "transkript.py"), roh, "medium"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    wj = roh.rsplit(".", 1)[0] + ".words.json"
    ws = ausrichten(json.load(open(wj, encoding="utf-8")),
                    " ".join(sz.get("text", sz["sprache"]) for sz in skript["szenen"]).split())
    json.dump(ws, open(wj, "w", encoding="utf-8"), ensure_ascii=False)
    aus = os.path.join(ordner, "video.mp4")
    if os.path.exists(aus):
        os.remove(aus)
    lauf([sys.executable, os.path.join(HIER, "fertig_machen.py"), roh, wj, aus, "--piep", "nein"])
    print(" ".join(w["w"] for w in ws))


if __name__ == "__main__":
    main()
