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

# The nine member solo tracks from THE BEST are explicit Apple records in the
# same generated song list as the group and unit catalog.
MEMBER_SOLO = [
    ("THE BEST 2020 - 2025", "7%", "岩本照", 1804833311),
    ("THE BEST 2020 - 2025", "iro iro", "深澤辰哉", 1804833312),
    ("THE BEST 2020 - 2025", "Induction", "ラウール", 1804833313),
    ("THE BEST 2020 - 2025", "オトノナルホウヘ", "渡辺翔太", 1804833314),
    ("THE BEST 2020 - 2025", "ファインダー", "向井康二", 1804833315),
    ("THE BEST 2020 - 2025", "いっそ、嫌いになれたら。", "阿部亮平", 1804833316),
    ("THE BEST 2020 - 2025", "朝の時間", "目黒蓮", 1804833317),
    ("THE BEST 2020 - 2025", "I・だって止まらない", "宮舘涼太", 1804833318),
    ("THE BEST 2020 - 2025", "守りたい、その笑顔", "佐久間大介", 1804833319),
]

# Display the first official single/album rather than a later compilation such as THE BEST.
# These names are intentionally the same labels used by Apple Music / the MENT discography.
CANONICAL_RELEASES: dict[str, str] = {}


def release_group(name: str, *titles: str) -> None:
    for title in titles:
        CANONICAL_RELEASES[title] = name


release_group("D.D. (Selected Edition) - Single", "Snow World", "D.D.", "Crazy F-R-E-S-H Beat")
release_group("Grandeur - EP", "Big Bang Sweet", "EVERYTHING IS EVERYTHING", "Grandeur", "ナミダの海を越えて行け")
release_group("HELLO HELLO - EP", "YumYumYum ～SpicyGirl～", "HELLO HELLO", "Hip bounce!!", "縁 -YUÁN-")
release_group("Secret Touch - EP", "Christmas wishes", "My Sweet Girl", "Secret Touch", "僕の彼女になってよ。")
release_group("ブラザービート - EP", "REFRESH", "From Today", "ブラザービート", "イチバンボシ")
release_group("オレンジkiss - EP", "Wonderful! × Surprise!", "Feel the light, Lovely", "オレンジkiss", "僕に大切にされてね。")
release_group("タペストリー / W - EP", "Luv Classic", "NO SURRENDER !", "タペストリー", "W")
release_group("Dangerholic - EP", "ANY & EVERY", "ベストフレンド", "DA BOMB", "Dangerholic")
release_group("LOVE TRIGGER / We'll go together - EP", "NEXT", "ココロヒトツ", "LOVE TRIGGER", "We'll go together")
release_group("BREAKOUT / 君は僕のもの - EP", "ドレス&タキシード", "What's your color?", "BREAKOUT", "君は僕のもの")
release_group("SERIOUS - EP", "ばきゅん", "SERIOUS", "夏色花火", "Jack In The Box")
release_group(
    "Snow Mania S1",
    "Infighter", "TIKI TIKI", "Delicious!!!", "HELLO HELLO -Movie Ver.-", "Be Proud!",
    "GRATITUDE", "Acrobatic", "Boogie Woogie Baby", "Vanishing Over", "IX Guys Snow Man",
    "Don't Hold Back", "Make It Hot", "Lock on!", "P.M.G.", "ADDICTED TO LOVE", "360m",
    "EVOLUTION", "Party! Party! Party!", "Snow Man's Life", "Sugar", "Super Sexy", "終わらない Memories",
)
release_group(
    "Snow Labo. S2",
    "Toxic Girl", "Brand New Smile", "BOOM BOOM LIGHT", "キッタキッテナイ", "Movin' up",
    "This is LOVE", "HYPNOSIS", "ガラライキュ！", "Color me live...", "Happy Birthday",
    "JUICY", "Tic Tac Toe", "ボクとキミと", "ミッドナイト・トレンディ",
)
release_group(
    "i DO ME",
    "あいことば", "Ready Go Round", "Super Deeper", "POWEEEEER", "slow...", "Julietta",
    "クラクラ", "8月の青", "Two", "Bass Bon", "Vroom Vroom Vroom", "Gotcha!",
    "Cry out", "Nine Snow Flash", "僕という名のドラマ",
)
release_group(
    "RAYS",
    "リンディーララ", "endless night", "君へ贈る応援歌", "これが愛じゃないのなら", "ROCK 'N' ROLL",
    "Wha cha cha", "KATANA", "GLITCH", "Hot Flow", "ナイトスケープ", "星のうた", "EMPIRE",
    "KANPAI Year!!", "スタートライン",
)
release_group("One - Single", "One")
release_group("KISSIN' MY LIPS / Stories - EP", "KISSIN' MY LIPS", "Stories", "ファンターナモーレ", "君の彼氏になりたい。")
release_group("音故知新", "Spark!!", "くちびる", "嫉妬ガール", "Miss Brand-New Friday Night", "約束は君と", "Days", "愛のせいで", "Symmetry", "ART", "地球(あい)してるぜ", "サンシャインドリーマー", "Nine Snow Charge!!")
release_group("TRUE LOVE - Single", "TRUE LOVE")
release_group("BOOST - Single", "BOOST")
release_group("悪戯な天使 - Single", "悪戯な天使")
release_group("カリスマックス - Single", "カリスマックス")
release_group("STARS - Single", "STARS")
release_group("BANG!! - Single", "BANG!!")
release_group("SAVE YOUR HEART - Single", "SAVE YOUR HEART")
release_group("オドロウゼ! - Single", "オドロウゼ！")
release_group("グッタイム - Single", "グッタイム")
release_group("AMENITY", "ALL SUITE", "奇跡", "GO HARD", "マドラー", "show time...")
release_group("CHARISMAX (English ver.) - Single", "CHARISMAX (English ver.)")
release_group("THE BEST 2020 - 2025", "A PIECE OF CAKE", "Dear,", "SBY")


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


