"""
CLI エントリポイント

コマンドラインから連続閉眼検知アルゴリズムを実行するためのインターフェースを提供します。
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Dict, Any

# 相対インポートを修正するため、パッケージのルートを追加
sys.path.append(str(Path(__file__).parent.parent.parent))

from source.config.config import Config
from source.config.validators import InputData
from source.core.drowsy_detector import DrowsyDetector


def load_config(config_path: str) -> Config:
    """
    設定ファイルを読み込み
    
    Args:
        config_path: 設定ファイルパス
        
    Returns:
        設定オブジェクト
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        return Config(**config_data)
    except FileNotFoundError:
        print(f"Error: Configuration file not found: {config_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in configuration file: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error loading configuration: {e}")
        sys.exit(1)


def load_input_data(input_path: str) -> List[InputData]:
    """
    入力データファイルを読み込み
    
    Args:
        input_path: 入力ファイルパス
        
    Returns:
        入力データのリスト
    """
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            input_data_list = json.load(f)
        
        # InputDataオブジェクトに変換
        parsed_data = []
        for i, data in enumerate(input_data_list):
            try:
                parsed_data.append(InputData(**data))
            except Exception as e:
                print(f"Error parsing input data at index {i}: {e}")
                sys.exit(1)
        
        return parsed_data
    except FileNotFoundError:
        print(f"Error: Input file not found: {input_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in input file: {e}")
        sys.exit(1)


def save_results(results: List[Dict[Any, Any]], output_path: str) -> None:
    """
    結果をファイルに保存
    
    Args:
        results: 結果のリスト
        output_path: 出力ファイルパス
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"Results saved to: {output_path}")
    except Exception as e:
        print(f"Error saving results: {e}")
        sys.exit(1)


def print_summary(results: List[Dict[Any, Any]]) -> None:
    """
    結果の要約を表示
    
    Args:
        results: 結果のリスト
    """
    total_frames = len(results)
    drowsy_frames = sum(1 for r in results if r.get('is_drowsy') == 1)
    error_frames = sum(1 for r in results if r.get('is_drowsy') == -1)
    normal_frames = total_frames - drowsy_frames - error_frames
    
    print("\n=== 処理結果サマリ ===")
    print(f"総フレーム数: {total_frames}")
    print(f"正常フレーム: {normal_frames} ({normal_frames/total_frames*100:.1f}%)")
    print(f"眠気検知フレーム: {drowsy_frames} ({drowsy_frames/total_frames*100:.1f}%)")
    print(f"エラーフレーム: {error_frames} ({error_frames/total_frames*100:.1f}%)")
    
    if drowsy_frames > 0:
        print(f"\n⚠️  眠気が検知されました！")


def create_sample_config(output_path: str) -> None:
    """
    サンプル設定ファイルを作成
    
    Args:
        output_path: 出力パス
    """
    config = Config()
    config_dict = config.dict()
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(config_dict, f, indent=2, ensure_ascii=False)
    
    print(f"Sample configuration file created: {output_path}")


def create_sample_input(output_path: str, num_frames: int = 100) -> None:
    """
    サンプル入力ファイルを作成
    
    Args:
        output_path: 出力パス
        num_frames: フレーム数
    """
    import random
    
    sample_data = []
    for i in range(num_frames):
        # ランダムなデータを生成（一部は閉眼状態）
        if i % 50 < 10:  # 20%の確率で閉眼
            left_eye = random.uniform(0.0, 0.2)
            right_eye = random.uniform(0.0, 0.2)
        else:
            left_eye = random.uniform(0.5, 1.0)
            right_eye = random.uniform(0.5, 1.0)
        
        sample_data.append({
            "frame_num": i + 1,
            "left_eye_open": left_eye,
            "right_eye_open": right_eye,
            "face_confidence": random.uniform(0.8, 1.0)
        })
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(sample_data, f, indent=2, ensure_ascii=False)
    
    print(f"Sample input file created: {output_path} ({num_frames} frames)")


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description="連続閉眼検知アルゴリズム",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # デフォルト設定で実行
  python -m source.cli.main --input data.json
  
  # 設定ファイルを指定して実行
  python -m source.cli.main --config config.json --input data.json --output result.json
  
  # サンプルファイルを生成
  python -m source.cli.main --create-sample-config config.json
  python -m source.cli.main --create-sample-input input.json --frames 200
        """
    )
    
    parser.add_argument("--config", type=str, help="設定ファイルパス (.json)")
    parser.add_argument("--input", type=str, help="入力JSONファイルパス")
    parser.add_argument("--output", type=str, help="出力JSONファイルパス")
    parser.add_argument("--verbose", "-v", action="store_true", help="詳細ログを表示")
    parser.add_argument("--create-sample-config", type=str, help="サンプル設定ファイルを作成")
    parser.add_argument("--create-sample-input", type=str, help="サンプル入力ファイルを作成")
    parser.add_argument("--frames", type=int, default=100, help="サンプル入力のフレーム数")
    
    args = parser.parse_args()
    
    # サンプルファイル作成
    if args.create_sample_config:
        create_sample_config(args.create_sample_config)
        return
    
    if args.create_sample_input:
        create_sample_input(args.create_sample_input, args.frames)
        return
    
    # 入力ファイルが必須
    if not args.input:
        print("Error: --input is required")
        parser.print_help()
        sys.exit(1)
    
    # 設定読み込み
    if args.config:
        config = load_config(args.config)
    else:
        config = Config()
        print("Using default configuration")
    
    # ログレベル設定
    if args.verbose:
        config.log_level = "DEBUG"
        config.enable_debug_log = True
    
    # 検出器初期化
    try:
        detector = DrowsyDetector(config)
        print(f"DrowsyDetector initialized with {config.dict()}")
    except Exception as e:
        print(f"Error initializing detector: {e}")
        sys.exit(1)
    
    # 入力データ読み込み
    input_data_list = load_input_data(args.input)
    print(f"Loaded {len(input_data_list)} frames from {args.input}")
    
    # 処理実行
    results = []
    try:
        for i, input_data in enumerate(input_data_list):
            result = detector.update(input_data)
            results.append(result.dict())
            
            # 進捗表示
            if (i + 1) % 100 == 0 or (i + 1) == len(input_data_list):
                print(f"Processed {i + 1}/{len(input_data_list)} frames")
                
    except Exception as e:
        print(f"Error during processing: {e}")
        sys.exit(1)
    
    # 結果出力
    if args.output:
        save_results(results, args.output)
    else:
        # コンソールに出力（最初の10件のみ）
        print("\n=== 処理結果 (最初の10件) ===")
        for result in results[:10]:
            print(json.dumps(result, ensure_ascii=False))
        if len(results) > 10:
            print(f"... and {len(results) - 10} more results")
    
    # サマリ表示
    print_summary(results)
    
    # 統計情報表示
    if args.verbose:
        stats = detector.get_statistics()
        print(f"\n=== 統計情報 ===")
        print(json.dumps(stats, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
