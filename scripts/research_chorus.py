from __future__ import annotations

"""Research chorus cue points without downloading audio or storing lyrics.

LRCLIB exposes line-synchronised lyric timestamps for some tracks, while
Musixmatch exposes verified section structure for some of the same tracks. This
script aligns the first Musixmatch chorus (and an immediately following hook)
to LRCLIB timestamps, then falls back to repeated lyric blocks. It stores only
cue seconds in songs.json and leaves tracks without a synchronised source
alone. Every generated cue should still be spot-checked against the selected
official YouTube source before being treated as exact.
"""

import json
import re
import time
import unicodedata
from pathlib import Path
from typing import Any
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
SONGS_PATH = ROOT / "songs.json"
API_URL = "https://lrclib.net/api/search"
HEADERS = {"User-Agent": "snowman-intro-quiz-research/1.0 (https://github.com/exkawaii/snowman-intro-quiz)"}
MUSIXMATCH_HEADERS = HEADERS


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).casefold()
    value = re.sub(r"\([^)]*\)|（[^）]*）", "", value)
    return re.sub(r"[^0-9a-zA-Zぁ-んァ-ヶ一-龠]+", "", value)


def parse_lrc(value: str) -> list[tuple[float, str]]:
    lines: list[tuple[float, str]] = []
    for raw in value.splitlines():
        match = re.match(r"\[(\d+):(\d+(?:\.\d+)?)\]\s*(.*)", raw)
        if not match or not match.group(3).strip():
            continue
        seconds = int(match.group(1)) * 60 + float(match.group(2))
        lines.append((seconds, match.group(3).strip()))
    return lines


def normalize_line(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).casefold()
    value = value.replace("′", "'").replace("’", "'")
    value = re.sub(r"[\(\)（）\[\]「」『』\"“”]", "", value)
    return re.sub(r"[^0-9a-zA-Zぁ-んァ-ヶ一-龠]+", "", value)


def line_matches(left: str, right: str) -> bool:
    a, b = normalize_line(left), normalize_line(right)
    if not a or not b:
        return False
    return a == b or (len(a) >= 12 and (a in b or b in a))


def parse_structure(song_title: str) -> list[dict[str, Any]] | None:
    slug = re.sub(r"[^0-9A-Za-zぁ-んァ-ヶ一-龠]+", "-", unicodedata.normalize("NFKC", song_title)).strip("-")
    url = f"https://www.musixmatch.com/lyrics/Snow-Man-7/{quote(slug, safe='')}"
    try:
        response = requests.get(url, headers=MUSIXMATCH_HEADERS, timeout=30)
        if not response.ok:
            return None
        document = BeautifulSoup(response.text, "html.parser")
        script = document.find("script", id="__NEXT_DATA__")
        if not script or not script.string:
            return None
        payload = json.loads(script.string)
        track_info = payload["props"]["pageProps"]["data"]["trackInfo"]["data"]
        track = track_info.get("track", {})
        if normalize(track.get("name", "")) != normalize(song_title):
            return None
        if "snowman" not in normalize(track.get("artistName", "")):
            return None
        structure = track_info.get("trackStructureList")
        return structure if isinstance(structure, list) else None
    except (OSError, ValueError, KeyError, TypeError, requests.RequestException):
        return None


def structure_cue(structure: list[dict[str, Any]], lines: list[tuple[float, str]]) -> dict[str, Any] | None:
    chorus_index = next((i for i, section in enumerate(structure) if str(section.get("title", "")).casefold() == "chorus"), None)
    if chorus_index is None:
        return None
    section_lines = [line.get("text", "") for line in structure[chorus_index].get("lines", []) if line.get("text")]
    if not section_lines:
        return None
    if chorus_index + 1 < len(structure) and str(structure[chorus_index + 1].get("title", "")).casefold() == "hook":
        section_lines += [line.get("text", "") for line in structure[chorus_index + 1].get("lines", []) if line.get("text")]

    best: tuple[int, int] | None = None
    for start in range(len(lines)):
        if lines[start][0] < 8 or not line_matches(section_lines[0], lines[start][1]):
            continue
        matched = 0
        for offset, text in enumerate(section_lines):
            if start + offset >= len(lines) or not line_matches(text, lines[start + offset][1]):
                break
            matched += 1
        if matched >= min(2, len(section_lines)) and (best is None or matched > best[1] or (matched == best[1] and start < best[0])):
            best = (start, matched)
    if best is None:
        return None
    start_index, matched = best
    start = lines[start_index][0]
    end_index = min(start_index + matched, len(lines) - 1)
    end = lines[end_index][0] if end_index > start_index else start + 30
    end = min(max(end, start + 20), start + 45)
    return {
        "youtubeStart": round(start, 2),
        "youtubeEnd": round(end, 2),
        "chorusTimingSource": "Musixmatch section structure + LRCLIB line-synchronised timestamps",
        "chorusTimingConfidence": "high",
        "chorusTimingLines": matched,
    }


