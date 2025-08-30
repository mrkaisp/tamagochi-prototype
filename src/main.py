#!/usr/bin/env python3
"""
たまごっちプロトタイプ - リファクタリング版
"""

import sys
import logging
from .game.core.game_engine import GameEngine

def setup_logging():
    """ログ設定を初期化"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('tamagotchi.log', encoding='utf-8')
        ]
    )

def main():
    """メイン関数"""
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
