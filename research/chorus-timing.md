# Chorus timing research

Date: 2026-09-07

## Result

- Catalog: 143 Snow Man tracks.
- Cue points added: 59 tracks.
- Unresolved: 84 tracks.
- Stored in `songs.json` as `youtubeStart` / `youtubeEnd` only; lyric text is not stored.
- A cue is used only when the track also has a selected official YouTube video. Tracks without a cue continue from the beginning of the official video.

## Method

1. Query LRCLIB's `/api/search` endpoint for the track title and Snow Man.
2. Select an exact Snow Man track record with `syncedLyrics` and parse its line timestamps.
3. Where Musixmatch exposes a verified `chorus` section, align its first chorus lines (plus an immediately following `hook`, when present) to the LRCLIB timestamps.
4. If no usable Musixmatch structure is available, find the earliest substantial block of lines that repeats later in the same song and use it as a chorus candidate.
5. Use the structural end or a 28–42 second window when the source does not expose a clear boundary.
6. Store seconds and the source/method label, never the lyric text.

Of the 59 cues, 28 use Musixmatch section structure and LRCLIB timestamps; 31 use the repeated-block fallback. Examples: `Grandeur` 46.52–77.38s, `LOVE TRIGGER` 57.43–88.96s, and `オレンジkiss` 70.39–90.39s.

These are research cues, not waveform-verified measurements. The official YouTube art track can differ from a streaming master by a small amount, so the values should be treated as approximate to the nearest second until manually auditioned.

## Why 84 remain unresolved

LRCLIB currently has no exact Snow Man synchronized-lyrics record for those titles, or only an unsynchronized/plain lyric record. Public song lyric pages identify chorus text but generally do not expose audio timestamps. YouTube's IFrame API exposes `startSeconds` and `endSeconds`, but not a semantic chorus marker, and the official art-track metadata does not provide one.

The update therefore does not invent timestamps for the remaining tracks. They use the full official YouTube source from its beginning, or Apple Music's official preview when YouTube is unavailable.

## Sources

- [Musixmatch — Grandeur / Snow Man](https://www.musixmatch.com/lyrics/Snow-Man-7/Grandeur) — example of verified `chorus` / `hook` section structure.
- [LRCLIB API documentation](https://lrclib.net/docs) — search response and `syncedLyrics` timestamp format; the API asks batch clients to identify themselves and throttle requests.
- [YouTube IFrame Player API reference](https://developers.google.com/youtube/iframe_api_reference) — `loadVideoById` with `startSeconds` / `endSeconds`, playback events, and embed requirements.
- [YouTube embedded player parameters](https://developers.google.com/youtube/player_parameters) — embedded players must have a viewport at least 200×200; `controls=0` only removes controls, not the player itself.
