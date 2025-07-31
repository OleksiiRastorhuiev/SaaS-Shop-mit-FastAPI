import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv
from db import SessionLocal  # nutzen wir aus db.py
from models import Product  # Modell wird nun nur noch importiert

# 🔐 .env-Variablen laden (z. B. secret_key für Sessions)
load_dotenv()

# 🚀 FastAPI-Anwendung initialisieren
app = FastAPI()

# 🧠 SessionMiddleware aktivieren (für Warenkorb & Login-Zustand)
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("secret_key")  # aus .env geladen
)

# 📁 Statische Dateien (CSS, JS etc.) einbinden
app.mount("/static", StaticFiles(directory="static"), name="static")

# 🧩 Jinja2-Template-Verzeichnis definieren (HTML-Render)
templates = Jinja2Templates(directory="templates")

# 🛣️ API-Routen importieren und registrieren
from auth import router as auth_router
from routes import router
app.include_router(auth_router)
app.include_router(router)

def seed_data_once():
    """
    Füllt die Datenbank einmalig mit Beispiel-Produkten.
    Wird nur beim ersten Start ausgeführt, wenn noch keine Produkte existieren.
    """
    db = SessionLocal()
    try:
        if db.query(Product).count() == 0:
            demo = [
                Product(name="CRM-System", description="Kundenverwaltung für Unternehmen", price=49.99),
                Product(name="Cloud Storage", description="Sichere Cloud-Speicherung", price=19.99),
                Product(name="Projektmanagement-Tool", description="Planung und Aufgabenverwaltung", price=29.99),
                Product(name="Marketing Automation", description="Automatisierte Marketingprozesse", price=59.99),
                Product(name="Helpdesk-Software", description="Support-Ticket-System", price=39.99),
                Product(name="E-Mail Hosting", description="Professionelle E-Mail-Adressen", price=9.99),
                Product(name="Analytics Dashboard", description="Echtzeit-Berichte und Analysen", price=24.99),
                Product(name="Team Collaboration", description="Kommunikationstools für Teams", price=14.99),
                Product(name="Website-Baukasten", description="Einfache Website-Erstellung", price=29.99),
                Product(name="SEO-Optimierung", description="Suchmaschinen-Optimierung", price=49.99),
                Product(name="Social Media Management", description="Soziale Medien-Verwaltung", price=39.99),
                Product(name="Content Management System", description="Inhaltsverwaltungssystem", price=59.99),
                Product(name="E-Commerce-Plattform", description="Online-Shop-System", price=99.99),
                Product(name="Buchhaltungs-Software", description="Finanzverwaltung und Buchhaltung", price=69.99),
                Product(name="Personalverwaltung", description="Mitarbeiterverwaltung und -planung", price=49.99),
                Product(name="Reisekostenabrechnung", description="Automatisierte Reisekostenabrechnung", price=29.99),
                Product(name="Zeiterfassung", description="Arbeitszeiterfassung und -verwaltung", price=19.99),
                Product(name="Dokumentenmanagement", description="Dokumentenverwaltung und -speicherung", price=39.99),
                Product(name="Datensicherung", description="Automatisierte Datensicherung", price=29.99),
                Product(name="Netzwerk-Sicherheit", description="Netzwerk-Sicherheitslösungen", price=59.99),
                Product(name="Firewall-Management", description="Firewall-Verwaltung und -sicherheit", price=49.99),
                Product(name="Antivirus-Software", description="Viren- und Malware-Schutz", price=19.99),
                Product(name="Backup-Software", description="Daten-Backup und -wiederherstellung", price=29.99),
                Product(name="IT-Service-Management", description="IT-Service- und -support", price=69.99),
                Product(name="Kundenbeziehungsmanagement", description="Kundenbeziehungs- und -verwaltung", price=49.99),
                Product(name="Vertriebsmanagement", description="Vertriebs- und -planung", price=59.99),
                Product(name="Marketing-Software", description="Marketing-Automatisierung und -analyse", price=99.99)
            ]
            db.add_all(demo)
            db.commit()
    finally:
        db.close()

# 🧪 Seed-Funktion beim Start ausführen (nur einmal)
seed_data_once()

def get_db():
    """
    Datenbank-Session für Dependency Injection bereitstellen.
    Wird von FastAPI bei Endpunkten verwendet.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
