# 花の育成ゲーム『ふらわっち』

## 🌸 プロジェクト概要

植物の"種"から"花"までの成長をテーマにした、育成たまごっち型ゲームです。花の性格、形、色がプレイヤーの選択と環境で変わり、多様な進化やストーリーを楽しめます。

### ゲームの特徴
- **リアルタイム育成**: 花は時間とともに状態が変化
- **複数の育成要素**: 水、光を管理
- **成長段階システム**: 種→芽→茎→蕾→花の5段階成長（仕様は `docs/参考_成長段階.md`）
- **種の選択**: 4種類の種（太陽・月・風・雨）から選択
- **自動セーブ機能**: ゲームの進行状況が自動的に保存
- **直感的な操作**: シンプルなキー操作で花のお世話
- **ピクセルアート風UI**: レトロな見た目のゲーム画面

## 🚀 共同開発者向けクイックスタート

### 前提条件
- [Git](https://git-scm.com/) がインストールされていること
- [Docker](https://www.docker.com/) がインストールされていること
- GitHubアカウントを持っていること
- リポジトリへのコラボレーター権限が付与されていること

### 1. 環境セットアップ（GUI）

#### リポジトリのクローン
```bash
# Windows
git clone https://github.com/mrkaisp/tamagotchi-prototype.git
cd tamagotchi-prototype

# macOS
git clone https://github.com/mrkaisp/tamagotchi-prototype.git
cd tamagotchi-prototype
```

#### GUI表示の設定

**Windows:**
1. [VcXsrv](https://sourceforge.net/projects/vcxsrv/)をダウンロード・インストール
2. XLaunchを起動し、設定：
   - Step 1: 「Multiple windows」選択
   - Step 2: 「Start no client」選択
   - Step 3: 「Disable access control」と「Native opengl」にチェック
   - Step 4: 「Finish」クリック
3. 環境変数設定：
   ```cmd
   set DISPLAY=localhost:0.0
   ```

**macOS:**
1. [XQuartz](https://www.xquartz.org/)をダウンロード・インストール
2. XQuartzを起動
3. 環境変数設定：
   ```bash
   export DISPLAY=:0
   ```

#### Dockerコンテナの起動
```bash
# Docker Desktopを起動後
docker-compose -f docker-compose.macwin.yml up --build
```

### 2. 開発ワークフロー

#### 新しい機能開発の開始
```bash
# 最新のmainブランチを取得
git checkout main
git pull origin main

# 新しいfeatureブランチを作成
git checkout -b feature/新機能名
# 例: git checkout -b feature/add-minigame
```

#### 開発中の作業
```bash
# 変更を確認
git status

# 変更をステージング
git add ファイル名
# または全て: git add .

# コミット
git commit -m "feat: 新機能の説明"

# 定期的にコミット（作業中）
git commit -m "WIP: 作業中の機能"
```

#### 開発完了とプルリクエスト
```bash
# mainブランチの最新変更を取得
git checkout main
git pull origin main

# featureブランチに戻ってマージ
git checkout feature/新機能名
git merge main

# コンフリクトがあれば解決後コミット
git add .
git commit -m "merge: mainブランチの変更をマージ"

# GitHubにプッシュ
git push origin feature/新機能名
```

#### プルリクエストの作成
1. GitHubで「Pull requests」タブをクリック
2. 「New pull request」をクリック
3. ベースブランチ（main）と比較ブランチ（feature/新機能名）を選択
4. タイトルと説明を記入
5. 「Create pull request」をクリック

### 3. 開発ルール

#### ブランチ命名規則
```bash
feature/新機能名    # 新機能の追加
fix/バグ修正名      # バグ修正
docs/ドキュメント名  # ドキュメント更新
refactor/変更内容    # リファクタリング
test/テスト内容      # テスト追加
```

#### コミットメッセージの書き方
```bash
feat: 新しい機能を追加
fix: バグを修正
docs: ドキュメントを更新
style: コードスタイルを修正
refactor: コードをリファクタリング
test: テストを追加
WIP: 作業中の機能
```

#### ベストプラクティス
- **小さなコミット**: 機能ごとに分けてコミット
- **定期的なテスト**: 開発中は頻繁にテスト実行
- **ドキュメント更新**: コード変更に合わせてドキュメントも更新

### 4. 実行・テスト

```bash
# ゲーム起動
python -m src.main

# ユニットテスト
python -m pytest -q

# Docker 環境での起動/テスト
docker-compose -f docker-compose.macwin.yml up --build
```

## 🌸 開発者向け重要情報

### 描画制約（必須）
**必ず240ピクセル×240ピクセルの論理解像度で描画してください。**

- ゲームの論理解像度は240×240ピクセルに固定
- すべてのUI要素、キャラクター、テキストはこの範囲内に収める必要
- 物理的な画面サイズは4倍スケール（960×960ピクセル）で表示されるが、描画座標は240×240の範囲で計算

```python
# 正しい例：240×240の範囲内
pg.draw.rect(surface, color, (10, 10, 20, 20))  # 左上付近
pg.draw.rect(surface, color, (200, 200, 25, 25))  # 右下付近

# 間違った例：240×240の範囲外
pg.draw.rect(surface, color, (300, 300, 50, 50))  # 範囲外
```

### プロジェクト構造
```
src/
├── main.py # エントリーポイント
├── game/
│ ├── core/ # ゲームエンジンとコアシステム
│ │ ├── game_engine.py # メインゲームエンジン
│ │ ├── input_handler.py # 入力処理
│ │ └── event_system.py # イベントシステム
│ │ └── screen_state.py # 画面状態（追加）
│ ├── entities/ # ゲームエンティティ
│ │ └── flower.py # 花のメインクラス
│ ├── ui/ # UIシステム
│ │ ├── components.py # UIコンポーネント
│ │ ├── renderer.py # レンダリング管理
│ │ ├── display.py # ディスプレイ管理
│ │ └── font_manager.py # フォント管理
│ ├── data/ # データ管理
│ │ ├── config.py # 設定管理
│ │ └── save_manager.py # セーブデータ管理
│ └── utils/ # ユーティリティ
│ └── helpers.py # ヘルパー関数
```

### 画面遷移（`docs/01_UI定義書.md`）

- 00 タイトル → 01 種の選択 → 02 時間設定 → 03 メイン
- 03 メイン ←→ 04 設定 / 05 ステータス
- 03 メイン → 06 水やり / 07 光（自動戻り）
- 自動: 成長→09 花言葉選択 / 枯れ→10 死亡

### スクリーンショット生成

各画面のスクリーンショットを自動生成してレビュー用の画像ファイルとして保存できます。

```bash
# スクリーンショット生成
python -m src.game.utils.screenshot_generator
```

生成された画像は `docs/screenshots/` ディレクトリに保存されます。
- `title.png`: タイトル画面
- `seed_selection.png`: 種選択画面
- `main_seed.png`, `main_sprout.png`, `main_stem.png`, `main_bud.png`, `main_flower.png`: メイン画面（各成長段階）
- `settings.png`: 設定画面
- `status.png`: ステータス画面
- `mode_water.png`: 水やりモード
- `mode_light.png`: 光モード
- `flower_language.png`: 花言葉選択画面
- `death.png`: 死亡画面

### ゲームシステム詳細（仕様反映）

#### 花の状態管理
- **水の量 (Water Level)**: 0〜100
  - 自然変化: 1秒あたり -0.5
  - 水やり効果: +30.0
- **光の蓄積量 (Light Level)**: 0〜100
  - 光ON状態の間、光蓄積量が増加する
  - 光OFF状態では光蓄積量は維持される
  - 成長時にリセット
- **年齢**: ゲーム開始からの経過時間
- **成長段階**: 種→芽→茎→蕾→花

#### 成長条件（docs連携）
各成長段階で一定の光を与えることで次の段階に進みます（`docs/05_成長分岐表.md`）：
- 種→芽: 光20以上
- 芽→茎: 光40以上
- 茎→蕾: 光60以上
- 蕾→花: 光80以上

#### ゲームの操作方法（`docs/01_UI定義書.md`）
カーソル選択方式を採用。3ボタン操作で全機能を利用可能です。

- **ボタン操作**
  - `1` / `←`: カーソル移動（前の項目へ）
  - `2` / `Enter` / `Space`: 決定（選択中の項目を実行）
  - `3` / `→`: カーソル移動（次の項目へ）
  - `ESC`: ゲーム終了

- **画面遷移**
  - タイトル画面: ボタン2で種の選択へ
  - 種の選択: カーソルで種を選び、ボタン2で決定
  - 時間設定: カーソルで設定を選び、「決定」でメインへ
  - メイン画面: カーソルで機能を選択（水やり/光/設定/ステータス）

- **時間制御（時間設定画面から変更可能）**
  - 一時停止 ON/OFF
  - 時間スケール変更（x1.0 → x4.0 → x0.25）

#### 種の種類（`docs/03_キャラクター.md`）
- **太陽**: 明るく元気な花
- **月**: 神秘的な花
- **風**: 軽やかな花
- **雨**: しっとりとした花

#### 設定の変更（`src/game/data/config.py`）
```python
# src/game/data/config.py
@dataclass
class GameConfig:
    # ゲームバランス調整
    water_decay_rate: float = 0.2        # 水の自然減少率（1秒あたり）
    water_amount: float = 20.0            # 水やりの効果量
    light_amount: float = 1.0            # 光ON時の1秒あたりの光蓄積量
    
    # テスト用オプション
    nutrition_limit_disabled: bool = False  # Trueにすると1時間3回制限を無効化
```

**テスト用オプションの使い方:**
- `nutrition_limit_disabled = True` に設定すると、栄養行為（水やり/餌やり）の1時間3回制限が無効化されます
- テスト時に何回でも栄養行為を実行できるようになります
- 本番環境では `False` のままにしてください

**テスト用オプションの実行方法:**
1. `src/game/data/config.py` を開く
2. `GameConfig` クラスの `nutrition_limit_disabled` を `True` に変更
3. ゲームを起動: `python -m src.main`
4. テスト完了後、`nutrition_limit_disabled` を `False` に戻す

## 🛠️ 技術スタック

- **Python 3.11**: メイン言語
- **Pygame 2.5.2**: ゲームエンジン
- **Docker**: 開発環境の統一
- **Git**: バージョン管理

## 🔧 トラブルシューティング

### GUIが表示されない場合
- VcXsrv/XQuartzが起動しているか確認
- 環境変数（DISPLAY）が正しく設定されているか確認
- ファイアウォールの設定を確認

### Git関連の問題
```bash
# 変更を破棄して最新の状態に戻す
git checkout -- ファイル名

# ブランチを削除
git branch -d ブランチ名

# リモートの最新状態を取得
git fetch origin
git reset --hard origin/main
```

### その他の問題
- **Dockerコンテナが起動しない**: Docker Desktopが起動しているか確認
- **ゲームがクラッシュする**: ログファイル（flower_game.log）を確認
- **パフォーマンスが悪い**: 他のアプリケーションを終了してリソースを確保

## ✅ 品質保証チェックリスト（納品前）

- 仕様整合
  - 画面遷移が `docs/01_UI定義書.md` と一致
  - 成長条件が `docs/05_成長分岐表.md` と一致
- 操作性
  - カーソル移動（1/← と 3/→）が全画面で正常動作
  - 決定ボタン（2/Enter/Space）で選択項目が実行される
  - 時間設定画面で一時停止/時間スケール変更が反映される
- 表示
  - 240×240 論理解像度で UI が収まっている
  - ステータス/設定/モード画面の表記が崩れていない
- データ
  - 自動セーブ/リセットの動作確認
  - セーブ破損時のバックアップ復元
- テスト
  - `python -m pytest -q` がグリーン
  - 主要ロジック（成長・行動・保存）のユニットテストが存在

## 📚 参考資料

- 仕様書（本リポジトリ内）
  - `docs/00_概要.md`
  - `docs/01_UI定義書.md`
  - `docs/02_状態パラメータ.md`
  - `docs/03_キャラクター.md`
  - `docs/04_フェーズ1.md` ～ `docs/04_フェーズ4.md`
  - `docs/04_成長分岐.md`
  - `docs/05_成長分岐表.md`
  - `docs/参考_成長段階.md`

- 外部ドキュメント
  - [Pygame公式ドキュメント](https://www.pygame.org/docs/)
  - [Python公式ドキュメント](https://docs.python.org/3/)
  - [Docker公式ドキュメント](https://docs.docker.com/)
  - [VcXsrv公式サイト](https://sourceforge.net/projects/vcxsrv/)
  - [XQuartz公式サイト](https://www.xquartz.org/)