def matching_runs(lines: list[tuple[float, str]]) -> list[dict[str, Any]]:
    normalized = [normalize(text) for _, text in lines]
    candidates: list[dict[str, Any]] = []
    for first in range(len(lines)):
        if not normalized[first]:
            continue
        for repeated in range(first + 1, len(lines)):
            if lines[repeated][0] - lines[first][0] < 25:
                continue
            if normalized[first] != normalized[repeated]:
                continue
            length = 0
            while (
                first + length < len(lines)
                and repeated + length < len(lines)
                and normalized[first + length]
                and normalized[first + length] == normalized[repeated + length]
            ):
                length += 1
            if length >= 3:
                candidates.append(
                    {
                        "first_index": first,
                        "repeat_index": repeated,
                        "length": length,
                        "start": lines[first][0],
                        "repeat_start": lines[repeated][0],
                    }
                )
    return candidates


def choose_cue(song_title: str, lines: list[tuple[float, str]]) -> dict[str, Any] | None:
    candidates = matching_runs(lines)
    if not candidates:
        return None

    longest = max(candidate["length"] for candidate in candidates)
    pool = [candidate for candidate in candidates if candidate["length"] >= longest - 1]
    candidate = min(pool, key=lambda item: item["start"])
    first = candidate["first_index"]
    end_index = min(first + candidate["length"], len(lines) - 1)
    start = candidate["start"]
    hook_index = None
    title_key = normalize(song_title)
    if len(title_key) >= 4:
        for index in range(first, end_index):
            if title_key in normalize(lines[index][1]):
                hook_index = index
                break
    if hook_index is not None:
        start = lines[hook_index][0]

    block_end = lines[end_index][0] if end_index > first else start + 30
    end = max(block_end, start + 28)
    end = min(end, start + 42)
    confidence = "high" if candidate["length"] >= 5 and hook_index is not None else "medium"
    return {
        "youtubeStart": round(start, 2),
        "youtubeEnd": round(end, 2),
        "chorusTimingSource": "LRCLIB line-synchronised lyrics; repeated chorus block",
        "chorusTimingConfidence": confidence,
        "chorusTimingLines": candidate["length"],
    }


def candidate_for_song(song: dict[str, Any]) -> dict[str, Any] | None:
    responses: list[dict[str, Any]] = []
    queries = [
        {"track_name": song["title"], "artist_name": "Snow Man"},
        {"track_name": song["title"]},
    ]
    seen_ids: set[Any] = set()
    for query in queries:
        try:
            response = requests.get(API_URL, params=query, headers=HEADERS, timeout=20)
            payload = response.json() if response.ok else []
        except (OSError, ValueError, requests.RequestException):
            payload = []
        if not isinstance(payload, list):
            continue
        for item in payload:
            if not isinstance(item, dict) or item.get("id") in seen_ids:
                continue
            seen_ids.add(item.get("id"))
            if normalize(item.get("trackName", "")) != normalize(song["title"]):
                continue
            if "snowman" not in normalize(item.get("artistName", "")):
                continue
            if item.get("syncedLyrics"):
                responses.append(item)
        time.sleep(0.25)

    if not responses:
        return None
    # Duplicate album entries normally contain the same line timings. Prefer
    # the entry with the most timestamped lines for a stable cue.
    source = max(responses, key=lambda item: len(parse_lrc(item.get("syncedLyrics", ""))))
    lines = parse_lrc(source["syncedLyrics"])
    structure = parse_structure(song["title"])
    cue = structure_cue(structure, lines) if structure else None
    cue = cue or choose_cue(song["title"], lines)
    time.sleep(0.25)
    if cue:
        cue["chorusTimingTrack"] = source.get("trackName")
        cue["chorusTimingAlbum"] = source.get("albumName")
        cue["chorusTimingDuration"] = source.get("duration")
    return cue


def main() -> None:
    data = json.loads(SONGS_PATH.read_text(encoding="utf-8"))
    songs = data.get("songs", [])
    found = 0
    unresolved: list[str] = []
    for index, song in enumerate(songs, start=1):
        for key in (
            "youtubeStart",
            "youtubeEnd",
            "chorusTimingSource",
            "chorusTimingConfidence",
            "chorusTimingLines",
            "chorusTimingTrack",
            "chorusTimingAlbum",
            "chorusTimingDuration",
        ):
            song.pop(key, None)
        cue = candidate_for_song(song)
        if cue:
            song.update(cue)
            found += 1
            print(f"[{index:03d}/{len(songs):03d}] {song['title']} -> {cue['youtubeStart']:.2f}-{cue['youtubeEnd']:.2f}s", flush=True)
        else:
            unresolved.append(song["title"])
            print(f"[{index:03d}/{len(songs):03d}] {song['title']} -> unresolved", flush=True)

    data["chorusTimingProvider"] = "Musixmatch section structure + LRCLIB synchronized lyric timestamps (cue seconds only; no lyrics stored)"
    data["chorusTimingMatches"] = found
    data["chorusTimingUnresolvedCount"] = len(unresolved)
    data["chorusTimingUnresolved"] = unresolved
    SONGS_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"timing cues: {found}/{len(songs)}; unresolved: {len(unresolved)}")


if __name__ == "__main__":
    main()
