# 花の育成ゲーム『ふらわっち』

## 🌸 プロジェクト概要

植物の"種"から"花"までの成長をテーマにした、育成たまごっち型ゲームです。花の性格、形、色、香り、用途などがプレイヤーの選択・環境によって変化し、多様な進化やストーリーを楽しめます。

### ゲームの特徴
- **リアルタイム育成**: 花は時間とともに状態が変化
- **複数の育成要素**: 水、光、雑草除去、害虫駆除を管理
- **成長段階システム**: 種→芽→茎→蕾→花の5段階成長
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

### 1. 環境セットアップ

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

### 4. Testの実行

```bash
# 機能開発中は定期的にテスト
python -m src.main

# テストファイルがある場合
python -m pytest tests/

# Docker環境でのテスト
docker-compose -f docker-compose.macwin.yml up --build
```

## 🌸 開発者向け重要情報

### 描画制約（必須）
**必ず128ピクセル×128ピクセルの論理解像度で描画してください。**

- ゲームの論理解像度は128×128ピクセルに固定
- すべてのUI要素、キャラクター、テキストはこの範囲内に収める必要
- 物理的な画面サイズは4倍スケール（512×512ピクセル）で表示されるが、描画座標は128×128の範囲で計算

```python
# 正しい例：128×128の範囲内
pg.draw.rect(surface, color, (10, 10, 20, 20))  # 左上付近
pg.draw.rect(surface, color, (100, 100, 25, 25))  # 右下付近

# 間違った例：128×128の範囲外
pg.draw.rect(surface, color, (200, 200, 50, 50))  # 範囲外
```

### プロジェクト構造
src/
├── main.py # エントリーポイント
├── game/
│ ├── core/ # ゲームエンジンとコアシステム
│ │ ├── game_engine.py # メインゲームエンジン
│ │ ├── input_handler.py # 入力処理
│ │ └── event_system.py # イベントシステム
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

### ゲームシステム詳細

#### 花の状態管理
- **水の量 (Water Level)**: 0〜100
  - 自然変化: 1秒あたり -0.5
  - 水やり効果: +30.0
- **光の蓄積量 (Light Level)**: 0〜100
  - 光を与える効果: +10.0
  - 成長時にリセット
- **雑草数 (Weed Count)**: 0〜5個
  - 自然発生: 低確率で増加
  - 除去効果: -2個
- **害虫数 (Pest Count)**: 0〜3個
  - 自然発生: 低確率で増加
  - 駆除効果: -2個
- **年齢**: ゲーム開始からの経過時間
- **成長段階**: 種→芽→茎→蕾→花

#### 成長条件
各成長段階で一定の光を与えることで次の段階に進みます：
- 種→芽: 光20以上
- 芽→茎: 光40以上
- 茎→蕾: 光60以上
- 蕾→花: 光80以上

#### ゲームの操作方法
- `1`: 水を与える
- `2`: 光を与える
- `3`: 雑草を除去する
- `4`: 害虫を駆除する
- `S`: 種を選択する（ゲーム開始時）
- `P`: 一時停止/再開
- `F1`: デバッグモード
- `ESC`: ゲーム終了

#### 種の種類
- **太陽**: 明るく元気な花
- **月**: 神秘的な花
- **風**: 軽やかな花
- **雨**: しっとりとした花

#### 設定の変更
```python
# src/game/data/config.py
@dataclass
class GameConfig:
    # ゲームバランス調整
    water_decay_rate: float = 0.5        # 水の自然減少率
    water_amount: float = 30.0           # 水やりの効果量
    light_amount: float = 10.0           # 光の効果量
    weed_removal_amount: int = 2         # 雑草除去の効果量
    pest_removal_amount: int = 2         # 害虫駆除の効果量
```

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

## 📚 参考資料

- [Pygame公式ドキュメント](https://www.pygame.org/docs/)
- [Python公式ドキュメント](https://docs.python.org/3/)
- [Docker公式ドキュメント](https://docs.docker.com/)
- [VcXsrv公式サイト](https://sourceforge.net/projects/vcxsrv/)
- [XQuartz公式サイト](https://www.xquartz.org/)