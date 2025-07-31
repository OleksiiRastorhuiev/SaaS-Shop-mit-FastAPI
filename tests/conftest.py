# tests/conftest.py

import os
from dotenv import load_dotenv
import pytest

"""
conftest.py enthält globale Fixtures, die automatisch in allen Tests verfügbar sind.

In diesem Fall sorgt die Fixture `load_env` dafür, dass die Umgebungsvariablen
aus der `.env`-Datei vor dem Start aller Tests geladen werden.
Dies ist besonders wichtig für sensible Werte wie ENCRYPTION_KEY.
"""

@pytest.fixture(scope="session", autouse=True)
def load_env():
    """
    Lädt die Umgebungsvariablen aus der `.env`-Datei einmalig pro Test-Session,
    bevor andere Tests ausgeführt werden.
    """
    load_dotenv()  # .env-Datei automatisch laden
