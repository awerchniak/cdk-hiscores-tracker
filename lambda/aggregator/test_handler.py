import importlib
import pytest


@pytest.fixture
def aggregator_handler(monkeypatch):
    """Import within a fixture so we can set environment variables."""
    monkeypatch.setenv("HISCORES_TABLE_NAME", "hiscores-table-name")
    module = importlib.import_module("aggregator.handler")
    return module


def test_handler(aggregator_handler):
    print(type(aggregator_handler))