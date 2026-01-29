from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple
from pathlib import Path

from PIL import Image
import numpy as np


@dataclass
class ImageAnalysis:
    size: Tuple[int, int]
    has_transparency: bool
    dominant_colors: List[Tuple[int, int, int]]
    opaque_ratio: float


class CharacterImageAnalyzer:
    """キャラクター画像の解析ユーティリティ"""

    def analyze_image(self, path: str | Path) -> ImageAnalysis:
        image_path = Path(path)
        img = Image.open(image_path)
        pixels = np.array(img)

        return ImageAnalysis(
            size=img.size,
            has_transparency=self._has_transparency(img),
            dominant_colors=self._get_dominant_colors(pixels),
            opaque_ratio=self._get_opaque_ratio(pixels, img.mode),
        )

    def _has_transparency(self, img: Image.Image) -> bool:
        if img.mode in ("RGBA", "LA"):
            return True
        if img.mode == "P" and "transparency" in img.info:
            return True
        return False

    def _get_opaque_ratio(self, pixels: np.ndarray, mode: str) -> float:
        if mode not in ("RGBA", "LA"):
            return 1.0
        alpha = pixels[..., -1]
        return float(np.count_nonzero(alpha > 0)) / float(alpha.size)

    def _get_dominant_colors(
        self, pixels: np.ndarray, max_colors: int = 5
    ) -> List[Tuple[int, int, int]]:
        if pixels.ndim == 2:
            pixels = np.stack([pixels, pixels, pixels], axis=-1)
        if pixels.shape[-1] == 4:
            pixels = pixels[..., :3]
        flat = pixels.reshape(-1, 3)
        if flat.size == 0:
            return []
        unique, counts = np.unique(flat, axis=0, return_counts=True)
        sorted_indices = np.argsort(counts)[::-1][:max_colors]
        return [tuple(map(int, unique[i])) for i in sorted_indices]
