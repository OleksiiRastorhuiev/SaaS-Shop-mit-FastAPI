from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User, Product, BenutzerBestellung, GastBestellung, BestellungBase

# 🔌 SQLite-Datenbank-Engine initialisieren
# Hinweis: "check_same_thread=False" erlaubt Nutzung in mehreren Threads (z. B. mit FastAPI)
engine = create_engine("sqlite:///saas_shop.db", connect_args={"check_same_thread": False})

# 🔄 SessionLocal: Instanz zur Erzeugung von DB-Sessions
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

# 🏗️ Alle Tabellen aus den Modellen erstellen (falls noch nicht vorhanden)
Base.metadata.create_all(engine)

# 📦 Dependency-Funktion zur Übergabe einer DB-Session
def get_db():
    """
    Erzeugt und liefert eine neue Datenbank-Session für die Verwendung in FastAPI-Routen.

    Diese Funktion wird typischerweise mit dem `Depends(get_db)`-Mechanismus
    in Routen verwendet. Sie stellt sicher, dass die Session nach Benutzung
    automatisch wieder geschlossen wird.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 📥 Bestellung speichern (für eingeloggte Benutzer oder Gäste)
def create_bestellung(benutzer_id=None, produkte=None, gast_id=None):
    """
    Legt eine neue Bestellung in der Datenbank an.

    Args:
        benutzer_id (int): Benutzer-ID, falls die Bestellung von einem registrierten Nutzer stammt.
        produkte (str): Produktinformationen (z. B. JSON-String oder CSV-artige Liste).
        gast_id (str): Gast-ID, falls die Bestellung von einem nicht registrierten Nutzer stammt.

    Hinweis:
        Entweder benutzer_id oder gast_id muss übergeben werden. Andernfalls wird eine Exception ausgelöst.
    """
    db = next(get_db())  # ▶ Generator sofort auflösen (nicht über Depends, da direkte Nutzung)

    try:
        if benutzer_id:
            # 🧾 Bestellung für eingeloggten Benutzer
            bestellung = BenutzerBestellung(benutzer_id=benutzer_id, produkte=produkte)
        elif gast_id:
            # 🧾 Bestellung für Gast (nicht eingeloggter Nutzer)
            bestellung = GastBestellung(gast_id=gast_id, produkte=produkte)
        else:
            raise ValueError("❌ Weder Benutzer-ID noch Gast-ID vorhanden – Bestellung kann nicht gespeichert werden.")
        
        db.add(bestellung)
        db.commit()
        print("✅ Bestellung erfolgreich gespeichert.")
    except Exception as e:
        db.rollback()
        print("❌ Fehler beim Speichern der Bestellung:", e)
    finally:
        db.close()
