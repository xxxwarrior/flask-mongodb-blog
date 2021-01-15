import os 
import tempfile 

import pytest

from config import TestConfig
from app import create_app

@pytest.fixture
def app():
    app = create_app(TestConfig)
    yield app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

