from __future__ import annotations

from dataclasses import dataclass
import math
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pygame as pg

from ..entities.flower import FlowerStats, GrowthStage
from ..utils.character_image_analyzer import CharacterImageAnalyzer


@dataclass
class AnimationFrames:
    frames: List[pg.Surface]
    fps: float


class CharacterSpriteManager:
    """キャラクタースプライト管理"""

    def __init__(self) -> None:
        self._base_dir = (
            Path(__file__).parent.parent / "assets" / "characters"
        ).resolve()
        self._image_cache: Dict[Path, pg.Surface] = {}
        self._animation_cache: Dict[Path, AnimationFrames] = {}
        self._analyzer = CharacterImageAnalyzer()

    def get_character_surface(
        self, stats: FlowerStats, target_size: Tuple[int, int]
    ) -> Optional[pg.Surface]:
        base_path = self._get_sprite_path(stats)
        if not base_path:
            return None

        frames = self._get_animation_frames(base_path)
        if not frames:
            return None

        frame = self._select_frame(frames)
        if frame is None:
            return None

        effect_surface = self._apply_effects(frame, stats)
        return self._scale_image(effect_surface, target_size)

    def analyze_image(self, path: Path):
        return self._analyzer.analyze_image(path)

    def _get_sprite_path(self, stats: FlowerStats) -> Optional[Path]:
        state_key = self._get_state_string(stats)
        if stats.growth_stage == GrowthStage.SEED:
            return self._base_dir / "seed" / stats.seed_type.value / f"{state_key}.png"
        if stats.growth_stage == GrowthStage.SPROUT:
            sprout_type = self._get_sprout_type(stats)
            return (
                self._base_dir
                / "sprout"
                / stats.seed_type.value
                / sprout_type
                / f"{state_key}.png"
            )
        if stats.growth_stage == GrowthStage.STEM:
            return self._base_dir / "stem" / stats.phase2_branch / f"{state_key}.png"
        if stats.growth_stage == GrowthStage.BUD:
            return self._base_dir / "bud" / stats.phase3_shape / f"{state_key}.png"
        if stats.growth_stage == GrowthStage.FLOWER:
            flower_name = stats.character_name
            return self._base_dir / "flower" / flower_name / f"{state_key}.png"
        return None

    def _get_state_string(self, stats: FlowerStats) -> str:
        nutrition = self._get_nutrition_state(stats)
        if stats.growth_stage in (GrowthStage.BUD, GrowthStage.FLOWER):
            mental = self._get_mental_state(stats)
            return f"{nutrition}_{mental}"
        return nutrition

    def _get_nutrition_state(self, stats: FlowerStats) -> str:
        if stats.water_level >= 60:
            return "good"
        if stats.water_level >= 20:
            return "normal"
        return "weak"

    def _get_mental_state(self, stats: FlowerStats) -> str:
        if stats.mental_level >= 60:
            return "good"
        if stats.mental_level >= 30:
            return "normal"
        return "low"

    def _get_sprout_type(self, stats: FlowerStats) -> str:
        return "棘芽" if stats.light_tendency_yin else "ハート芽"

    def _get_animation_frames(self, base_path: Path) -> Optional[AnimationFrames]:
        if base_path in self._animation_cache:
            return self._animation_cache[base_path]

        if base_path.exists():
            frames = [self._load_image(base_path)]
            animation = AnimationFrames(frames=frames, fps=0.0)
            self._animation_cache[base_path] = animation
            return animation

        # アニメーション用の複数フレーム探索
        frame_candidates = sorted(base_path.parent.glob(f"{base_path.stem}_*.png"))
        if frame_candidates:
            frames = [self._load_image(path) for path in frame_candidates]
            animation = AnimationFrames(frames=frames, fps=6.0)
            self._animation_cache[base_path] = animation
            return animation

        # スプライトシート探索
        sheet_path = base_path.with_name(f"{base_path.stem}_sheet.png")
        if sheet_path.exists():
            frames = self._slice_sheet(sheet_path)
            animation = AnimationFrames(frames=frames, fps=6.0)
            self._animation_cache[base_path] = animation
            return animation

        return None

    def _slice_sheet(self, sheet_path: Path) -> List[pg.Surface]:
        sheet = self._load_image(sheet_path)
        width, height = sheet.get_size()
        if height == 0:
            return [sheet]
        frame_count = max(1, width // height)
        frames = []
        for i in range(frame_count):
            frame = pg.Surface((height, height), pg.SRCALPHA)
            frame.blit(sheet, (0, 0), (i * height, 0, height, height))
            frames.append(frame)
        return frames

    def _select_frame(self, animation: AnimationFrames) -> Optional[pg.Surface]:
        if not animation.frames:
            return None
        if animation.fps <= 0:
            return animation.frames[0]
        time_seconds = pg.time.get_ticks() / 1000.0
        index = int(time_seconds * animation.fps) % len(animation.frames)
        return animation.frames[index]

    def _apply_effects(self, image: pg.Surface, stats: FlowerStats) -> pg.Surface:
        result = image.copy()
        time_seconds = pg.time.get_ticks() / 1000.0

        if stats.is_light_on:
            glow = pg.Surface(result.get_size(), pg.SRCALPHA)
            glow.fill((255, 245, 200, 60))
            result.blit(glow, (0, 0))

        if stats.water_level >= 60:
            pulse = 1.0 + 0.03 * math.sin(time_seconds * 6.0)
            result = self._scale_image(result, self._scaled_size(result, pulse))

        if stats.mental_level >= 60:
            self._draw_particles(result, time_seconds)

        return result

    def _draw_particles(self, surface: pg.Surface, time_seconds: float) -> None:
        width, height = surface.get_size()
        for i in range(6):
            angle = time_seconds * 2.0 + i
            x = int(width / 2 + (width * 0.3) * math.cos(angle))
            y = int(height / 2 + (height * 0.3) * math.sin(angle))
            pg.draw.circle(surface, (255, 240, 120, 180), (x, y), 2)

    def _scaled_size(self, image: pg.Surface, factor: float) -> Tuple[int, int]:
        width, height = image.get_size()
        return max(1, int(width * factor)), max(1, int(height * factor))

    def _load_image(self, path: Path) -> pg.Surface:
        if path in self._image_cache:
            return self._image_cache[path]
        image = pg.image.load(str(path)).convert_alpha()
        self._image_cache[path] = image
        return image

    def _scale_image(self, image: pg.Surface, target_size: Tuple[int, int]) -> pg.Surface:
        return pg.transform.smoothscale(image, target_size)
