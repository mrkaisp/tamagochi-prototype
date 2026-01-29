# draft画像 移行メモ（陰陽2種・まっすぐ削除対応）

このメモは、`docs/characters/draft/` の既存画像を
`src/game/assets/characters/` の新構成へ配置するための指針です。
現時点では画像の内容を自動判定できないため、ファイル名ベースでの提案です。

## 1. 芽（sprout）

- `芽_ハート.png`
  - `sprout/陽/ハート芽/normal.png` の候補
  - 状態別（good/weak）は未作成のため、必要なら複製して調整
- `芽_棘.png`
  - `sprout/陰/棘芽/normal.png` の候補
  - 状態別（good/weak）は未作成のため、必要なら複製して調整
- `芽_しなる.png`, `芽_ツル.png`
  - 芽段階の差分として使うか、茎段階の素材として再利用するか要検討

## 2. 蕾（bud）

以下は形状別に `bud/<形状>/normal.png` の候補。
状態別（good/weak）は未作成のため、必要なら複製して調整。

- `蕾_まるまる.png` -> `bud/まるまる/normal.png`
- `蕾_大輪.png` -> `bud/大輪/normal.png`
- `蕾_ひらひら.png` -> `bud/ひらひら/normal.png`
- `蕾_ちいさめ.png` -> `bud/ちいさめ/normal.png`
- `蕾_とがり.png` -> `bud/とがり/normal.png`
- `蕾_ふつう.png` -> `bud/ふつう/normal.png`

## 3. 花（flower）

新しい分岐で参照される花名のみを優先的に配置。
状態別（good/weak）は未作成のため、必要なら複製して調整。

- `ひまわりっち.png` -> `flower/ひまわり/normal.png`
- `さくらっち.png` -> `flower/さくら/normal.png`
- `すみれっち.png` -> `flower/すみれ/normal.png`

## 4. 種（seed）

陰陽の種画像は現状なし。
必要に応じて新規作成、または既存素材の再利用を検討。

## 5. その他（要検討/削除候補）

現仕様に直接対応しない可能性があるため、用途を決めた上で移行または削除を検討。

- `たんぽっち.png`
- `ふじっち.png`
- `ねもっち.png`
- `ばらっち.png`
- `こすもっち.png`
- `あじさいっち.png`
- `なでしこっち.png`
- `かれはなっち.png`
- `ふつうっち.png`
