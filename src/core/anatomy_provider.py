from __future__ import annotations

from abc import ABC, abstractmethod


class AnatomyProvider(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def license_name(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def homepage(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def organ_metrics(self, layer_index: int) -> dict[str, str]:
        raise NotImplementedError


class BodyParts3DProvider(AnatomyProvider):
    @property
    def name(self) -> str:
        return "BodyParts3D"

    @property
    def license_name(self) -> str:
        return "CC BY-SA 2.1 JP"

    @property
    def homepage(self) -> str:
        return "https://lifesciencedb.jp/bp3d/"

    def organ_metrics(self, layer_index: int) -> dict[str, str]:
        scaling = 0.82 + (layer_index * 0.05)
        return {
            "BRAIN": f"{int(1207 * scaling):,} cm3",
            "HEART": f"{int(45 * scaling)} %",
            "LUNGS": f"{int(6212 * scaling):,} cm3",
            "LIVER": f"{int(2098 * scaling):,} cm3",
        }


# Chosen default source for the current free-first strategy.
ACTIVE_ANATOMY_PROVIDER: AnatomyProvider = BodyParts3DProvider()