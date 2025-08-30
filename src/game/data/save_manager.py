import json
import os
import logging
from typing import Any, Dict, Optional
from pathlib import Path
from ..data.config import config

logger = logging.getLogger(__name__)

class SaveManager:
    """セーブ/ロード機能を管理するクラス"""
    
    def __init__(self, save_path: Optional[str] = None):
        self.save_path = Path(save_path or config.data.save_path)
        self.backup_path = self.save_path.with_suffix('.backup')
    
    def save(self, data: Dict[str, Any]) -> bool:
        """データをセーブする"""
        try:
            # ディレクトリを作成
            self.save_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 既存のファイルをバックアップ
            if self.save_path.exists():
                self.save_path.rename(self.backup_path)
            
            # 新しいファイルに書き込み
            with open(self.save_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            # バックアップを削除
            if self.backup_path.exists():
                self.backup_path.unlink()
            
            logger.info(f"Save successful: {self.save_path}")
            return True
            
        except Exception as e:
            logger.error(f"Save failed: {e}")
            # バックアップから復元を試行
            self._restore_backup()
            return False
    
    def load(self) -> Optional[Dict[str, Any]]:
        """データをロードする"""
        try:
            if not self.save_path.exists():
                logger.info("No save file found, creating new game")
                return None
            
            with open(self.save_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.info(f"Load successful: {self.save_path}")
            return data
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid save file format: {e}")
            return self._load_backup()
        except Exception as e:
            logger.error(f"Load failed: {e}")
            return self._load_backup()
    
    def _load_backup(self) -> Optional[Dict[str, Any]]:
        """バックアップファイルからロードを試行"""
        try:
            if self.backup_path.exists():
                with open(self.backup_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                logger.info("Loaded from backup file")
                return data
        except Exception as e:
            logger.error(f"Backup load failed: {e}")
        
        return None
    
    def _restore_backup(self):
        """バックアップファイルを復元"""
        try:
            if self.backup_path.exists():
                self.backup_path.rename(self.save_path)
                logger.info("Restored from backup")
        except Exception as e:
            logger.error(f"Backup restore failed: {e}")
    
    def delete_save(self) -> bool:
        """セーブファイルを削除"""
        try:
            if self.save_path.exists():
                self.save_path.unlink()
            if self.backup_path.exists():
                self.backup_path.unlink()
            logger.info("Save file deleted")
            return True
        except Exception as e:
            logger.error(f"Delete save failed: {e}")
            return False
    
    def has_save(self) -> bool:
        """セーブファイルが存在するかチェック"""
        return self.save_path.exists() or self.backup_path.exists()
