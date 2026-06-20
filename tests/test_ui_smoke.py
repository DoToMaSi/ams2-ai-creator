import pytest
from PySide6.QtWidgets import QApplication

from ams2_ai.ui.main_window import MainWindow


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_main_window_smoke(qapp):
    window = MainWindow()
    assert window.sidebar is not None
    assert window.driver_panel is not None
    window.close()
