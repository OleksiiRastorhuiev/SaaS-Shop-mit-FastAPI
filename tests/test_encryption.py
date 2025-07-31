'''
export PYTHONPATH=$PYTHONPATH:../
pytest tests/test_encryption.py
'''

import pytest
from cryptography.fernet import InvalidToken
from encryption import Encryption

# ✅ Test: Verschlüsselung und Entschlüsselung funktionieren korrekt
def test_encrypt_decrypt():
    """
    Testet, ob ein String korrekt verschlüsselt und wieder entschlüsselt werden kann.
    """
    enc = Encryption()
    original = "Geheime Nachricht 123! 🤫"
    encrypted = enc.encrypt(original)
    decrypted = enc.decrypt(encrypted)

    assert isinstance(encrypted, bytes)
    assert isinstance(decrypted, str)
    assert decrypted == original

# ✅ Test: Fehler bei ungültigem Entschlüsselungs-Token
def test_decrypt_invalid_token():
    """
    Testet, ob eine Exception ausgelöst wird, wenn ein ungültiger Token entschlüsselt werden soll.
    """
    enc = Encryption()
    invalid_data = b"invalidtoken"

    with pytest.raises(InvalidToken):
        enc.decrypt(invalid_data)

# ✅ Test: Mehrfachverschlüsselung desselben Textes ergibt unterschiedliche Ciphertexte
def test_encrypt_returns_different_ciphertexts_for_same_input():
    """
    Testet, ob dieselbe Eingabe bei wiederholter Verschlüsselung unterschiedliche Ausgaben erzeugt.
    Dies zeigt, dass ein zufälliger Initialisierungsvektor verwendet wird.
    """
    enc = Encryption()
    input_text = "immer gleich"
    enc1 = enc.encrypt(input_text)
    enc2 = enc.encrypt(input_text)

    # Obwohl beide entschlüsselten Inhalte gleich sind,
    # sollten die verschlüsselten Bytes unterschiedlich sein
    assert enc1 != enc2
    assert enc.decrypt(enc1) == input_text
    assert enc.decrypt(enc2) == input_text
