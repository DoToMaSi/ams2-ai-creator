import pytest


def pytest_configure(config: pytest.Config) -> None:
    if config.pluginmanager.hasplugin("pytestqt"):
        config.option.qt_api = "pyside6"
