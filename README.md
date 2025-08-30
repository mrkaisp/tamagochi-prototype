# たまごっちプロトタイプ

## 🎮 ゲーム概要

このプロジェクトは、クラシックなたまごっち風のペット育成ゲームです。デジタルペットを育て、餌を与え、遊び、掃除して、幸せで健康な状態を保ちましょう。

### ゲームの特徴
- **リアルタイム育成**: ペットは時間とともに状態が変化します
- **複数のケア要素**: 空腹度、幸福度、清潔度、健康状態を管理
- **自動セーブ機能**: ゲームの進行状況が自動的に保存されます
- **直感的な操作**: シンプルなキー操作でペットのお世話ができます
- **ピクセルアート風UI**: レトロな見た目のゲーム画面

## AI開発者向け重要制約

### 描画制約
**必ず128ピクセル×128ピクセルの論理解像度で描画してください。**

- ゲームの論理解像度は128×128ピクセルに固定されています
- すべてのUI要素、キャラクター、テキストはこの範囲内に収める必要があります
- 物理的な画面サイズは4倍スケール（512×512ピクセル）で表示されますが、描画座標は128×128の範囲で計算してください
- この制約を守らないと、ゲーム画面が正しく表示されません

### 座標系の例
```python
# 正しい例：128×128の範囲内
pg.draw.rect(surface, color, (10, 10, 20, 20))  # 左上付近
pg.draw.rect(surface, color, (100, 100, 25, 25))  # 右下付近

# 間違った例：128×128の範囲外
pg.draw.rect(surface, color, (200, 200, 50, 50))  # 範囲外
```

## ゲームシステム詳細

### ペットの状態管理

#### 基本統計情報
- **空腹度 (Hunger)**: 0（満腹）〜 100（腹ペコ）
  - 自然変化: 1秒あたり +2.0
  - 餌効果: -35.0
- **幸福度 (Happiness)**: 0 〜 100
  - 自然変化: 1秒あたり -1.0
  - 遊び効果: +25.0
- **清潔度 (Cleanliness)**: 0 〜 100
  - 自然変化: 1秒あたり -0.5
  - 掃除効果: +60.0
- **年齢**: ゲーム開始からの経過時間
- **うんち数 (Poop Count)**: 0 〜 3個
  - 餌を食べると +1
  - 掃除すると 0にリセット
- **病気状態 (Is Sick)**: 健康/病気

#### 病気判定条件
以下のいずれかの条件を満たすと病気になります：
- 空腹度 ≥ 85.0
- 清潔度 ≤ 25.0
- うんち数 > 3個

#### 健康状態表示
- **病気**: 病気状態
- **空腹**: 空腹度 > 80
- **汚い**: 清潔度 < 30
- **悲しい**: 幸福度 < 30
- **健康**: 上記以外

### ゲームの操作方法
- `1`: 餌を与える
- `2`: 遊ぶ
- `3`: 掃除する
- `4`: 薬を与える（病気時のみ効果）
- `P`: 一時停止/再開
- `F1`: デバッグモード
- `ESC`: ゲーム終了

### ゲーム画面構成
- **メイン画面**: 128×128ピクセルの論理解像度
- **スケール**: 4倍拡大表示（512×512ピクセル）
- **フレームレート**: 30 FPS
- **UI要素**:
  - ペットのキャラクター表示
  - 状態バー（空腹度、幸福度、清潔度）
  - 年齢表示
  - うんちアイコン
  - 健康状態表示

## 🚀 開発環境のセットアップ

