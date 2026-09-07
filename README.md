# SNOW MAN // INTRO QUIZ

Snow Manの配信曲を使った、4択イントロクイズです。GitHub Pagesでビルド不要のまま公開できます。

## Features

- 曲名4択のイントロクイズ
- 10問 / 20問 / 全曲（現在のカタログ全143曲）モード
- イントロは12秒で自動停止
- 正解・不正解、スコア、連続正解、自己ベストを表示
- キーボードの `1`〜`4` とスペースキーに対応
- 音源ファイルはリポジトリへ保存せず、Apple Music / iTunes Search APIの公式プレビューURLを再生
- Snow Man公式ディスコグラフィーの配信曲リストを含む

## Local preview

ブラウザのセキュリティ制限を避けるため、ローカルサーバー経由で開いてください。

```bash
cd snowman-intro-quiz
uv run python -m http.server 4173
```

その後、<http://localhost:4173> を開きます。

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

`songs.json` は **2026-09-07** 時点のスナップショットです。公式曲目とApple Music / iTunes Search APIのプレビューURLをまとめています。

更新したい場合は、ネットワーク接続がある状態で次を実行してください。

```bash
uv run python scripts/build_catalog.py
```

`build_catalog.py` はApple Musicの検索結果を取得し、Snow Man公式発表の曲名・ユニット曲クレジットを重ねて `songs.json` を再生成します。

## Sources / rights note

- 曲名・配信情報: [Snow Man / MENT RECORDING Official Discography](https://mentrecording.jp/snowman/discography/)
- 未解禁曲72曲の公式発表: [MENT RECORDING News](https://mentrecording.jp/snowman/news/detail.php?id=1133666)
- 試聴プレビュー: [iTunes Search API](https://performance-partners.apple.com/search-api) / [Snow Man on Apple Music](https://music.apple.com/jp/artist/snow-man/1772019148)

このプロジェクトはファン向けの非公式作品です。音源そのものはホスティングせず、各サービスが提供するプレビューをブラウザから参照しています。配信状況、プレビューURL、曲名は提供元の変更により変わる可能性があります。
