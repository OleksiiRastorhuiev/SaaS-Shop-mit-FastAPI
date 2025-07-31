import os
from dotenv import load_dotenv
from cryptography.fernet import Fernet

# Lade Umgebungsvariablen aus .env
load_dotenv()

class Encryption:
    """
    Diese Klasse kapselt die Verschlüsselungs- und Entschlüsselungslogik
    basierend auf einem geheimen Schlüssel aus der .env-Datei.
    """

    def __init__(self):
        # Verschlüsselungsschlüssel aus der Umgebungsvariable lesen
        key = os.getenv("ENCRYPTION_KEY")
        if not key:
            raise ValueError("ENCRYPTION_KEY not set in .env file.")
        self.cipher_suite = Fernet(key.encode())

    def encrypt(self, data):
        """
        Verschlüsselt einen String.
        """
        return self.cipher_suite.encrypt(data.encode())

    def decrypt(self, data):
        """
        Entschlüsselt verschlüsselte Daten zurück in einen lesbaren String.
        """
        return self.cipher_suite.decrypt(data).decode()

# Instanz für globale Nutzung im Projekt
encryption = Encryption()
