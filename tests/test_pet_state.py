import unittest
from src.game.entities.pet_state import PetStats
from src.game.data.config import config

class TestPetStats(unittest.TestCase):
    """PetStatsクラスのテスト"""
    
    def setUp(self):
        """テスト前の準備"""
        self.stats = PetStats()
    
    def test_initial_values(self):
        """初期値のテスト"""
        self.assertEqual(self.stats.hunger, 20.0)
        self.assertEqual(self.stats.happiness, 80.0)
        self.assertEqual(self.stats.cleanliness, 80.0)
        self.assertEqual(self.stats.age_seconds, 0.0)
        self.assertEqual(self.stats.poop_count, 0)
        self.assertFalse(self.stats.is_sick)
    
    def test_update(self):
        """更新処理のテスト"""
        # 1秒更新
        self.stats.update(1.0)
        
        # 自然変化の確認
        self.assertGreater(self.stats.hunger, 20.0)  # 空腹度が増加
        self.assertLess(self.stats.happiness, 80.0)  # 幸福度が減少
        self.assertLess(self.stats.cleanliness, 80.0)  # 清潔度が減少
        self.assertEqual(self.stats.age_seconds, 1.0)  # 年齢が増加
    
    def test_feed(self):
        """餌を与える処理のテスト"""
        initial_hunger = self.stats.hunger
        initial_poop = self.stats.poop_count
        
        self.stats.feed()
        
        self.assertLess(self.stats.hunger, initial_hunger)
        self.assertGreater(self.stats.poop_count, initial_poop)
    
    def test_play(self):
        """遊ぶ処理のテスト"""
        initial_happiness = self.stats.happiness
        
        self.stats.play()
        
        self.assertGreater(self.stats.happiness, initial_happiness)
    
    def test_clean(self):
        """掃除処理のテスト"""
        self.stats.poop_count = 3
        initial_cleanliness = self.stats.cleanliness
        
        self.stats.clean()
        
        self.assertEqual(self.stats.poop_count, 0)
        self.assertGreater(self.stats.cleanliness, initial_cleanliness)
    
    def test_sick_condition(self):
        """病気状態のテスト"""
        # 空腹度を高くして病気状態にする
        self.stats.hunger = 90.0
        self.stats.update(0.0)  # 病気判定のみ実行
        
        self.assertTrue(self.stats.is_sick)
    
    def test_age_formatting(self):
        """年齢フォーマットのテスト"""
        # 1時間30分45秒
        self.stats.age_seconds = 5445.0
        
        hours, minutes, seconds = self.stats.age
        self.assertEqual(hours, 1)
        self.assertEqual(minutes, 30)
        self.assertEqual(seconds, 45)
        
        # フォーマットされた文字列
        self.assertIn("1h30m", self.stats.age_formatted)

if __name__ == '__main__':
    unittest.main()
