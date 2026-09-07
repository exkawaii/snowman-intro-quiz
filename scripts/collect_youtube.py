from __future__ import annotations

import json
import re
import sys
import time
import unicodedata
from pathlib import Path

from yt_dlp import YoutubeDL

ROOT = Path(__file__).resolve().parents[1]
SONGS_PATH = ROOT / "songs.json"
OFFICIAL_CHANNELS = {"Snow Man", "Snow Man - Topic"}


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).casefold()
    return re.sub(r"[^0-9a-zA-Zぁ-んァ-ヶ一-龠]+", "", value)


def title_matches(song_title: str, video_title: str) -> bool:
    wanted = normalize(song_title)
    candidate = normalize(video_title)
    if not wanted:
        return False
    if wanted in candidate:
        return True
    # Common official-title aliases.
    aliases = {
        "オドロウゼ！": ["オドロウゼ!", "odorouse"],
        "グッタイム": ["goodtime", "good time"],
        "IX Guys Snow Man": ["Ⅸ Guys Snow Man"],
        "HELLO HELLO -Movie Ver.-": ["HELLO HELLO Movie Ver"],
        "YumYumYum ～SpicyGirl～": ["YumYumYum ~SpicyGirl~"],
        "地球(あい)してるぜ": ["地球してるぜ"],
    }
    return any(normalize(alias) in candidate for alias in aliases.get(song_title, []))


def score_candidate(song: dict, entry: dict) -> int:
    channel = entry.get("channel") or entry.get("uploader") or ""
    title = entry.get("title") or ""
    if channel not in OFFICIAL_CHANNELS or not title_matches(song["title"], title):
        return -1
    score = 100
    if normalize(title) == normalize(song["title"]):
        score += 40
    if "provided to youtube" in title.casefold():
        score += 5
    if "music video" in title.casefold() or "mv" in title.casefold():
        score += 3
    if "dance practice" in title.casefold() or "live" in title.casefold():
        score -= 2
    return score


def main() -> None:
    data = json.loads(SONGS_PATH.read_text(encoding="utf-8"))
    songs = data.get("songs", [])
    options = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "extract_flat": "in_playlist",
        "ignoreerrors": True,
    }
    found = 0
    failed = []
    with YoutubeDL(options) as ydl:
        for index, song in enumerate(songs, start=1):
            query = f"ytsearch5:Snow Man {song['title']}"
            try:
                result = ydl.extract_info(query, download=False) or {}
                entries = [entry for entry in result.get("entries", []) if entry]
                scored = sorted(((score_candidate(song, entry), entry) for entry in entries), key=lambda pair: pair[0], reverse=True)
                best_score, best = scored[0] if scored else (-1, None)
                if best and best_score >= 100:
                    song["youtubeVideoId"] = best.get("id")
                    song["youtubeTitle"] = best.get("title")
                    song["youtubeChannel"] = best.get("channel") or best.get("uploader")
                    song["youtubeDuration"] = best.get("duration")
                    song["youtubeUrl"] = f"https://www.youtube.com/watch?v={best.get('id')}"
                    found += 1
                else:
                    for key in ("youtubeVideoId", "youtubeTitle", "youtubeChannel", "youtubeDuration", "youtubeUrl"):
                        song.pop(key, None)
                    failed.append(song["title"])
                print(f"[{index:03d}/{len(songs):03d}] {song['title']} -> {song.get('youtubeVideoId', 'fallback')}", flush=True)
            except Exception as error:
                failed.append(song["title"])
                print(f"[{index:03d}/{len(songs):03d}] {song['title']} -> fallback ({error})", file=sys.stderr, flush=True)
            time.sleep(0.15)

    data["youtubeProvider"] = "YouTube official channel metadata (no audio downloaded)"
    data["youtubeOfficialMatches"] = found
    data["youtubeFallbackCount"] = len(failed)
    SONGS_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"matched {found}/{len(songs)} official YouTube videos; fallback {len(failed)}")
    if failed:
        print("fallback titles:", ", ".join(failed))


if __name__ == "__main__":
    main()