### 前提条件
- [Git](https://git-scm.com/) がインストールされていること
- [Docker](https://www.docker.com/) がインストールされていること
- [Cursor](https://cursor.sh/) エディタ（推奨）

### 1. リポジトリのクローン

#### Windowsの場合
1. **ターミナルを開く**
   - Windowsキー + R を押す
   - `cmd` と入力してEnter
   - または、Windowsキーを押して「コマンドプロンプト」を検索して開く

2. **作業ディレクトリに移動**
   ```cmd
   cd C:\Users\ユーザー名\Desktop
   ```

3. **リポジトリをクローン**
   ```cmd
   git clone https://github.com/your-username/tamagotchi-prototype.git
   cd tamagotchi-prototype
   ```

#### macOSの場合
1. **ターミナルを開く**
   - Finderを開く
   - アプリケーション → ユーティリティ → ターミナルをダブルクリック
   - または、Spotlight（Cmd + Space）で「ターミナル」を検索

2. **作業ディレクトリに移動**
   ```bash
   cd ~/Desktop
   ```

3. **リポジトリをクローン**
   ```bash
   git clone https://github.com/your-username/tamagotchi-prototype.git
   cd tamagotchi-prototype
   ```

### 2. GUI表示の設定

#### Windowsの場合
1. **VcXsrvをインストール**
   - [VcXsrv公式サイト](https://sourceforge.net/projects/vcxsrv/)にアクセス
   - 「Download」ボタンをクリック
   - ダウンロードしたファイルを実行してインストール

2. **XLaunchを起動**
   - スタートメニューから「XLaunch」を検索して起動
   - または、デスクトップの「XLaunch」アイコンをダブルクリック

3. **XLaunchの設定**
   - **Step 1**: 「Multiple windows」を選択 → 「Next」
   - **Step 2**: 「Start no client」を選択 → 「Next」
   - **Step 3**: 「Extra settings」で以下をチェック：
     - ✅ 「Disable access control」
     - ✅ 「Native opengl」
   - **Step 4**: 「Finish」をクリック

4. **環境変数を設定**
   ```cmd
   set DISPLAY=localhost:0.0
   ```

#### macOSの場合
1. **XQuartzをインストール**
   - [XQuartz公式サイト](https://www.xquartz.org/)にアクセス
   - 「XQuartz-2.8.5.dmg」をダウンロード
   - ダウンロードしたファイルをダブルクリック
   - インストーラーを実行

2. **XQuartzを起動**
   - アプリケーション → ユーティリティ → XQuartzをダブルクリック
   - 初回起動時は設定をそのまま「OK」で進める

3. **環境変数を設定**
   ```bash
   export DISPLAY=:0
   ```

### 3. Dockerコンテナの起動

#### Windowsの場合
1. **Docker Desktopを起動**
   - Windowsキーを押して「Docker Desktop」を検索
   - Docker Desktopをダブルクリックして起動
   - タスクバーにDockerのアイコンが表示されるまで待つ

2. **ターミナルでコンテナを起動**
   ```cmd
   docker-compose -f docker-compose.macwin.yml up --build
   ```

#### macOSの場合
1. **Docker Desktopを起動**
   - Finderを開く
   - アプリケーション → Docker → Docker Desktopをダブルクリック
   - メニューバーにDockerのアイコンが表示されるまで待つ

2. **ターミナルでコンテナを起動**
   ```bash
   docker-compose -f docker-compose.macwin.yml up --build
   ```

### 4. Cursorでの開発

1. **Cursorをインストール（未インストールの場合）**
   - [Cursor公式サイト](https://cursor.sh/)にアクセス
   - 「Download」ボタンをクリック
   - ダウンロードしたファイルを実行してインストール

2. **Cursorでプロジェクトを開く**
   - Cursorを起動
   - 「Open Folder」をクリック
   - クローンした`tamagotchi-prototype`フォルダを選択

3. **コンテナ内で開発**
   - 新しいターミナルを開く（Cursor内でCtrl + ` または Cmd + `）
   - コンテナに接続
   ```bash
   docker exec -it tamagotchi-pygame bash
   ```

4. **ゲームの実行**
   ```bash
   python -m src.main
   ```

### 5. GUI表示の確認

ゲームが正常に起動すると、以下のようなウィンドウが表示されます：
- **ウィンドウタイトル**: "Tamagotchi Prototype (512x512)"
- **ウィンドウサイズ**: 512×512ピクセル
- **ゲーム画面**: 128×128ピクセルの論理解像度を4倍拡大表示

## トラブルシューティング

### GUIが表示されない場合

#### Windows
1. **VcXsrvが起動しているか確認**
   - タスクバーにXLaunchアイコンがあるか確認
   - ない場合はXLaunchを再起動

2. **環境変数を再設定**
   ```cmd
   set DISPLAY=localhost:0.0
   ```

3. **ファイアウォールの設定**
   - WindowsファイアウォールでVcXsrvを許可
   - または一時的にファイアウォールを無効化

#### macOS
1. **XQuartzが起動しているか確認**
   - メニューバーにXQuartzアイコンがあるか確認
   - ない場合はXQuartzを再起動

2. **環境変数を再設定**
   ```bash
   export DISPLAY=:0
   ```

3. **セキュリティ設定**
   - システム環境設定 → セキュリティとプライバシー
   - XQuartzの実行を許可

### その他の問題
- **Dockerコンテナが起動しない**: Docker Desktopが起動しているか確認
- **ゲームがクラッシュする**: ログファイル（tamagotchi.log）を確認
- **パフォーマンスが悪い**: 他のアプリケーションを終了してリソースを確保

## 共同開発の方法

### 初心者向けガイド

#### 1. 開発の流れ
1. **Issueの確認**: GitHubのIssuesタブで現在の課題を確認
2. **ブランチの作成**: 新しい機能や修正用のブランチを作成
3. **開発**: コードを書いてテスト
4. **プルリクエスト**: 変更をレビューしてもらうためにPRを作成
5. **マージ**: 承認されたらメインブランチにマージ

#### 2. ブランチ命名規則
```
feature/新機能名    # 新機能の追加
fix/バグ修正名      # バグ修正
docs/ドキュメント名  # ドキュメント更新
```

#### 3. コミットメッセージの書き方
```
feat: 新しい機能を追加
fix: バグを修正
docs: ドキュメントを更新
style: コードスタイルを修正
refactor: コードをリファクタリング
test: テストを追加
```

#### 4. プルリクエストの作成手順
1. GitHubで「Pull requests」タブをクリック
2. 「New pull request」をクリック
3. ベースブランチ（通常は`main`）と比較ブランチを選択
4. タイトルと説明を記入
5. 「Create pull request」をクリック

### 開発者向け情報

#### プロジェクト構造
```
src/
├── main.py                 # エントリーポイント
├── game/
│   ├── core/              # ゲームエンジンとコアシステム
│   │   ├── game_engine.py # メインゲームエンジン
│   │   ├── input_handler.py # 入力処理
│   │   └── event_system.py # イベントシステム
│   ├── entities/          # ゲームエンティティ
│   │   ├── tamagotchi.py  # たまごっちメインクラス
│   │   └── pet_state.py   # ペット状態管理
│   ├── ui/                # UIシステム
│   │   ├── components.py  # UIコンポーネント
│   │   ├── renderer.py    # レンダリング管理
│   │   ├── display.py     # ディスプレイ管理
│   │   └── font_manager.py # フォント管理
│   ├── data/              # データ管理
│   │   ├── config.py      # 設定管理
│   │   └── save_manager.py # セーブデータ管理
│   └── utils/             # ユーティリティ
│       └── helpers.py     # ヘルパー関数
```

#### 新しい機能の追加方法

##### 1. 新しいイベントタイプの追加
```python
# src/game/core/event_system.py
class EventType(Enum):
    NEW_FEATURE = auto()
```

##### 2. 新しいUIコンポーネントの追加
```python
# src/game/ui/components.py
class NewComponent(UIComponent):
    def draw(self, surface):
        # 描画処理（必ず128×128の範囲内で描画）
        pass
```

##### 3. 新しいペットアクションの追加
```python
# src/game/entities/pet_state.py
def new_action(self) -> None:
    """新しいアクション"""
    # アクション処理
    pass
```

#### テストの実行
```bash
# テストを実行
python -m pytest tests/

# 特定のテストを実行
python -m pytest tests/test_pet_state.py

# カバレッジ付きでテスト実行
python -m pytest tests/ --cov=src
```

#### 設定の変更
```python
# src/game/data/config.py
@dataclass
class GameConfig:
    # ゲームバランス調整
    hunger_rate: float = 2.0        # 空腹度の自然増加率
    happiness_decay: float = 1.0    # 幸福度の自然減少率
    cleanliness_decay: float = 0.5  # 清潔度の自然減少率
    feed_amount: float = 35.0       # 餌の効果量
    play_amount: float = 25.0       # 遊びの効果量
    clean_amount: float = 60.0      # 掃除の効果量
```

## 🛠️ 技術スタック

- **Python 3.11**: メイン言語
- **Pygame 2.5.2**: ゲームエンジン
- **Docker**: 開発環境の統一
- **Git**: バージョン管理

### 主要な技術的特徴
- **イベント駆動アーキテクチャ**: 疎結合なシステム設計
- **コンポーネントベースUI**: 再利用可能なUIコンポーネント
- **自動セーブシステム**: 30秒間隔での自動保存
- **設定可能なゲームバランス**: データクラスによる設定管理
- **ピクセルパーフェクト表示**: レトロゲーム風の表示

## 📝 ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## 貢献

このプロジェクトへの貢献を歓迎します！以下の方法で参加できます：

1. **バグ報告**: Issuesでバグを報告
2. **機能提案**: 新しい機能のアイデアを提案
3. **コード貢献**: プルリクエストでコードを提供
4. **ドキュメント改善**: READMEやコメントの改善

何か質問がある場合は、Issuesでお気軽にお聞きください！

## ⚠️ 既知の問題

- Windows/macOSではDocker Desktopの起動が必要
- 初回起動時はDockerイメージのダウンロードに時間がかかる場合があります
- GUI表示にはX11サーバー（VcXsrv/XQuartz）の設定が必要

## 参考資料

- [Pygame公式ドキュメント](https://www.pygame.org/docs/)
- [Python公式ドキュメント](https://docs.python.org/3/)
- [Docker公式ドキュメント](https://docs.docker.com/)
- [VcXsrv公式サイト](https://sourceforge.net/projects/vcxsrv/)
- [XQuartz公式サイト](https://www.xquartz.org/)
