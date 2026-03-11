import argparse
import sys

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from app.main_window import MainWindow
from core.module_manager import ModuleManager
from modules.body_profile_module import BodyProfileModule


def build_module_manager() -> ModuleManager:
    manager = ModuleManager()
    manager.register_module(BodyProfileModule())
    return manager


def run_application(smoke_test: bool = False) -> int:
    app = QApplication(sys.argv)

    module_manager = build_module_manager()

    window = MainWindow()
    window.set_module_manager(module_manager)

    if smoke_test:
        QTimer.singleShot(0, app.quit)
    else:
        window.show()

    return app.exec()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Digital Human Twin desktop app")
    parser.add_argument(
        "--smoke-test",
        action="store_true",
        help="Initialize UI and modules, then exit immediately.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    raise SystemExit(run_application(smoke_test=args.smoke_test))