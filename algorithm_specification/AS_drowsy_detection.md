# 連続閉眼検知アルゴリズム仕様書 (AS_drowsy_detection)

## 1. 概要・目的

### 1.1 アルゴリズム名
- 連続閉眼検知アルゴリズム (Continuous Eye Closure Detection)
- 略称: AS_drowsy_detection
- バージョン: v1.0.0

### 1.2 目的・背景
- ドライバーや作業者の眠気・注意力低下を早期に検知し、安全性を向上させることを目的とする。
- 左右の目の開眼度 (0.0 = 完全閉眼 ~ 1.0 = 完全開眼) を入力とし、指定時間以上連続して閉眼状態が続いた場合にアラートを発報する。
- 既存手法は単純なまばたき検出が多く、連続閉眼を精度高くリアルタイムに検知できない問題があった。本アルゴリズムは顔検出信頼度を組み合わせることで誤検知を低減する。

### 1.3 適用範囲
- 対象: カメラ映像・画像から抽出した開眼度情報と顔検出信頼度
- プラットフォーム: Python 実装を基準とし、C++ へ容易に移植できるようモジュール化
- ハードウェア: CPU ベース (組込み SoC 含む)。GPU 不要、60 fps 程度まで対応可能

---

## 2. 技術仕様

### 2.1 入力仕様
| フィールド | 型 | 説明 | 制約 |
| --- | --- | --- | --- |
| timestamp | float | フレーム時刻 [s] | 単調増加
| left_eye_open | float | 左目の開眼度 (0.0〜1.0) | 0.0 ≤ value ≤ 1.0
| right_eye_open | float | 右目の開眼度 (0.0〜1.0) | 0.0 ≤ value ≤ 1.0
| face_confidence | float | 顔検出信頼度 (0.0〜1.0) | 0.0 ≤ value ≤ 1.0

- 必須項目: 全フィールド必須
- 入力例:
```json
{
  "timestamp": 12.345,
  "left_eye_open": 0.15,
  "right_eye_open": 0.18,
  "face_confidence": 0.92
}
```

### 2.2 出力仕様
| フィールド | 型 | 説明 |
| --- | --- | --- |
| is_drowsy | bool | 連続閉眼状態が検知されたか |
| closed_duration | float | 現在の連続閉眼継続時間 [s] |
| last_change_time | float | 最終ステータス変更時刻 [s] |

- エラー時は `is_drowsy=false, closed_duration=0` を返す。
- 出力例:
```json
{
  "is_drowsy": true,
  "closed_duration": 1.27,
  "last_change_time": 15.600
}
```

### 2.3 パラメータ
| パラメータ | 説明 | デフォルト値 | 下限 | 上限 |
| --- | --- | --- | --- | --- |
| eye_close_threshold | 開眼度がこの値以下で閉眼と判定 | **0.30** | 0.0 | 1.0 |
| continuous_close_time | 連続閉眼とみなす時間閾値 [s] | **1.00** | 0.1 | 10.0 |
| face_conf_threshold | 顔検出が有効とみなす信頼度 | **0.70** | 0.0 | 1.0 |

---

## 3. アルゴリズム詳細

### 3.1 アルゴリズムの概要
開眼度と顔検出信頼度を時系列で入力し、以下 3 モジュールで構成される。
1. **前処理モジュール**: 外れ値除去・正規化を行う。
2. **閉眼判定モジュール**: `eye_close_threshold` を用いて各フレームで閉眼フラグを生成。
3. **連続閉眼判定モジュール**: 閉眼フラグが `continuous_close_time` 以上継続した場合に眠気フラグを立てる。

### 3.2 処理フロー
```mermaid
graph TD;
  A[入力: 開眼度 &amp; 顔信頼度] --> B{顔信頼度 &gt; face_conf_threshold?};
  B -- no --> G[無効データとしてスキップ];
  B -- yes --> C[開眼度 ≤ eye_close_threshold?];
  C -- no --> F[閉眼タイマー初期化];
  C -- yes --> D[閉眼タイマー加算];
  D --> E{閉眼タイマー ≥ continuous_close_time?};
  E -- no --> F;
  E -- yes --> H[連続閉眼(Fatigued)フラグ ON];
```

擬似コード:
```python
if face_confidence &lt; face_conf_threshold:
    reset_timer()
    return is_drowsy=False

if max(left_eye_open, right_eye_open) &gt; eye_close_threshold:
    reset_timer()
    return is_drowsy=False

update_timer(dt)
if timer &gt;= continuous_close_time:
    return is_drowsy=True
return is_drowsy=False
```

