#!/usr/bin/env python3
"""
花の育成ゲーム『ふらわっち』 - プロトタイプ版
"""

import sys
import argparse
import logging
from .game.core.game_engine import GameEngine
from .game.data.config import config

def setup_logging():
    """ログ設定を初期化"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('flower_game.log', encoding='utf-8')
        ]
    )

def main():
    """メイン関数"""
    # コマンドライン引数の解析
    parser = argparse.ArgumentParser(
        description='花の育成ゲーム『ふらわっち』',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
例:
  python -m src.main              # デフォルト設定で実行
  python -m src.main --seed 42     # シード42で実行（再現性確保）
  python -m src.main --seed 12345 # シード12345で実行
        """
    )
    parser.add_argument(
        '--seed',
        type=int,
        default=None,
        help='乱数シードを指定（再現性確保のため）'
    )
    
    args = parser.parse_args()
    
    # シードが指定された場合は設定に反映
    if args.seed is not None:
        config.data.random_seed = args.seed
        logging.info(f"Random seed set to: {args.seed}")
    
    # ログ設定
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # ゲームエンジンを作成
        engine = GameEngine()
        
        # 初期化
        if not engine.initialize():
            logger.error("Failed to initialize game engine")
            return 1
        
        logger.info("Game engine initialized successfully")
        if config.data.random_seed is not None:
            logger.info(f"Using random seed: {config.data.random_seed}")
        
        # ゲームループを実行
        engine.run()
        
        logger.info("Game finished successfully")
        return 0
        
    except KeyboardInterrupt:
        logger.info("Game interrupted by user")
        return 0
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())
