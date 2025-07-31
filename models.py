from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.ext.declarative import declared_attr
from encryption import encryption
from datetime import datetime
from sqlalchemy import func
from passlib.context import CryptContext

# Passwort-Hashing-Kontext mit bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Basisklasse für alle SQLAlchemy-Modelle
Base = declarative_base()

class Product(Base):
    """
    Datenbankmodell für ein Produkt.
    Der Produktname und die Beschreibung werden verschlüsselt gespeichert.
    """
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    description = Column(String)
    price = Column(Float)

    def __init__(self, name, description, price):
        # Verschlüsselte Speicherung von Name und Beschreibung
        self.name = encryption.encrypt(name)
        self.description = encryption.encrypt(description)
        self.price = price

    def decrypt_name(self):
        """Entschlüsselt den Produktnamen"""
        return encryption.decrypt(self.name)

    def decrypt_description(self):
        """Entschlüsselt die Produktbeschreibung"""
        return encryption.decrypt(self.description)

class User(Base):
    """
    Datenbankmodell für registrierte Benutzer.
    Das Passwort wird automatisch gehasht (inkl. Salt) beim Erstellen.
    """
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)

    def __init__(self, username, password, already_hashed=False):
        self.username = username
        # Passwort-Hashing mit bcrypt + Salt
        self.password = (
            password if already_hashed else pwd_context.hash(password)
        )

    def verify_password(self, plain_password):
        """
        Verifiziert ein Klartextpasswort gegen den gespeicherten Hash.
        """
        return pwd_context.verify(plain_password, self.password)

# ▶ Polymorphe Basisklasse für Bestellungen
class BestellungBase(Base):
    """
    Abstrakte Basisklasse für Bestellungen (Gäste & Benutzer).
    Die Liste der bestellten Produkte wird verschlüsselt gespeichert.
    """
    __tablename__ = "bestellungen"
    id = Column(Integer, primary_key=True, index=True)
    typ = Column(String(50))  # Discriminator-Feld für Polymorphie
    timestamp = Column(DateTime, default=datetime.now)
    produkte = Column(String)  # Verschlüsselte Produktübersicht

    __mapper_args__ = {
        "polymorphic_identity": "base",
        "polymorphic_on": typ
    }

    def __init__(self, produkte):
        # Produkte verschlüsseln bei Speicherung
        self.produkte = self.encrypt_produkte(produkte)

    def encrypt_produkte(self, plaintext):
        """
        Verschlüsselt die Produktübersicht als String.
        """
        if isinstance(plaintext, bytes):
            plaintext = plaintext.decode("utf-8")
        return encryption.encrypt(plaintext)

    def decrypt_produkte(self):
        """
        Entschlüsselt die gespeicherte Produktübersicht.
        """
        return encryption.decrypt(self.produkte)

# ▶ Subtyp für eingeloggte Benutzer
class BenutzerBestellung(BestellungBase):
    """
    Speichert Bestellungen registrierter Benutzer.
    Verknüpft mit User über benutzer_id.
    """
    __tablename__ = "benutzer_bestellungen"
    id = Column(Integer, ForeignKey("bestellungen.id"), primary_key=True)
    benutzer_id = Column(Integer, ForeignKey("users.id"))
    benutzer = relationship("User", backref="benutzer_bestellungen")

    __mapper_args__ = {
        "polymorphic_identity": "benutzer"
    }

    def __init__(self, benutzer_id, produkte):
        super().__init__(produkte=produkte)
        self.benutzer_id = benutzer_id

# ▶ Subtyp für Gäste
class GastBestellung(BestellungBase):
    """
    Speichert Bestellungen von nicht angemeldeten Nutzern (Gästen).
    Identifikation erfolgt über eine zufällige Session-ID.
    """
    __tablename__ = "gast_bestellungen"
    id = Column(Integer, ForeignKey("bestellungen.id"), primary_key=True)
    gast_id = Column(String)  # Session-basierte ID

    __mapper_args__ = {
        "polymorphic_identity": "gast"
    }

    def __init__(self, gast_id, produkte):
        super().__init__(produkte=produkte)
        self.gast_id = gast_id
