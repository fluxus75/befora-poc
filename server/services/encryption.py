from __future__ import annotations

import os
from typing import Optional

from cryptography.fernet import Fernet


class EncryptionService:
    def __init__(self, key: Optional[str] = None) -> None:
        secret = key or os.getenv("DB_ENCRYPTION_KEY")
        if not secret:
            raise ValueError("DB_ENCRYPTION_KEY is required for at-rest encryption")
        self.cipher = Fernet(secret.encode("utf-8"))

    def encrypt(self, plaintext: Optional[str]) -> Optional[str]:
        if plaintext is None:
            return None
        return self.cipher.encrypt(plaintext.encode("utf-8")).decode("utf-8")

    def decrypt(self, ciphertext: Optional[str]) -> Optional[str]:
        if ciphertext is None:
            return None
        return self.cipher.decrypt(ciphertext.encode("utf-8")).decode("utf-8")
