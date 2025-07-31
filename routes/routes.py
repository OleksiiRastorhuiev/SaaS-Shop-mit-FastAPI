# routes.py:
from fastapi import APIRouter, Request, Form, Depends, HTTPException, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from models import Product, User
from models import BenutzerBestellung, GastBestellung
from uuid import uuid4
from recommendation.rules_engine import recommend_products
from db import get_db
import time
from auth import templates, verify_token
from auth import get_current_user_optional
from urllib.parse import quote_plus
from auth import get_current_user_optional

router = APIRouter()

# ----------------------------------------
# Produktübersicht (Startseite)
# ----------------------------------------
@router.get("/", response_class=HTMLResponse)
def index(request: Request, db: Session = Depends(get_db), search: str = "", success: str = ""):
    """
    Zeigt alle Produkte an, optional mit Suchfilter. 
    Berechnet Preise mit/ohne Rabatt und zeigt Erfolgsmeldung bei Bestellung.
    """
    username = get_current_user_optional(request)
    rabatt = username is not None

    if request.session.get("order_completed"):
        request.session["order_completed"] = False
        return RedirectResponse(url="/?success=true", status_code=303)

    cart = request.session.get("cart", [])
    request.session["product_count"] = len(cart)

    query = db.query(Product)
    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))
    products = query.all()

    rabattierte_preise = {p.id: round(p.price * 0.9, 2) for p in products} if rabatt else {}
    gesamt = sum(p["price"] * 0.9 if rabatt else p["price"] for p in cart)

    success_message = "Bestellung wurde erfolgreich abgegeben!" if success == "true" else ""

    return templates.TemplateResponse("index.html", {
        "request": request,
        "products": products,
        "cart": cart,
        "username": username,
        "rabatt": rabatt,
        "rabattierte_preise": rabattierte_preise,
        "search": search,
        "success": success_message,
        "gesamtpreis": round(gesamt, 2),
        "product_count": len(cart)
    },
    headers={
        "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
        "Pragma": "no-cache",
    })

# ----------------------------------------
# Zeigt Produktliste separat an
# ----------------------------------------
@router.get("/products")
def get_products(db: Session = Depends(get_db)):
    """
    Zeigt alle Produkte als eigene Seite an.
    """
    products = db.query(Product).all()
    return templates.TemplateResponse("products.html", {"products": products})