### 3.3 核心アルゴリズム
- 時間積分タイマーを利用した状態遷移モデル (有限状態機械)。
- 雑音の影響を減らすため指数移動平均 (EMA) を開眼度に適用可。

### 3.4 エラーハンドリング
- 顔信頼度が 0 の場合は計算をスキップし、ステータスを `unknown` とログに記録。
- 入力 NaN や範囲外値は直前の有効値で補完、もしくはリセット。

---

## 4. 性能・制約

### 4.1 計算量
- **時間計算量**: O(1) / フレーム
- **空間計算量**: O(1)

### 4.2 精度・性能指標
- 誤検知率 (False Positive Rate): &lt; 3 % @ 公開データセット XXXX
- 検知遅延: 閾値 + 1 フレーム (&lt; 150 ms @ 60 fps)

### 4.3 制約事項
- 顔が一定時間フレーム外に出るとタイマーがリセットされるため、連続閉眼の検知が遅延する。
- 暗所・逆光では開眼度推定精度が低下し、閾値を調整する必要がある。

---

## 5. 実装仕様

### 5.1 開発環境
- 言語: Python 3.11
- 主要ライブラリ: numpy, opencv-python, pydantic (検証用)
- C++ 移植時は Eigen + OpenCV を使用予定

### 5.2 ファイル構成 (例)
```
source/
  ├── detectors/
  │     └── eye_state.py      # 開眼度推定器ラッパ
  ├── drowsy_detection.py     # 本アルゴリズム実装
  ├── config.py               # パラメータ定義
  ├── tests/
  │     └── test_drowsy.py    # 単体テスト
  └── cli.py                  # CLI エントリポイント
```

### 5.3 テスト仕様
- **単体テスト**: 閾値境界ケース、NaN 入力、顔未検出ケース
- **統合テスト**: 動画シミュレーションで 30 分連続再生し誤検知が 0 件であること
- **性能テスト**: Raspberry Pi 4 で 30 fps 処理時に CPU 使用率 &lt; 20 %

---

## 6. 使用例・サンプル

### 6.1 基本的な使用例
```python
from drowsy_detection import DrowsyDetector, Config

detector = DrowsyDetector(Config())
for frame in stream:
    result = detector.update(frame.open_left, frame.open_right, frame.face_score)
    if result.is_drowsy:
        alert_driver()
```

### 6.2 応用例
- EMA 係数を変更し高速な目パチ検知も同時に行うマルチモーダルモデル

### 6.3 トラブルシューティング
| 症状 | 原因候補 | 対応策 |
| --- | --- | --- |
| 常に drowsy になる | eye_close_threshold が高すぎる | 閾値を下げる / 照明条件を変える |
| 検知が遅い | continuous_close_time が長い | 1 s → 0.7 s へ調整 |

---

## 7. 保守・運用

### 7.1 メンテナンス
- 新ハードウェア毎にパラメータ再キャリブレーション

### 7.2 監視・ログ
- `is_drowsy` 状態遷移を時刻付きで CSV 出力
- 異常入力 (NaN 等) のカウンタを Prometheus へエクスポート

### 7.3 バックアップ・復旧
- パラメータファイル (`config.json`) を Git 管理 + S3 バックアップ

---

## 8. セキュリティ・プライバシー

### 8.1 セキュリティ要件
- モジュール外部と通信しない設計 (オフライン動作)
- バイナリ整合性検証 (SHA-256)

### 8.2 プライバシー保護
- 開眼度等の個人特定情報を含まないメタデータのみ保存
- 記録データの保持期間: 30 日

---

## 9. 法的・規制対応

### 9.1 準拠すべき規制
- ISO 26262 (自動車機能安全規格) のソフトウェア開発ガイドライン

### 9.2 コンプライアンス
- 社内セキュリティポリシー (DOC-SEC-001) に基づくコードレビュー

---

## 10. 参考資料
- "Real-Time Eye Closure Detection Using Convolutional Neural Networks", IEEE 2023
- OpenCV ドキュメント (v4.9)

---

## 11. 変更履歴
| 日付 | バージョン | 変更箇所 | 変更者 |
| --- | --- | --- | --- |
| 2025-08-05 | 1.0.0 | 初版作成 | GPT-Assist |
