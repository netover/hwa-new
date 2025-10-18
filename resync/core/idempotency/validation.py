"""
Validação de chaves de idempotency.
"""

import re
from typing import Optional


class IdempotencyKeyValidator:
    """Validador de chaves de idempotency"""

    UUID_PATTERN = re.compile(
        r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$",
        re.IGNORECASE,
    )

    @classmethod
    def is_valid(cls, key: str) -> bool:
        """Verifica se a chave é um UUID v4 válido"""
        return bool(cls.UUID_PATTERN.match(key))

    @classmethod
    def validate(cls, key: str) -> str:
        """Valida e retorna a chave se válida"""
        if not key:
            raise ValueError("Idempotency key cannot be empty")
        if not cls.is_valid(key):
            raise ValueError(f"Invalid idempotency key format: {key}")
        return key