# ----------------------------------------
# Produkt zum Warenkorb hinzufügen
# ----------------------------------------
@router.post("/add_to_cart")
def add_to_cart(request: Request, product_id: int = Form(...), db: Session = Depends(get_db)):
    """
    Fügt ein Produkt dem Warenkorb (Session) hinzu.
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if product:
        product_dict = {
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "price": product.price
        }
        cart = request.session.get("cart", [])
        cart.append(product_dict)
        request.session["cart"] = cart
        request.session["modified"] = time.time()
    return RedirectResponse("/", status_code=303)

# ----------------------------------------
# Produkt aus dem Warenkorb entfernen
# ----------------------------------------
@router.post("/remove_from_cart")
def remove_from_cart(request: Request, product_id: int = Form(...), db: Session = Depends(get_db)):
    """
    Entfernt ein Produkt aus dem Warenkorb.
    """
    cart = request.session.get("cart", [])
    updated_cart = [p for p in cart if p["id"] != product_id]
    request.session["cart"] = updated_cart
    request.session["product_count"] = len(updated_cart)
    request.session["modified"] = time.time()

    if not updated_cart:
        request.session.pop("cart", None)
    return RedirectResponse("/", status_code=303)

# ----------------------------------------
# Vorbereitung zur Bestellung (nur wenn eingeloggt)
# ----------------------------------------
@router.post("/bestellen")
def bestellen(request: Request, db: Session = Depends(get_db)):
    """
    Leitet zur Bestellung weiter, nur wenn Benutzer eingeloggt ist.
    """
    cart = request.session.get("cart", {})
    
    if not cart:
        return templates.TemplateResponse("checkout.html", {
            "request": request,
            "error": "Ihr Warenkorb ist leer."
        })

    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse("/login", status_code=303)
    
    username = verify_token(token)
    if not username:
        return RedirectResponse("/login", status_code=303)
    
    user = db.query(User).filter_by(username=username).first()
    if not user:
        return RedirectResponse("/login", status_code=303)

# ----------------------------------------
# Bestellung final abschließen (Benutzer oder Gast)
# ----------------------------------------
@router.post("/checkout")
def checkout(request: Request, db: Session = Depends(get_db), user = Depends(get_current_user_optional)):
    """
    Speichert eine Bestellung in der Datenbank – für Benutzer oder Gäste.
    """
    cart = request.session.get("cart", [])

    if not cart:
        return RedirectResponse("/", status_code=303)

    if isinstance(user, str):
        user = db.query(User).filter_by(username=user).first()

    produkt_mengen = {}
    for p in cart:
        key = p["name"]
        produkt_mengen[key] = produkt_mengen.get(key, 0) + 1

    produkte_string = ", ".join([f"{name} x {anzahl}" for name, anzahl in produkt_mengen.items()])
    benutzer_id = user.id if user else None

    session_id = request.session.get("gast_id")
    if not session_id:
        session_id = str(uuid4())
        request.session["gast_id"] = session_id

    try:
        if benutzer_id:
            bestellung = BenutzerBestellung(benutzer_id=benutzer_id, produkte=produkte_string)
            print(f"✅ Bestellung gespeichert für: {user.username}")
        else:
            bestellung = GastBestellung(gast_id=session_id, produkte=produkte_string)
            print("✅ Bestellung gespeichert (Gast)")

        db.add(bestellung)
        db.commit()
    except Exception as e:
        db.rollback()
        print("❌ Fehler beim Speichern:", e)

    request.session.pop("cart", None)
    request.session["product_count"] = 0
    request.session["order_completed"] = True

    return RedirectResponse("/bestellung_erfolgreich", status_code=303)

# ----------------------------------------
# Erfolgsseite nach Bestellung
# ----------------------------------------
@router.get("/bestellung_erfolgreich")
def bestellung_erfolgreich(request: Request):
    """
    Zeigt eine Seite nach erfolgreicher Bestellung an.
    """
    return templates.TemplateResponse("bestellung_erfolgreich.html", {"request": request})

# ----------------------------------------
# Fragen für das Quiz (Product Recommendation)
# ----------------------------------------
questions = [
    ("department", "In welcher Abteilung arbeiten Sie? (z. B. HR, IT, Sales, Finance, Admin)"),
    ("remote_work", "Arbeiten Sie remote? (yes/no)"),
    ("needs_training", "Benötigt Ihr Team Schulungen? (yes/no)"),
    ("expense_handling", "Müssen Sie Reisekosten verwalten? (yes/no)"),
    ("document_handling", "Arbeiten Sie mit vielen Dokumenten? (yes/no)"),
    ("security_concern", "Sind IT-Sicherheitsaspekte besonders wichtig? (yes/no)"),
    ("team_size", "Wie groß ist Ihr Team? (small/medium/large)")
]

# ----------------------------------------
# Einzelne Quizfrage anzeigen
# ----------------------------------------
@router.get("/quiz", response_class=HTMLResponse)
def quiz_get(request: Request, q: int = 0):
    """
    Zeigt die aktuelle Quizfrage (basierend auf Index q).
    """
    if q >= len(questions):
        return RedirectResponse("/quiz/result", status_code=303)

    key, text = questions[q]
    return templates.TemplateResponse("quiz_question.html", {
        "request": request,
        "question_number": q,
        "question_key": key,
        "question_text": text,
    })

# ----------------------------------------
# Quizantwort verarbeiten und nächste Frage anzeigen
# ----------------------------------------
@router.post("/quiz", response_class=HTMLResponse)
async def quiz_post(request: Request, question_key: str = Form(...), answer: str = Form(...), q: int = Form(...)):
    """
    Speichert die Antwort in der Session und leitet zur nächsten Frage weiter.
    """
    session = request.session if hasattr(request, "session") else {}
    session = request.session = session or {}
    session[question_key] = answer

    next_q = int(q) + 1
    if next_q >= len(questions):
        return RedirectResponse("/quiz/result", status_code=303)
    else:
        return RedirectResponse(f"/quiz?q={next_q}", status_code=303)

# ----------------------------------------
# Ergebnis und Empfehlungen nach dem Quiz anzeigen
# ----------------------------------------
@router.get("/quiz/result", response_class=HTMLResponse)
def quiz_result(request: Request):
    """
    Liest alle Antworten aus der Session und zeigt Produktempfehlungen.
    """
    session = request.session if hasattr(request, "session") else {}
    answers = {
        q[0]: session.get(q[0], "")
        for q in questions
    }
    recommendations = recommend_products(answers)
    return templates.TemplateResponse("quiz_result.html", {
        "request": request,
        "recommendations": recommendations,
        "answers": answers,
        "back_to_homepage": True
    })

# ----------------------------------------
# Produktempfehlungen direkt via POST senden
# ----------------------------------------
@router.post("/recommendations", response_class=HTMLResponse)
def get_recommendations(
    request: Request,
    department: str = Form(...),
    remote_work: str = Form(...),
    needs_training: str = Form(...),
    expense_handling: str = Form(...),
    document_handling: str = Form(...),
    security_concern: str = Form(...),
    team_size: str = Form(...)
):
    """
    Liefert Produktempfehlungen direkt aus Formularantworten (ohne Quizflow).
    """
    answers = {
        "department": department,
        "remote_work": remote_work,
        "needs_training": needs_training,
        "expense_handling": expense_handling,
        "document_handling": document_handling,
        "security_concern": security_concern,
        "team_size": team_size
    }
    recommendations = recommend_products(answers)
    return templates.TemplateResponse("quiz_result.html", {
        "request": request,
        "recommendations": recommendations,
        "answers": answers
    })
