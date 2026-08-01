import os

# app.services.openai_service reads GROQ_API_KEY (and calls load_dotenv())
# at *module import* time, so the dummy value must be in os.environ before
# `from app.main import app` triggers that import chain. load_dotenv()
# does not override variables that are already set, so this value wins
# even if a real .env file is present.
os.environ.setdefault("GROQ_API_KEY", "test-dummy-groq-api-key")
os.environ.setdefault("GROQ_MODEL", "llama-3.3-70b-versatile")
os.environ.setdefault("APP_PORT", "8000")

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client
