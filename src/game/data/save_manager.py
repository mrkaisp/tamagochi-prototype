import json
import os
import logging
from typing import Any, Dict, Optional
from pathlib import Path
from datetime import datetime
from ..data.config import config

logger = logging.getLogger(__name__)

# セーブデータのバージョン（互換性管理用）
SAVE_DATA_VERSION = "1.0.0"

class SaveManager:
    """セーブ/ロード機能を管理するクラス"""
    
    def __init__(self, save_path: Optional[str] = None):
        self.save_path = Path(save_path or config.data.save_path)
        self.backup_path = self.save_path.with_suffix('.backup')
    
    def save(self, data: Dict[str, Any]) -> bool:
        """データをセーブする（バージョンメタデータ付き）"""
        try:
            # ディレクトリを作成
            self.save_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 既存のファイルをバックアップ
            if self.save_path.exists():
                self.save_path.rename(self.backup_path)
            
            # メタデータを追加
            save_data = {
                "version": SAVE_DATA_VERSION,
                "timestamp": datetime.now().isoformat(),
                "data": data
            }
            
            # 新しいファイルに書き込み
            with open(self.save_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            
            # バックアップを削除
            if self.backup_path.exists():
                self.backup_path.unlink()
            
            logger.info(
                f"Save successful: {self.save_path} "
                f"(version={SAVE_DATA_VERSION})"
            )
            return True
            
        except Exception as e:
            logger.error(f"Save failed: {e}")
            # バックアップから復元を試行
            self._restore_backup()
            return False
    
    def load(self) -> Optional[Dict[str, Any]]:
        """データをロードする（バージョンチェック付き）"""
        try:
            if not self.save_path.exists():
                logger.info("No save file found, creating new game")
                return None
            
            with open(self.save_path, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
            
            # バージョン情報をチェック
            if isinstance(save_data, dict) and "version" in save_data:
                version = save_data.get("version")
                data = save_data.get("data", save_data)
                logger.info(
                    f"Load successful: {self.save_path} "
                    f"(version={version}, current={SAVE_DATA_VERSION})"
                )
                
                # バージョン互換性チェック
                if version != SAVE_DATA_VERSION:
                    logger.warning(
                        f"Save data version mismatch: "
                        f"loaded={version}, current={SAVE_DATA_VERSION}. "
                        f"Attempting migration..."
                    )
                    data = self._migrate_data(data, version)
            else:
                # 古い形式（バージョン情報なし）の互換性処理
                logger.warning(
                    f"Legacy save file format detected. "
                    f"Attempting migration..."
                )
                data = self._migrate_legacy_data(save_data)
            
            return data
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid save file format: {e}")
            return self._load_backup()
        except Exception as e:
            logger.error(f"Load failed: {e}")
            return self._load_backup()
    
    def _load_backup(self) -> Optional[Dict[str, Any]]:
        """バックアップファイルからロードを試行（バージョンチェック付き）"""
        try:
            if self.backup_path.exists():
                with open(self.backup_path, 'r', encoding='utf-8') as f:
                    save_data = json.load(f)
                
                # バージョン情報をチェック
                if isinstance(save_data, dict) and "version" in save_data:
                    version = save_data.get("version")
                    data = save_data.get("data", save_data)
                    logger.info(
                        f"Loaded from backup file "
                        f"(version={version}, current={SAVE_DATA_VERSION})"
                    )
                    if version != SAVE_DATA_VERSION:
                        data = self._migrate_data(data, version)
                else:
                    data = self._migrate_legacy_data(save_data)
                
                return data
        except Exception as e:
            logger.error(f"Backup load failed: {e}")
        
        return None
    
    def _migrate_data(self, data: Dict[str, Any], from_version: str) -> Dict[str, Any]:
        """
        セーブデータのバージョンマイグレーション
        
        現在はバージョン1.0.0のみのため、基本的にはそのまま返す
        将来的にバージョンが上がった場合、ここで変換処理を追加
        """
        logger.info(f"Migrating data from version {from_version} to {SAVE_DATA_VERSION}")
        
        # 現在はバージョン1.0.0のみのため、そのまま返す
        # 将来的にバージョンが上がった場合、ここで変換処理を追加
        if from_version == SAVE_DATA_VERSION:
            return data
        
        # 未知のバージョンの場合は警告を出してそのまま返す
        logger.warning(
            f"Unknown save data version: {from_version}. "
            f"Attempting to load as-is."
        )
        return data
    
    def _migrate_legacy_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        古い形式（バージョン情報なし）のセーブデータをマイグレーション
        
        FlowerStats.from_dict()で既に古い形式の変換処理があるため、
        ここでは基本的にそのまま返す
        """
        logger.info("Migrating legacy save data format")
        return data
    
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
