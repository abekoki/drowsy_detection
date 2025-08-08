"""
連続閉眼検知アルゴリズム Pythonモジュール

このパッケージは、カメラ映像から抽出した開眼度情報を基に、
指定時間以上連続して閉眼状態が続いた場合にアラートを発報する
アルゴリズムを提供します。

主要なモジュール:
- config: 設定管理とデータ検証
- core: メインアルゴリズム、タイマー管理、目の状態管理
- utils: ログ機能、データ前処理
- cli: コマンドラインインターフェース
"""

__version__ = "1.0.0"
__author__ = "GPT-Assist"

from .config.config import Config
from .config.validators import InputData, OutputData
from .core.drowsy_detector import DrowsyDetector

__all__ = [
    "Config",
    "InputData", 
    "OutputData",
    "DrowsyDetector"
]
