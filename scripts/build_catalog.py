from __future__ import annotations

import json
import re
import unicodedata
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "songs.json"

# MENT RECORDING's official announcement of 72 previously unavailable tracks.
# Unit-member credits are kept separate so answer choices stay readable.
OFFICIAL_72 = [
    ("1st Debut Single", "Snow World", ""),
    ("3rd Single", "Big Bang Sweet", ""),
    ("4th Single", "YumYumYum ～SpicyGirl～", ""),
    ("5th Single", "Christmas wishes", ""),
    ("5th Single", "My Sweet Girl", ""),
    ("6th Single", "REFRESH", ""),
    ("6th Single", "From Today", ""),
    ("7th Single", "Wonderful! × Surprise!", ""),
    ("7th Single", "Feel the light, Lovely", ""),
    ("8th Single", "Luv Classic", ""),
    ("8th Single", "NO SURRENDER !", ""),
    ("9th Single", "ANY & EVERY", ""),
    ("9th Single", "ベストフレンド", ""),
    ("10th Single", "NEXT", ""),
    ("10th Single", "ココロヒトツ", ""),
    ("11th Single", "ドレス&タキシード", ""),
    ("11th Single", "What's your color?", ""),
    ("12th Single", "ばきゅん", ""),
    ("Snow Mania S1", "Infighter", ""),
    ("Snow Mania S1", "TIKI TIKI", ""),
    ("Snow Mania S1", "Delicious!!!", ""),
    ("Snow Mania S1", "HELLO HELLO -Movie Ver.-", ""),
    ("Snow Mania S1", "Be Proud!", ""),
    ("Snow Mania S1", "GRATITUDE", ""),
    ("Snow Mania S1", "Acrobatic", ""),
    ("Snow Mania S1", "Boogie Woogie Baby", ""),
    ("Snow Mania S1", "Vanishing Over", ""),
    ("Snow Mania S1", "IX Guys Snow Man", ""),
    ("Snow Mania S1", "Don't Hold Back", ""),
    ("Snow Mania S1", "Make It Hot", ""),
    ("Snow Mania S1", "Lock on!", ""),
    ("Snow Mania S1", "P.M.G.", "深澤辰哉 / 向井康二 / 宮舘涼太"),
    ("Snow Mania S1", "ADDICTED TO LOVE", "岩本照 / ラウール / 佐久間大介"),
    ("Snow Mania S1", "360m", "渡辺翔太 / 阿部亮平 / 目黒蓮"),
    ("Snow Labo. S2", "Toxic Girl", ""),
    ("Snow Labo. S2", "Brand New Smile", ""),
    ("Snow Labo. S2", "BOOM BOOM LIGHT", ""),
    ("Snow Labo. S2", "キッタキッテナイ", ""),
    ("Snow Labo. S2", "Movin' up", ""),
    ("Snow Labo. S2", "This is LOVE", ""),
    ("Snow Labo. S2", "HYPNOSIS", "岩本照 / 向井康二 / 目黒蓮"),
    ("Snow Labo. S2", "ガラライキュ！", "深澤辰哉 / ラウール / 渡辺翔太"),
    ("Snow Labo. S2", "Color me live...", "阿部亮平 / 宮舘涼太 / 佐久間大介"),
    ("i DO ME", "Super Deeper", ""),
    ("i DO ME", "8月の青", ""),
    ("i DO ME", "Two", "渡辺翔太 / 目黒蓮"),
    ("i DO ME", "Bass Bon", "ラウール / 佐久間大介"),
    ("i DO ME", "Vroom Vroom Vroom", "岩本照 / 深澤辰哉 / 宮舘涼太"),
    ("i DO ME", "Gotcha!", "向井康二 / 阿部亮平"),
    ("RAYS", "リンディーララ", ""),
    ("RAYS", "endless night", ""),
    ("RAYS", "君へ贈る応援歌", ""),
    ("RAYS", "これが愛じゃないのなら", ""),
    ("RAYS", "ROCK 'N' ROLL", ""),
    ("RAYS", "Wha cha cha", ""),
    ("RAYS", "KATANA", ""),
    ("RAYS", "GLITCH", "岩本照 / ラウール"),
    ("RAYS", "Hot Flow", "目黒蓮 / 佐久間大介"),
    ("RAYS", "ナイトスケープ", "深澤辰哉 / 阿部亮平 / 宮舘涼太"),
    ("RAYS", "星のうた", "渡辺翔太 / 向井康二"),
    ("音故知新", "Spark!!", ""),
    ("音故知新", "くちびる", ""),
    ("音故知新", "嫉妬ガール", ""),
    ("音故知新", "Miss Brand-New Friday Night", ""),
    ("音故知新", "約束は君と", ""),
    ("音故知新", "Days", ""),
    ("音故知新", "愛のせいで", ""),
    ("音故知新", "Symmetry", "岩本照 / 深澤辰哉"),
    ("音故知新", "ART", "阿部亮平 / 目黒蓮"),
    ("音故知新", "地球(あい)してるぜ", "宮舘涼太 / 佐久間大介"),
    ("音故知新", "サンシャインドリーマー", "ラウール / 渡辺翔太 / 向井康二"),
    ("音故知新", "Nine Snow Charge!!", ""),
]

