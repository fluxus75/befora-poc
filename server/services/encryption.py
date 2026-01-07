from __future__ import annotations

import os

from cryptography.fernet import Fernet


class EncryptionService:
    def __init__(self, key: str | None = None) -> None:
        secret = key or os.getenv("DB_ENCRYPTION_KEY")
        if not secret:
            raise ValueError("DB_ENCRYPTION_KEY is required for at-rest encryption")
        self.cipher = Fernet(secret.encode("utf-8"))

    def encrypt(self, plaintext: str | None) -> str | None:
        if plaintext is None:
            return None
        return self.cipher.encrypt(plaintext.encode("utf-8")).decode("utf-8")

    def decrypt(self, ciphertext: str | None) -> str | None:
        if ciphertext is None:
            return None
        return self.cipher.decrypt(ciphertext.encode("utf-8")).decode("utf-8")
