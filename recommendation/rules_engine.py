# rules_engine.py

def recommend_products(answers: dict) -> list:
    """
    Gibt Produktempfehlungen auf Basis einfacher if-else-Regeln zurück.

    Die Empfehlungen basieren auf Antworten aus einem Fragebogen oder Formular,
    in dem Nutzer:innen verschiedene Anforderungen angeben. Es wird ein Set
    von maximal 3 passenden Produkten zurückgegeben.

    Parameter:
        answers (dict): Enthält Nutzerantworten, z. B.:
            {
                "department": "HR",
                "remote_work": "yes",
                "needs_training": "no",
                "expense_handling": "yes",
                "document_handling": "no",
                "security_concern": "no",
                "team_size": "large"
            }

    Rückgabe:
        Liste mit bis zu 3 empfohlenen Produktnamen (alphabetisch sortiert).
    """

    department = answers.get("department", "").lower()
    remote = answers.get("remote_work", "").lower()
    needs_training = answers.get("needs_training", "").lower()
    expense_handling = answers.get("expense_handling", "").lower()
    document_handling = answers.get("document_handling", "").lower()
    security_concern = answers.get("security_concern", "").lower()
    team_size = answers.get("team_size", "").lower()

    recommended = set()

    # 📌 1. Abteilungsbasierte Empfehlungen
    if "hr" in department:
        recommended.update(["Personalverwaltung", "Lohnabrechnung", "Onboarding-Tool"])
    elif "it" in department:
        recommended.update(["Netzwerk-Sicherheit", "VPN-Lösung", "Zugriffsmanagement"])
    elif "sales" in department:
        recommended.update(["CRM-System", "Marketing Automation", "Kundensupport-Plattform"])
    elif "finance" in department:
        recommended.update(["Finanzbuchhaltung", "Spesenmanagement", "Reisekostenabrechnung"])
    elif "project" in department or "pm" in department:
        recommended.update(["Projektmanagement", "Cloud-Speicher", "Aufgabenverwaltung"])
    elif "admin" in department:
        recommended.update(["DMS (Dokumentenmanagementsystem)", "Inventarverwaltung", "Digitale Signatur"])

    # 📌 2. Remote-Arbeit
    if remote == "yes":
        recommended.update(["Mobiles Arbeiten", "Video-Konferenzsystem", "Team Collaboration"])

    # 📌 3. Schulungsbedarf
    if needs_training == "yes":
        recommended.add("E-Learning-Plattform")

    # 📌 4. Reisekosten
    if expense_handling == "yes":
        recommended.update(["Reisekostenabrechnung", "Spesenmanagement"])

    # 📌 5. Dokumentenverarbeitung
    if document_handling == "yes":
        recommended.update(["DMS (Dokumentenmanagementsystem)", "Digitale Signatur"])

    # 📌 6. Sicherheitsbedenken
    if security_concern == "yes":
        recommended.update(["Netzwerk-Sicherheit", "E-Mail-Archivierung", "Zugriffsmanagement"])

    # 📌 7. Teamgröße
    if team_size == "large":
        recommended.add("Zeiterfassung")
        recommended.add("Helpdesk-System")
        recommended.add("Enterprise Search")

    # 📌 Standard-Fallback, falls keine Regel greift
    if not recommended:
        recommended.update(["Projektmanagement", "Team Collaboration", "CRM-System"])

    # Gib maximal 3 Empfehlungen zurück, alphabetisch sortiert
    return sorted(list(recommended))[:3]

# Beispielhafte Nutzung der Engine
answers = {
    "department": "HR",
    "remote_work": "yes",
    "needs_training": "no",
    "expense_handling": "yes",
    "document_handling": "no",
    "security_concern": "no",
    "team_size": "large"
}

recommended_products = recommend_products(answers)
#print(recommended_products)
# → ['Lohnabrechnung', 'Mobiles Arbeiten', 'Personalverwaltung'] (z. B.)