# Recent releases and tracks listed in the official discography but not part of the 72-track announcement.
RECENT_OFFICIAL = [
    ("Snow Mania S1", "D.D.", ""),
    ("Snow Mania S1", "EVOLUTION", ""),
    ("Snow Labo. S2", "Secret Touch", ""),
    ("i DO ME", "あいことば", ""),
    ("RAYS", "EMPIRE", ""),
    ("音故知新", "TRUE LOVE", ""),
    ("音故知新", "BOOST", ""),
    ("音故知新", "悪戯な天使", ""),
    ("音故知新", "カリスマックス", ""),
    ("SERIOUS", "SERIOUS", ""),
    ("SERIOUS", "ばきゅん", ""),
    ("SERIOUS", "夏色花火", ""),
    ("SERIOUS", "Jack In The Box", ""),
    ("STARS", "STARS", ""),
    ("13th Single", "BANG!!", ""),
    ("13th Single", "SAVE YOUR HEART", ""),
    ("13th Single", "オドロウゼ！", ""),
    ("グッタイム", "グッタイム", ""),
    ("AMENITY", "グッタイム", ""),
    ("AMENITY", "ALL SUITE", ""),
    ("AMENITY", "オドロウゼ！", ""),
    ("AMENITY", "奇跡", ""),
    ("AMENITY", "BANG!!", ""),
    ("AMENITY", "SAVE YOUR HEART", ""),
    ("AMENITY", "GO HARD", ""),
    ("AMENITY", "マドラー", ""),
    ("AMENITY", "show time...", ""),
]

ALIASES = {
    "オドロウゼ!": "オドロウゼ！",
    "Ⅸ Guys Snow Man": "IX Guys Snow Man",
    "YumYumYum ~SpicyGirl~": "YumYumYum ～SpicyGirl～",
    "HELLO HELLO (Movie Ver.)": "HELLO HELLO -Movie Ver.-",
    "地球してるぜ": "地球(あい)してるぜ",
    "地球[ヨミ：あい]してるぜ": "地球(あい)してるぜ",
    "地球(あい)してるぜ": "地球(あい)してるぜ",
    "ガラライキュ!": "ガラライキュ！",
}


def canonical(title: str) -> str:
    title = unicodedata.normalize("NFKC", title).strip()
    title = ALIASES.get(title, title)
    return re.sub(r"\s+", " ", title)


def key(title: str) -> str:
    return canonical(title).casefold().replace(" ", "")


def get_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "snowman-intro-quiz-catalog/1.0"})
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.load(response)


def search(term: str, limit: int = 25) -> list[dict]:
    params = urllib.parse.urlencode({
        "term": term,
        "entity": "song",
        "country": "JP",
        "limit": limit,
        "lang": "ja_jp",
    })
    return get_json(f"https://itunes.apple.com/search?{params}").get("results", [])


def is_snow_man(result: dict) -> bool:
    artist = result.get("artistName", "")
    return artist == "Snow Man" or result.get("collectionName") in {
        "Snow Mania S1", "Snow Labo. S2", "i DO ME", "RAYS", "音故知新"
    } and any(name in artist for name in ["岩本", "深澤", "渡辺", "阿部", "宮舘", "佐久間", "向井", "目黒", "ラウール"])


