#!/usr/bin/env python3
"""Transkript mit Wortzeiten (faster-whisper). Aufruf: transkript.py clip.mp4 [modell] -> clip.words.json"""
import sys, json, subprocess
import numpy as np
from faster_whisper import WhisperModel
datei = sys.argv[1]; modell = sys.argv[2] if len(sys.argv) > 2 else "medium"
m = WhisperModel(modell, device="cpu", compute_type="int8")
roh = subprocess.run(["ffmpeg", "-v", "error", "-i", datei, "-ac", "1", "-ar", "16000", "-f", "f32le", "-"],
                     capture_output=True, check=True).stdout
audio = np.frombuffer(roh, dtype=np.float32)
segs, info = m.transcribe(audio, language="de", word_timestamps=True, vad_filter=True)
woerter = [{"w": w.word.strip(), "s": round(w.start, 2), "e": round(w.end, 2), "p": round(w.probability, 2)}
           for s in segs for w in (s.words or [])]
out = datei.rsplit(".", 1)[0] + ".words.json"
json.dump(woerter, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print(out, len(woerter), "Woerter")
print(" ".join(f"{x['w']}" for x in woerter))