def lookup_track(track_id: int) -> dict | None:
    params = urllib.parse.urlencode({"id": str(track_id), "entity": "song", "country": "JP"})
    results = get_json(f"https://itunes.apple.com/lookup?{params}").get("results", [])
    return next((result for result in results if result.get("trackId") == track_id), None)


def is_snow_man(result: dict) -> bool:
    artist = result.get("artistName", "")
    return artist == "Snow Man" or result.get("collectionName") in {
        "Snow Mania S1", "Snow Labo. S2", "i DO ME", "RAYS", "音故知新"
    } and any(name in artist for name in ["岩本", "深澤", "渡辺", "阿部", "宮舘", "佐久間", "向井", "目黒", "ラウール"])


def choose_result(results: list[dict], title: str, album: str | None = None, unit: bool = False) -> dict | None:
    wanted = key(title)
    candidates = [
        r for r in results
        if r.get("previewUrl") and key(r.get("trackName", "")) == wanted and is_snow_man(r)
    ]
    if album:
        album_candidates = [r for r in candidates if r.get("collectionName") == album]
        candidates = album_candidates or candidates
    if unit:
        candidates = [r for r in candidates if r.get("artistName") != "Snow Man"] or candidates
    return candidates[0] if candidates else None


def snapshot_record(song: dict, category: str) -> dict:
    fields = ("title", "credit", "release", "previewUrl", "trackViewUrl", "artworkUrl", "source")
    record = {field: song.get(field) for field in fields}
    record["category"] = category
    return record


