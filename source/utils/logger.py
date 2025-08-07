"""
ログ管理モジュール

アプリケーション全体のログ機能を提供します。
"""

import logging
import sys
from datetime import datetime
from typing import Optional
from pathlib import Path


class Logger:
    """ログ管理クラス"""
    
    def __init__(self, level: str = "INFO", enable_debug: bool = False, log_file: Optional[str] = None):
        """
        ログ管理クラスを初期化
        
        Args:
            level: ログレベル
            enable_debug: デバッグログ有効化
            log_file: ログファイルパス（Noneの場合はコンソールのみ）
        """
        self.logger = logging.getLogger("drowsy_detection")
        self.logger.setLevel(getattr(logging, level))
        
        # 既存のハンドラーをクリア
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # コンソールハンドラー設定
        console_handler = logging.StreamHandler(sys.stdout)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # ファイルハンドラー設定（指定がある場合）
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
            )
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)
        
        # デバッグログ設定
        if enable_debug:
            debug_handler = logging.FileHandler("drowsy_detection_debug.log")
            debug_handler.setLevel(logging.DEBUG)
            debug_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
            )
            debug_handler.setFormatter(debug_formatter)
            self.logger.addHandler(debug_handler)
        
        # ログの重複を防ぐ
        self.logger.propagate = False
    
    def info(self, message: str) -> None:
        """情報ログ"""
        self.logger.info(message)
    
    def warning(self, message: str) -> None:
        """警告ログ"""
        self.logger.warning(message)
    
    def error(self, message: str) -> None:
        """エラーログ"""
        self.logger.error(message)
    
    def debug(self, message: str) -> None:
        """デバッグログ"""
        self.logger.debug(message)
    
    def critical(self, message: str) -> None:
        """重要ログ"""
        self.logger.critical(message)
    
    def set_level(self, level: str) -> None:
        """ログレベルを動的に変更"""
        self.logger.setLevel(getattr(logging, level.upper()))
    
    def log_performance(self, func_name: str, duration: float) -> None:
        """パフォーマンス情報をログ出力"""
        self.debug(f"Performance: {func_name} took {duration:.4f} seconds")
