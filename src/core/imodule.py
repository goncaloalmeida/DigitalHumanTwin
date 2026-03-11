from __future__ import annotations

from abc import ABC, abstractmethod

from PySide6.QtWidgets import QWidget


class IModule(ABC):
    @abstractmethod
    def id(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def display_name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def view(self) -> QWidget:
        raise NotImplementedError

    def initialize(self) -> None:
        """Optional module setup hook."""
