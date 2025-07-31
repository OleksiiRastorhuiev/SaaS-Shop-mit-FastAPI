'''
Diese Tests überprüfen die folgenden Fälle:

test_product: Testet, ob die Product-Klasse korrekt funktioniert.
test_user: Testet, ob die User-Klasse korrekt funktioniert.
test_bestellung_base: Testet, ob die BestellungBase-Klasse korrekt funktioniert.
test_benutzer_bestellung: Testet, ob die BenutzerBestellung-Klasse korrekt funktioniert.
test_gast_bestellung: Testet, ob die GastBestellung-Klasse korrekt funktioniert.

Ausführung:
    export PYTHONPATH=$PYTHONPATH:../
    pytest tests/test_models.py
'''

import pytest
from models import Product, User, BestellungBase, BenutzerBestellung, GastBestellung
from encryption import encryption

# 🧪 Test: Produkt-Modell mit Verschlüsselung/Entschlüsselung
def test_product():
    """
    Erstellt ein verschlüsseltes Produktobjekt und prüft, ob Name und Beschreibung
    korrekt entschlüsselt werden können.
    """
    product = Product("Testprodukt", "Dies ist ein Testprodukt", 9.99)
    assert product.decrypt_name() == "Testprodukt"
    assert product.decrypt_description() == "Dies ist ein Testprodukt"

# 🧪 Test: Benutzer-Modell mit Passwortprüfung
def test_user():
    """
    Erstellt ein Benutzerobjekt und prüft die Passwortverifikation
    mit korrektem und falschem Passwort.
    """
    user = User("testuser", "testpassword")
    assert user.verify_password("testpassword") == True
    assert user.verify_password("wrongpassword") == False

# 🧪 Test: Basismodell für Bestellungen
def test_bestellung_base():
    """
    Erstellt ein BestellungBase-Objekt und prüft,
    ob verschlüsselte Produktdaten korrekt entschlüsselt werden.
    """
    bestellung = BestellungBase("Testprodukte")
    assert bestellung.decrypt_produkte() == "Testprodukte"

# 🧪 Test: Benutzerbestellung mit Referenz auf Benutzer-ID
def test_benutzer_bestellung():
    """
    Erstellt eine Benutzerbestellung und prüft,
    ob Produkte entschlüsselt werden können und die Benutzer-ID korrekt übernommen wurde.
    """
    user = User("testuser", "testpassword")
    bestellung = BenutzerBestellung(user.id, "Testprodukte")
    assert bestellung.decrypt_produkte() == "Testprodukte"
    assert bestellung.benutzer_id == user.id

# 🧪 Test: Gastbestellung mit Gast-ID
def test_gast_bestellung():
    """
    Erstellt eine Gastbestellung mit einer Gast-ID und prüft,
    ob die verschlüsselten Produkte korrekt entschlüsselt werden und die Gast-ID korrekt ist.
    """
    bestellung = GastBestellung("12345", "Testprodukte")
    assert bestellung.decrypt_produkte() == "Testprodukte"
    assert bestellung.gast_id == "12345"
