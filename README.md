# SNOW MAN // INTRO QUIZ

Snow Manの配信曲を使った、4択イントロクイズです。GitHub Pagesでビルド不要のまま公開できます。

## Features

- 曲名4択のイントロクイズ
- ランディングページとゲームページを分離
- 問題開始時にイントロを自動再生（12秒で自動停止）
- 10問 / 20問 / カスタム / 全曲（現在のカタログ全143曲）モード
- 正解するとジャケット画像、シングル・アルバム名、曲名を表示
- 正解後は公式YouTube音源を優先して埋め込み再生（143曲中137曲、未対応曲はApple Musicプレビュー）
- 音源ファイルはリポジトリへ保存せず、YouTube公式プレイヤーまたはApple Music / iTunes Search APIの公式プレビューを再生
- 正解・不正解、スコア、連続正解、自己ベストを表示
- キーボードの `1`〜`4` とスペースキーに対応
- Snow Man公式ディスコグラフィーの配信曲リストを含む

## Local preview

ブラウザのセキュリティ制限を避けるため、ローカルサーバー経由で開いてください。

```bash
cd snowman-intro-quiz
uv run python -m http.server 4173
```

その後、<http://localhost:4173> を開きます。トップページの「ゲームをはじめる」からゲーム画面へ移動します。

## GitHub Pagesで公開する手順

1. GitHubで `exkawaii/snowman-intro-quiz` という名前の新規Public repositoryを作成
2. このフォルダのファイルをそのリポジトリへpush
3. Repositoryの **Settings → Pages** を開く
4. **Build and deployment / Source** で `Deploy from a branch` を選択
5. Branchを `main`、Folderを `/ (root)` にして保存
6. 数分後、`https://exkawaii.github.io/snowman-intro-quiz/` で公開

コマンド例：

```bash
git init
git add .
git commit -m "Create Snow Man intro quiz"
git branch -M main
git remote add origin https://github.com/exkawaii/snowman-intro-quiz.git
git push -u origin main
```

## 曲データの更新

`songs.json` は **2026-09-07** 時点のスナップショットです。公式曲目、Apple Music / iTunes Search APIの30秒プレビュー、ジャケット画像、公式YouTube動画IDをまとめています。

曲目とAppleプレビューを更新したあと、YouTube公式動画IDを追加する場合：

```bash
uv run python scripts/build_catalog.py
uv run --with yt-dlp python scripts/collect_youtube.py
```

`collect_youtube.py` は音源をダウンロードせず、曲名一致かつSnow Man公式チャンネルの検索メタデータだけを取得します。

## Sources / rights note

- 曲名・配信情報: [Snow Man / MENT RECORDING Official Discography](https://mentrecording.jp/snowman/discography/)
- 未解禁曲72曲の公式発表: [MENT RECORDING News](https://mentrecording.jp/snowman/news/detail.php?id=1133666)
- YouTube埋め込み: [YouTube IFrame Player API](https://developers.google.com/youtube/iframe_api_reference)
- 試聴プレビュー: [iTunes Search API](https://performance-partners.apple.com/search-api) / [Snow Man on Apple Music](https://music.apple.com/jp/artist/snow-man/1772019148)

このプロジェクトはファン向けの非公式作品です。音源そのものはホスティングせず、YouTube公式プレイヤーを埋め込みます。公式動画がない曲は各サービスが提供する30秒プレビューをブラウザから参照します。YouTube APIや公式動画から音声を抽出・保存していません。配信状況、埋め込み可否、プレビューURL、曲名は提供元の変更により変わる可能性があります。
