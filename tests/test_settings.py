import os

import pytest

from pysubs.utils import PySubsSettings


@pytest.fixture(autouse=True)
def run_before_and_after_tests():
    """Fixture to execute asserts before and after a test is run"""
    # Setup: fill with any logic you want
    key = "PYSUBS_TEST_KEY"
    if key in os.environ:
        os.environ.pop(key)
    yield  # this is where the testing happens
    # Teardown : fill with any logic you want
    if key in os.environ:
        os.environ.pop(key)


class TestPySubsSettings:
    def test_get_config(self):
        key = "PYSUBS_TEST_KEY"
        value = "CORRECT"
        os.environ[key] = value
        settings = PySubsSettings.instance()
        assert settings.get_config(key) == value

    def test_default_get_config(self):
        key = "PYSUBS_TEST_KEY"
        value = "DEFAULT"
        settings = PySubsSettings.instance()
        settings.__class__.defaults[key] = value
        assert settings.get_config(key) == value
