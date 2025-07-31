'''
Ausführen mit:
export PYTHONPATH=$PYTHONPATH:../
pytest tests/test_rules_engine.py
'''

import pytest
from recommendation.rules_engine import recommend_products

def test_recommendation_hr_remote_expense_large_team():
    """
    Testfall: HR-Abteilung mit Remote-Arbeit, Spesenverwaltung, großes Team
    Erwartung: 3 Produktempfehlungen, alphabetisch sortiert
    """
    answers = {
        "department": "HR",
        "remote_work": "yes",
        "needs_training": "no",
        "expense_handling": "yes",
        "document_handling": "no",
        "security_concern": "no",
        "team_size": "large"
    }

    result = recommend_products(answers)
    assert isinstance(result, list)
    assert len(result) == 3
    assert result == sorted(result)  # Alphabetische Sortierung sicherstellen
    assert all(isinstance(r, str) for r in result)

def test_recommendation_it_security_yes():
    """
    Testfall: IT-Abteilung mit Fokus auf Sicherheit
    Erwartung: 3 sicherheitsrelevante Empfehlungen, alphabetisch sortiert
    """
    answers = {
        "department": "IT",
        "remote_work": "no",
        "needs_training": "no",
        "expense_handling": "no",
        "document_handling": "no",
        "security_concern": "yes",
        "team_size": "small"
    }

    result = recommend_products(answers)
    assert isinstance(result, list)
    assert len(result) == 3
    assert result == sorted(result)
    expected = sorted(["Netzwerk-Sicherheit", "VPN-Lösung", "Zugriffsmanagement", "E-Mail-Archivierung"])[:3]
    assert result == expected

def test_empty_answers_triggers_fallback():
    """
    Testfall: Leere Antworten → Fallback-Produkte
    Erwartung: 3 Standardempfehlungen, alphabetisch sortiert
    """
    answers = {}

    result = recommend_products(answers)
    assert isinstance(result, list)
    assert len(result) == 3
    assert result == sorted(result)
    fallback_products = sorted(["Projektmanagement", "Team Collaboration", "CRM-System"])[:3]
    assert result == fallback_products

def test_training_and_documents():
    """
    Testfall: Bedarf an Schulung + Dokumentenbearbeitung
    Erwartung: Mindestens eines der entsprechenden Produkte empfohlen
    """
    answers = {
        "department": "Finance",
        "remote_work": "no",
        "needs_training": "yes",
        "expense_handling": "no",
        "document_handling": "yes",
        "security_concern": "no",
        "team_size": "small"
    }

    result = recommend_products(answers)
    assert isinstance(result, list)
    assert len(result) == 3
    assert result == sorted(result)
    assert "E-Learning-Plattform" in result or "Digitale Signatur" in result
