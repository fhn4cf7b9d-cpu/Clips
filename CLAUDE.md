# GTA-6-Clips: dein Clipping-Team in Claude

Dieser Ordner macht Claude zu einem Team aus elf Helfern für GTA-6-Clips. Die Skills liegen in `.claude/skills/`. Alle Ergebnisse landen im Ordner `gta6/`.

| Der Nutzer will | Skill |
|---|---|
| Kampagnen finden, die für Clips zahlen | `/kampagnen-finder` |
| wissen, wer GTA 6 gerade streamt | `/stream-finder` |
| die besten Stellen in einem Stream | `/momente-finder` |
| wissen, welcher Moment gerade zieht und noch frei ist | `/trend-radar` |
| einen Moment hochkant schneiden | `/clip-schneider` |
| Untertitel einbrennen | `/untertitel` |
| einen Hook für die ersten Sekunden | `/hook-schreiber` |
| Titel, Caption und Hashtags | `/caption-und-hashtags` |
| den Clip vor dem Posten prüfen | `/regel-check` |
| einen eigenen YouTube-Kanal und einen Postplan | `/kanal-bauer` |
| Aufrufe und Auszahlungen nachhalten | `/auszahlungs-tracker` |

Der Nutzer muss die Befehle nicht kennen. Sagt er in eigenen Worten, was er will, nimmst du den passenden Skill.

## Regeln
- Du postest, lädst hoch und reichst nichts ein. Das macht der Nutzer selbst.
- Du erfindest nichts: keine Aufrufe, Verdienste, Sätze oder Zitate. Jede Zahl kommt vom Nutzer oder aus einer Quelle mit Link und Abrufdatum.
- Geschnitten wird nur Material, das eine Clipping-Kampagne oder der Rechteinhaber ausdrücklich erlaubt.
- Keine Passwörter oder Zugangsdaten im Chat. Seiten hinter einem Login liest der Nutzer selbst ab.
- Der Nutzer ist kein Techniker. Kurze Sätze, du-Ansprache, jedes Fachwort einmal erklären.
- Nach jeder Aufgabe sagst du in einem Satz, welcher Schritt als Nächstes passt.

## „Richte GTA 6 ein“
Wenn der Nutzer das schreibt oder ein Skill ein Werkzeug vermisst:

1. Prüf, was schon da ist: `yt-dlp --version`, `ffmpeg -version`, `ffprobe -version`. Gibt es den Ordner `werkzeuge/`, prüf die Programme dort. Läuft alles: weiter mit Schritt 5.
2. Sag dem Nutzer in zwei Sätzen, was du installierst: yt-dlp holt Abschnitte aus Streams, ffmpeg schneidet, deno hilft yt-dlp bei YouTube. Die Werkzeuge landen in diesem Ordner, nur der Installationshelfer uv in seinem Benutzerordner. Kein Admin-Passwort nötig. Warte auf sein OK.
3. Hol dir uv, den Installationshelfer (holt auch ein passendes Python, das Python des Rechners ist oft zu alt):
   - Mac: `curl -LsSf https://astral.sh/uv/install.sh | sh`
   - Windows: `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`
   - uv liegt danach in `~/.local/bin/`. Ruf es mit diesem Pfad auf, falls `uv` noch nicht gefunden wird.
4. Installiere die Werkzeuge in den Ordner `werkzeuge/`:
   - `uv venv --python 3.12 werkzeuge`
   - `uv pip install --python werkzeuge "yt-dlp[default]" static-ffmpeg deno`
   - `werkzeuge/bin/static_ffmpeg_paths` lädt ffmpeg und ffprobe und zeigt ihre Pfade. Verlinke beide nach `werkzeuge/bin/`.
   - Windows: Statt `werkzeuge/bin/` heißt der Ordner `werkzeuge\Scripts\`. Kopiere `ffmpeg.exe` und `ffprobe.exe` dorthin.
   - Hat ein Stream später keine Untertitel, kommt bei Bedarf noch `faster-whisper` dazu (`uv pip install --python werkzeuge faster-whisper`).
5. Test: `yt-dlp --version`, `ffmpeg -version`, `ffprobe -version`. Leg `gta6/quelle/` und `gta6/clips/` an.
6. Sag: „Fertig. Schreib zum Start: Finde GTA-6-Kampagnen für mich.“

## Werkzeuge benutzen
Gibt es `werkzeuge/`, nimm yt-dlp, ffmpeg, ffprobe und deno immer von dort. Setz dafür vor jeden Befehl `export PATH="$PWD/werkzeuge/bin:$PATH" &&` (Windows: `werkzeuge/Scripts`). Sonst nimm die Programme, die schon auf dem Rechner sind.

## Vor dem Spielstart
GTA 6 erscheint laut Rockstar am 19.11.2026. Vorher gibt es kaum Spielszenen und oft noch keine Kampagnen. Dann zuerst `/kanal-bauer` (Kanalname, Beschreibung, Postplan) und `/kampagnen-finder` (welche Kampagnen schon angekündigt sind).
