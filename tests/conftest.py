import sys
from pathlib import Path

import pytest

from eventemitter import AsyncIOEventEmitter, EventEmitter

tests_path = Path(__file__).parent.absolute()
sys.path.append(str(tests_path))


@pytest.fixture
def ee() -> EventEmitter:
    return EventEmitter()


@pytest.fixture
def aee() -> AsyncIOEventEmitter:
    return AsyncIOEventEmitter()
