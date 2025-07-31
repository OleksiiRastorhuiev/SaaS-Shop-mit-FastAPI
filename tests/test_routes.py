'''
Ausführung:
    export PYTHONPATH=$PYTHONPATH:../
    pytest tests/test_routes.py
'''

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Base, Product
from main import app, get_db

# 📂 Testdatenbank: eigene SQLite-Datei (lokal persistent)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_routes.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

# 🧪 Eigene Session-Klasse für Tests
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 🚫 Dependency override für get_db → verwendet Testdatenbank
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# 🧩 Dependency überschreiben
app.dependency_overrides[get_db] = override_get_db

# 🧪 TestClient für FastAPI-App
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    """
    Diese Fixture wird automatisch vor jedem Test ausgeführt.
    Sie erstellt die Tabellen neu und fügt ein Testprodukt ein.
    """
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    db.add(Product(name="Test Produkt", description="Beschreibung", price=10.0))
    db.commit()
    db.close()
    yield


def test_index():
    """
    Testet die Startseite ("/") und prüft, ob Titeltext vorhanden ist.
    """
    response = client.get("/")
    assert response.status_code == 200
    assert "SaaS Produkt-Shop" in response.text


def test_add_to_cart():
    """
    Testet das Hinzufügen eines Produkts zum Warenkorb.
    """
    db = TestingSessionLocal()
    product = db.query(Product).first()
    db.close()

    response = client.post("/add_to_cart", data={"product_id": product.id}, follow_redirects=True)
    assert response.status_code == 200
    assert "Warenkorb" in response.text or "SaaS Produkt-Shop" in response.text


def test_remove_from_cart():
    """
    Testet das Entfernen eines Produkts aus dem Warenkorb.
    """
    db = TestingSessionLocal()
    product = db.query(Product).first()
    db.close()

    # Produkt erst hinzufügen
    client.post("/add_to_cart", data={"product_id": product.id}, follow_redirects=True)

    # Dann entfernen
    response = client.post("/remove_from_cart", data={"product_id": product.id}, follow_redirects=True)
    assert response.status_code == 200
    assert "SaaS Produkt-Shop" in response.text


def test_bestellen_unauthorized(monkeypatch):
    """
    Testet den Checkout-Prozess für nicht eingeloggte Benutzer.
    Simuliert den Template-Response mit monkeypatch.
    """
    from fastapi.responses import HTMLResponse
    monkeypatch.setattr("main.templates.TemplateResponse", lambda *args, **kwargs: HTMLResponse(content="Bestellung Erfolgreich", status_code=200))

    db = TestingSessionLocal()
    product = db.query(Product).first()
    db.close()

    client.post("/add_to_cart", data={"product_id": product.id}, follow_redirects=True)
    response = client.post("/checkout", follow_redirects=True)
    assert response.status_code == 200
    assert "Bestellung Erfolgreich" in response.text
