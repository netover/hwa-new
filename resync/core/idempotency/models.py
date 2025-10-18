"""
Modelos de dados para o sistema de idempotency.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict


@dataclass
class IdempotencyRecord:
    """Registro de idempotency armazenado"""

    idempotency_key: str
    request_hash: str
    response_data: Dict[str, Any]
    status_code: int
    created_at: datetime
    expires_at: datetime
    request_metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário para serialização"""
        return {
            "idempotency_key": self.idempotency_key,
            "request_hash": self.request_hash,
            "response_data": self.response_data,
            "status_code": self.status_code,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "request_metadata": self.request_metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "IdempotencyRecord":
        """Cria instância a partir de dicionário"""
        return cls(
            idempotency_key=data["idempotency_key"],
            request_hash=data["request_hash"],
            response_data=data["response_data"],
            status_code=data["status_code"],
            created_at=datetime.fromisoformat(data["created_at"]),
            expires_at=datetime.fromisoformat(data["expires_at"]),
            request_metadata=data.get("request_metadata", {}),
        )
