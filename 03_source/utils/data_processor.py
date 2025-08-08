"""
データ前処理モジュール

入力データの前処理、NaN値の処理、範囲制限などを提供します。
"""

import numpy as np
from ..config.validators import InputData, ProcessedData
from typing import Optional


class DataProcessor:
    """データ前処理クラス"""
    
    def __init__(self):
        """データ前処理クラスを初期化"""
        self.last_valid_data: Optional[ProcessedData] = None
        self.nan_count = 0  # NaN値の出現回数を追跡
        self.total_count = 0  # 総処理回数を追跡
    
    def preprocess(self, input_data: InputData) -> ProcessedData:
        """
        入力データの前処理
        
        Args:
            input_data: 生入力データ
            
        Returns:
            前処理済みデータ
        """
        self.total_count += 1
        
        # NaN チェックと補完
        left_eye = self._handle_nan_value(input_data.left_eye_open, "left_eye_open")
        right_eye = self._handle_nan_value(input_data.right_eye_open, "right_eye_open")
        face_conf = self._handle_nan_value(input_data.face_confidence, "face_confidence")
        
        # 範囲制限
        left_eye = np.clip(left_eye, 0.0, 1.0)
        right_eye = np.clip(right_eye, 0.0, 1.0)
        face_conf = np.clip(face_conf, 0.0, 1.0)
        
        # 有効データとして保存
        self.last_valid_data = ProcessedData(
            left_eye_open=left_eye,
            right_eye_open=right_eye,
            face_confidence=face_conf
        )
        
        return self.last_valid_data
    
    def _handle_nan_value(self, value: float, field_name: str) -> float:
        """
        NaN値の処理
        
        Args:
            value: 入力値
            field_name: フィールド名
            
        Returns:
            処理済み値
        """
        if np.isnan(value):
            self.nan_count += 1
            
            if self.last_valid_data is not None:
                # 直前の有効値で補完
                if field_name == "left_eye_open":
                    return self.last_valid_data.left_eye_open
                elif field_name == "right_eye_open":
                    return self.last_valid_data.right_eye_open
                elif field_name == "face_confidence":
                    return self.last_valid_data.face_confidence
            
            # デフォルト値
            return 0.0
        
        return value
    
    def reset(self) -> None:
        """状態リセット"""
        self.last_valid_data = None
        self.nan_count = 0
        self.total_count = 0
    
    def get_statistics(self) -> dict:
        """処理統計を取得"""
        nan_rate = self.nan_count / max(self.total_count, 1)
        return {
            'total_processed': self.total_count,
            'nan_count': self.nan_count,
            'nan_rate': nan_rate,
            'has_last_valid': self.last_valid_data is not None
        }
    
    def apply_smoothing(self, values: list, window_size: int = 3) -> float:
        """
        値の平滑化（移動平均）
        
        Args:
            values: 値のリスト
            window_size: 平滑化ウィンドウサイズ
            
        Returns:
            平滑化された値
        """
        if not values:
            return 0.0
        
        # 最新のwindow_size個の値で平均を計算
        recent_values = values[-window_size:]
        return float(np.mean(recent_values))
