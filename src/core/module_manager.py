from __future__ import annotations

from typing import List

from core.imodule import IModule


class ModuleManager:
    def __init__(self) -> None:
        self._modules: List[IModule] = []

    def register_module(self, module: IModule) -> None:
        module.initialize()
        self._modules.append(module)

    @property
    def modules(self) -> List[IModule]:
        return self._modules