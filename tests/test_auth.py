'''
Ausführungshinweis:
    export PYTHONPATH=$PYTHONPATH:../
    pytest tests/test_auth.py
'''

import pytest
from starlette.testclient import TestClient
from main import app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base
from db import get_db
import os

# 🔧 Temporäre SQLite-Datenbank für Tests
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_auth_temp.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 🧪 Setup & Teardown: Test-Datenbank automatisch vor/nach den Tests einrichten
@pytest.fixture(scope="module", autouse=True)
def setup_database():
    """
    Erzeugt vor allen Tests die Tabellen in einer temporären Testdatenbank
    und entfernt diese nach Testabschluss wieder.
    """
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("test_auth_temp.db"):
        os.remove("test_auth_temp.db")

# 🧩 Dependency Override: Nutzt die Testdatenbank anstelle der echten DB
def override_get_db():
    """
    Überschreibt die Datenbank-Dependency `get_db()` mit einer Test-Session.
    """
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# 🔁 Override aktivieren
app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


# ✅ Test: Registrierung und anschließender Login
def test_register_and_login_success():
    """
    Testet erfolgreiche Registrierung und anschließenden Login eines neuen Nutzers.
    Erwartung: Status 200 oder Weiterleitung (302), HTML-Titel vorhanden.
    """
    response = client.post("/register", data={
        "username": "testuser",
        "password": "testpass"
    })
    assert response.status_code in (200, 302)

    response = client.post("/login", data={
        "username": "testuser",
        "password": "testpass"
    })
    assert response.status_code in (200, 302)
    assert "<title>" in response.text.lower()


# ❌ Test: Login mit ungültigen Zugangsdaten
def test_login_failure():
    """
    Testet fehlerhaften Login mit falschem Nutzernamen und Passwort.
    Erwartung: Keine Weiterleitung zur geschützten Seite, sondern Login-Seite.
    """
    response = client.post("/login", data={
        "username": "wronguser",
        "password": "wrongpass"
    })
    assert response.status_code in (200, 302)
    assert "<title>anmelden" in response.text.lower()


# ❌ Test: Registrierung mit doppeltem Nutzernamen
def test_register_failure_duplicate():
    """
    Testet doppelte Registrierung desselben Benutzernamens.
    Erwartung: 400 Bad Request und entsprechende Fehlermeldung.
    """
    # Ersten Benutzer registrieren
    client.post("/register", data={
        "username": "duplicateuser",
        "password": "pass"
    })

    # Zweite Registrierung mit gleichem Nutzernamen
    response = client.post("/register", data={
        "username": "duplicateuser",
        "password": "pass"
    })

    # Erwartet: 400 Bad Request + JSON-Fehlernachricht
    assert response.status_code == 400
    assert "benutzer existiert bereits" in response.text.lower()


# 🚪 Test: Logout nach erfolgreichem Login
def test_logout():
    """
    Testet den Logout-Prozess nach erfolgreichem Login.
    Erwartung: Status 200 oder Weiterleitung, HTML-Titel bestätigt Abmeldung.
    """
    client.post("/register", data={
        "username": "logoutuser",
        "password": "testpass"
    })

    client.post("/login", data={
        "username": "logoutuser",
        "password": "testpass"
    })

    response = client.get("/logout")
    assert response.status_code in (200, 302)
    assert "<title>" in response.text.lower()