def main() -> None:
    previous_group: dict[str, dict] = {}
    previous_solo: dict[str, dict] = {}
    if OUT.exists():
        try:
            previous = json.loads(OUT.read_text(encoding="utf-8"))
            for song in previous.get("songs", []):
                if not song.get("title") or not song.get("previewUrl"):
                    continue
                category = song.get("category", "group-unit")
                target = previous_solo if category == "member-solo" else previous_group
                target[key(song["title"])] = snapshot_record(song, category)
        except (OSError, json.JSONDecodeError):
            pass

    try:
        raw_results = search("Snow Man", 200)
    except Exception as error:
        if not previous_group:
            raise
        print(f"Apple catalog search unavailable; preserving the existing snapshot ({error})")
        raw_results = []
    records: dict[str, dict] = dict(previous_group)

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
            "category": "group-unit",
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
            "category": "group-unit",
            "source": "MENT RECORDING official discography",
        })
        record["title"] = title
        record["credit"] = credit
        record["category"] = "group-unit"
        if record.get("release") in (None, "", "Snow Man") or album in {"Snow Mania S1", "Snow Labo. S2", "i DO ME", "RAYS", "音故知新"}:
            record["release"] = album
        canonical_album = CANONICAL_RELEASES.get(title)
        if record.get("previewUrl") and (key(title) in previous_group or not canonical_album):
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
        try:
            candidates = search(search_title, 25)
        except Exception as error:
            print(f"Apple search unavailable for {title}; keeping the existing record ({error})")
            candidates = []
        target_album = canonical_album or (album if album in {"Snow Mania S1", "Snow Labo. S2", "i DO ME", "RAYS", "音故知新"} else None)
        chosen = choose_result(candidates, title, target_album, bool(credit))
        if not chosen:
            # Search against the raw Apple spelling for aliases such as 地球してるぜ and ゆめ variants.
            chosen = next((r for r in candidates if r.get("previewUrl") and is_snow_man(r)), None)
        if not chosen and title == "Two":
            # Apple search can intermittently omit this unit's preview; use its verified track ID.
            chosen = lookup_track(6769372001)
        if chosen:
            record["previewUrl"] = chosen.get("previewUrl")
            record["trackViewUrl"] = chosen.get("trackViewUrl")
            record["artworkUrl"] = chosen.get("artworkUrl100")
            record["source"] = "MENT RECORDING official discography + Apple Music preview"

    solo_records = []
    for album, title, member, track_id in MEMBER_SOLO:
        solo_key = key(title)
        if solo_key in previous_solo:
            solo_records.append(previous_solo[solo_key])
            continue
        try:
            result = lookup_track(track_id)
        except Exception as error:
            raise RuntimeError(f"Apple solo track lookup failed: {title} ({track_id})") from error
        if not result or result.get("artistName") != member or not result.get("previewUrl"):
            raise RuntimeError(f"Apple solo track verification failed: {title} ({track_id})")
        solo_records.append({
            "title": canonical(title),
            "credit": member,
            "release": album,
            "previewUrl": result.get("previewUrl"),
            "trackViewUrl": result.get("trackViewUrl"),
            "artworkUrl": result.get("artworkUrl100"),
            "category": "member-solo",
            "source": "Snow Man official discography + Apple Music preview",
        })

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
    ordered.extend(solo_records)

    for song in ordered:
        song.setdefault("category", "group-unit")
        canonical_release = CANONICAL_RELEASES.get(song["title"])
        if canonical_release:
            song["release"] = canonical_release

    group_unit_count = sum(song["category"] == "group-unit" for song in ordered)
    member_solo_count = sum(song["category"] == "member-solo" for song in ordered)
    payload = {
        "artist": "Snow Man",
        "lastUpdated": date.today().isoformat(),
        "count": len(ordered),
        "groupUnitCount": group_unit_count,
        "memberSoloCount": member_solo_count,
        "previewProvider": "Apple Music / iTunes Search API",
        "songs": [dict({"id": f"song-{i+1:03d}", "highlightStart": 0}, **song) for i, song in enumerate(ordered)],
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    available = sum(bool(song.get("previewUrl")) for song in ordered)
    print(f"wrote {OUT} ({len(ordered)} tracks, {available} previews)")


if __name__ == "__main__":
    main()