def choose_result(results: list[dict], title: str, album: str | None = None, unit: bool = False) -> dict | None:
    wanted = key(title)
    candidates = [r for r in results if r.get("previewUrl") and key(r.get("trackName", "")) == wanted]
    if album:
        album_candidates = [r for r in candidates if r.get("collectionName") == album]
        candidates = album_candidates or candidates
    if unit:
        candidates = [r for r in candidates if r.get("artistName") != "Snow Man"] or candidates
    return candidates[0] if candidates else None


def main() -> None:
    raw_results = search("Snow Man", 200)
    records: dict[str, dict] = {}

    # First add the full Apple catalog snapshot for Snow Man as the broadest current streaming set.
    for result in raw_results:
        if result.get("artistName") != "Snow Man" or not result.get("trackName"):
            continue
        title = canonical(result["trackName"])
        records.setdefault(key(title), {
            "title": title,
            "credit": "",
            "release": result.get("collectionName", "Snow Man"),
            "previewUrl": result.get("previewUrl"),
            "trackViewUrl": result.get("trackViewUrl"),
            "artworkUrl": result.get("artworkUrl100"),
            "source": "Apple Music preview / iTunes Search API",
        })

    # Overlay official names and credits, then fill missing unit-song previews with precise searches.
    official_rows = OFFICIAL_72 + RECENT_OFFICIAL
    for album, title, credit in official_rows:
        title = canonical(title)
        record = records.setdefault(key(title), {
            "title": title,
            "credit": credit,
            "release": album,
            "previewUrl": None,
            "trackViewUrl": None,
            "artworkUrl": None,
            "source": "MENT RECORDING official discography",
        })
        record["title"] = title
        record["credit"] = credit
        if record.get("release") in (None, "", "Snow Man") or album in {"Snow Mania S1", "Snow Labo. S2", "i DO ME", "RAYS", "音故知新"}:
            record["release"] = album
        if record.get("previewUrl"):
            continue

        search_title = title
        if title == "地球(あい)してるぜ":
            search_title = "地球してるぜ"
        elif title == "IX Guys Snow Man":
            search_title = "Ⅸ Guys Snow Man"
        elif title == "HELLO HELLO -Movie Ver.-":
            search_title = "HELLO HELLO (Movie Ver.)"
        elif title == "YumYumYum ～SpicyGirl～":
            search_title = "YumYumYum ~SpicyGirl~"
        candidates = search(search_title, 25)
        chosen = choose_result(candidates, title, album if album in {"Snow Mania S1", "Snow Labo. S2", "i DO ME", "RAYS", "音故知新"} else None, bool(credit))
        if not chosen:
            # Search against the raw Apple spelling for aliases such as 地球してるぜ and ゆめ variants.
            chosen = next((r for r in candidates if r.get("previewUrl") and is_snow_man(r)), None)
        if chosen:
            record["previewUrl"] = chosen.get("previewUrl")
            record["trackViewUrl"] = chosen.get("trackViewUrl")
            record["artworkUrl"] = chosen.get("artworkUrl100")
            record["source"] = "MENT RECORDING official discography + Apple Music preview"

    # Keep a deterministic order: newest/current official additions first, then the remaining catalog alphabetically.
    official_keys = []
    for album, title, _ in official_rows:
        k = key(title)
        if k not in official_keys:
            official_keys.append(k)
    ordered = []
    for k in official_keys:
        if k in records:
            ordered.append(records.pop(k))
    ordered.extend(sorted(records.values(), key=lambda x: x["title"].casefold()))

    payload = {
        "artist": "Snow Man",
        "lastUpdated": date.today().isoformat(),
        "count": len(ordered),
        "previewProvider": "Apple Music / iTunes Search API",
        "songs": [dict({"id": f"song-{i+1:03d}", "highlightStart": 8}, **song) for i, song in enumerate(ordered)],
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    available = sum(bool(song.get("previewUrl")) for song in ordered)
    print(f"wrote {OUT} ({len(ordered)} tracks, {available} previews)")


if __name__ == "__main__":
    main()
