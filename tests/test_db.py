'''
Ausführungshinweis:
    export PYTHONPATH=$PYTHONPATH:../
    pytest tests/test_db.py
'''

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User, Product, BenutzerBestellung, GastBestellung
from db import create_bestellung as original_create_bestellung

# 🛠 In-Memory SQLite-Datenbank für Testzwecke
TEST_ENGINE = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(bind=TEST_ENGINE, autocommit=False, autoflush=False)

# 🔁 Fixture: Setzt Test-Datenbank für jede Funktion neu auf
@pytest.fixture(scope="function")
def db():
    """
    Erstellt und entfernt die Datenbanktabellen für jeden Testlauf,
    um Test-Isolation zu gewährleisten.
    """
    Base.metadata.create_all(bind=TEST_ENGINE)
    db = TestSessionLocal()
    yield db
    db.rollback()
    db.close()
    Base.metadata.drop_all(bind=TEST_ENGINE)

# 💾 Eigene create_bestellung-Funktion für Tests, ohne Originalfunktion zu beeinflussen
def create_bestellung_testsession(db, benutzer_id=None, produkte=None, gast_id=None):
    """
    Speichert eine Bestellung über Benutzer-ID oder Gast-ID in der Test-Datenbank.
    Führt Commit aus, oder Rollback bei Fehler.
    """
    try:
        if benutzer_id:
            bestellung = BenutzerBestellung(benutzer_id=benutzer_id, produkte=produkte)
        elif gast_id:
            bestellung = GastBestellung(gast_id=gast_id, produkte=produkte)
        else:
            raise ValueError("❌ Weder Benutzer-ID noch Gast-ID vorhanden – Bestellung kann nicht gespeichert werden.")

        db.add(bestellung)
        db.commit()
    except Exception as e:
        db.rollback()
        raise e

# ✅ Test: Datenbankverbindung verfügbar
def test_get_db(db):
    """
    Prüft, ob die Testdatenbank korrekt erstellt wurde.
    """
    assert db is not None

# ✅ Test: Benutzerbestellung kann gespeichert und korrekt gelesen werden
def test_create_bestellung_benutzer(db):
    """
    Erstellt eine Benutzerbestellung und prüft, ob sie erfolgreich gespeichert wurde.
    """
    user = User(username="Testuser1", password="test123")
    product = Product(name="Produkt A", description="Test", price=9.99)
    db.add(user)
    db.add(product)
    db.commit()

    create_bestellung_testsession(db, benutzer_id=user.id, produkte=product.decrypt_name())

    bestellung = db.query(BenutzerBestellung).first()
    assert bestellung is not None
    assert bestellung.benutzer_id == user.id
    assert bestellung.decrypt_produkte() == product.decrypt_name()

# ✅ Test: Gastbestellung kann gespeichert und korrekt gelesen werden
def test_create_bestellung_gast(db):
    """
    Erstellt eine Gastbestellung und prüft, ob sie erfolgreich gespeichert wurde.
    """
    gast_id = 999
    product = Product(name="Produkt B", description="Test", price=19.99)
    db.add(product)
    db.commit()

    create_bestellung_testsession(db, gast_id=gast_id, produkte=product.decrypt_name())

    bestellung = db.query(GastBestellung).first()
    assert bestellung is not None
    assert bestellung.gast_id == str(gast_id)
    assert bestellung.decrypt_produkte() == product.decrypt_name()

# ✅ Test: Fehlerfall – weder Benutzer-ID noch Gast-ID übergeben
def test_create_bestellung_fehler(db):
    """
    Prüft, ob bei fehlender Benutzer- und Gast-ID eine Exception ausgelöst wird.
    """
    with pytest.raises(ValueError):
        create_bestellung_testsession(db, benutzer_id=None, gast_id=None, produkte="Testprodukt")

# ✅ Test: Fehlerfall mit Rollback – Commit darf nicht erfolgen
def test_create_bestellung_db_rollback(db):
    """
    Prüft, ob bei Exception innerhalb von create_bestellung ein Rollback erfolgt
    und keine Bestellung in der Datenbank landet.
    """
    user = User(username="Fehleruser", password="pass")
    product = Product(name="Produkt C", description="Crash", price=0)
    db.add_all([user, product])
    db.commit()

    with pytest.raises(Exception):
        # Erzeuge absichtlich einen Fehler: `produkte=None`
        create_bestellung_testsession(db, benutzer_id=user.id, produkte=None)

    bestellung = db.query(BenutzerBestellung).first()
    assert bestellung is None
