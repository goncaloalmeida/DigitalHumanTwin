from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMainWindow,
    QStackedWidget,
    QWidget,
)

from core.module_manager import ModuleManager


class MainWindow(QMainWindow):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._module_manager: Optional[ModuleManager] = None
        self._navigation: Optional[QListWidget] = None
        self._stack: Optional[QStackedWidget] = None
        self._empty_state: Optional[QLabel] = None
        self._build_shell()

    def set_module_manager(self, manager: ModuleManager) -> None:
        self._module_manager = manager
        self._refresh_modules()

    def _build_shell(self) -> None:
        root = QWidget(self)
        layout = QHBoxLayout(root)

        self._navigation = QListWidget(root)
        self._navigation.setMinimumWidth(220)

        self._stack = QStackedWidget(root)
        self._empty_state = QLabel(
            "Base application ready. Add future features under src/modules.",
            root,
        )
        self._empty_state.setWordWrap(True)
        self._empty_state.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._stack.addWidget(self._empty_state)

        layout.addWidget(self._navigation)
        layout.addWidget(self._stack, 1)

        self.setCentralWidget(root)
        self.setWindowTitle("Digital Human Twin")
        self.resize(1100, 700)

        self._navigation.currentRowChanged.connect(self._on_navigation_index_changed)

    def _on_navigation_index_changed(self, index: int) -> None:
        if self._stack is None:
            return

        if index < 0:
            self._stack.setCurrentIndex(0)
            return

        self._stack.setCurrentIndex(index + 1)

    def _refresh_modules(self) -> None:
        if self._navigation is None or self._stack is None:
            return

        self._navigation.clear()

        while self._stack.count() > 1:
            widget = self._stack.widget(1)
            self._stack.removeWidget(widget)
            widget.deleteLater()

        if self._module_manager is None or not self._module_manager.modules:
            self._navigation.setCurrentRow(-1)
            self._stack.setCurrentIndex(0)
            return

        for module in self._module_manager.modules:
            self._navigation.addItem(module.display_name())
            self._stack.addWidget(module.view())

        self._navigation.setCurrentRow(0)