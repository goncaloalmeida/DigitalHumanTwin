from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class LayerAssetSpec:
    layer_index: int
    layer_name: str
    mesh_path: Path
    base_scale: float
    rgb: tuple[int, int, int]


class BodyParts3DAssetCatalog:
    def __init__(self) -> None:
        self._root = Path(__file__).resolve().parents[1] / "assets" / "bodyparts3d"
        self._mesh = self._root / "base_humanoid.obj"

    @property
    def root(self) -> Path:
        return self._root

    @property
    def mesh(self) -> Path:
        return self._mesh

    def layer_specs(self) -> list[LayerAssetSpec]:
        return [
            LayerAssetSpec(0, "Pele", self._mesh, 1.00, (92, 165, 245)),
            LayerAssetSpec(1, "Tecido subcutaneo", self._mesh, 0.97, (174, 220, 255)),
            LayerAssetSpec(2, "Musculatura", self._mesh, 0.93, (118, 218, 255)),
            LayerAssetSpec(3, "Esqueleto", self._mesh, 0.88, (221, 243, 255)),
            LayerAssetSpec(4, "Orgaos toracicos", self._mesh, 0.70, (149, 203, 251)),
            LayerAssetSpec(5, "Coracao e arterias", self._mesh, 0.54, (236, 90, 105)),
        ]

    def focus_layer_for_mode(self, mode: str) -> int:
        return {
            "skeleton": 3,
            "fat": 1,
            "muscle": 2,
        }.get(mode, 0)

    def pose_yaw_for_mode(self, mode: str) -> float:
        return {
            "skeleton": 0.0,
            "fat": -25.0,
            "muscle": -90.0,
        }.get(mode, 0.0)


ACTIVE_ASSET_CATALOG = BodyParts3DAssetCatalog()