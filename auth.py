from passlib.context import CryptContext
from jose import jwt, JWTError
import time
import os
from dotenv import load_dotenv

# Lade Umgebungsvariablen (z. B. SECRET_KEY)
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

# Passwort-Kontext für sichere Hashing-Methoden (bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Ablaufzeit des Tokens in Sekunden (24 Stunden)
TOKEN_EXPIRE_SECONDS = 60 * 60 * 24

def create_access_token(data: dict, expires_delta: int = TOKEN_EXPIRE_SECONDS):
    """
    Erzeuge ein JWT-Zugriffstoken mit Ablaufzeit.
    :param data: Daten, die im Token enthalten sein sollen (z. B. {"sub": "username"})
    :param expires_delta: Gültigkeitsdauer in Sekunden
    :return: Kodiertes JWT-Token als String
    """
    payload = data.copy()
    payload.update({"exp": time.time() + expires_delta})
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str):
    """
    Verifiziere ein JWT-Token und extrahiere den Benutzername (sub).
    :param token: Das übergebene JWT-Token
    :return: Benutzername oder None, wenn ungültig
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None

# ---------------------------------------
# FastAPI-spezifische Login-/Logout-Logik
# ---------------------------------------

from fastapi import APIRouter, Form, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from models import User
from db import get_db

templates = Jinja2Templates(directory="templates")
router = APIRouter()

def get_current_user_optional(request: Request):
    """
    Extrahiere aktuell eingeloggten Benutzer (optional).
    :param request: HTTP-Request-Objekt
    :return: Benutzername aus Cookie oder None
    """
    token = request.cookies.get("access_token")
    if token:
        username = verify_token(token)
        return username
    return None

@router.get("/login")
def login_page(request: Request):
    """
    Zeige die Login-Seite.
    """
    current_user = get_current_user_optional(request)
    return templates.TemplateResponse("login.html", {
        "request": request,
        "current_user": current_user
    })

@router.post("/login")
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Verarbeite Login-Formular, validiere Benutzer.
    Bei Erfolg: Setze JWT-Cookie und leite weiter.
    """
    db_user = db.query(User).filter_by(username=username).first()
    
    if db_user and db_user.verify_password(password):
        token = create_access_token({"sub": username})
        response = RedirectResponse("/", status_code=303)
        response.set_cookie(key="access_token", value=token, httponly=True)
        return response

    return templates.TemplateResponse("login.html", {
        "request": request,
        "error": "Ungültige Anmeldedaten"
    })

@router.get("/register")
def register_page(request: Request):
    """
    Zeige die Registrierungsseite.
    """
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/register")
def register(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Verarbeite Registrierung:
    Erstelle neuen Benutzer mit sicherem Passwort-Hashing.
    """
    if db.query(User).filter_by(username=username).first():
        raise HTTPException(status_code=400, detail="Benutzer existiert bereits.")

    user = User(username=username, password=password)  # Hashing erfolgt im Model
    db.add(user)
    db.commit()

    return RedirectResponse("/login", status_code=303)

@router.get("/logout")
def logout(request: Request):
    """
    Logge den Benutzer aus, lösche Session & Cookie.
    """
    response = RedirectResponse("/", status_code=303)
    response.delete_cookie(key="access_token")
    request.session.pop("cart", None)
    return response
