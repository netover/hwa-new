import hashlib
import json
from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Callable


def cache_response(ttl_seconds: int = 30):
    """
    Um decorador de cache em memória com tempo de vida (TTL) para funções assíncronas.
    """
    def decorator(func: Callable[..., Any]):
        cache = {}

        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Cria uma chave de cache baseada no nome da função e nos argumentos
            # O primeiro argumento (self) é ignorado para que a chave seja a mesma entre instâncias
            key_args = args[1:]
            key_kwargs = sorted(kwargs.items())
            cache_key_parts = (func.__name__, key_args, tuple(key_kwargs))
            cache_key = hashlib.md5(json.dumps(str(cache_key_parts)).encode()).hexdigest()

            # Verifica o cache
            if cache_key in cache:
                data, timestamp = cache[cache_key]
                if datetime.now() - timestamp < timedelta(seconds=ttl_seconds):
                    print(f"CACHE HIT: Usando resultado em cache para '{func.__name__}'.")
                    return data

            # Executa a função e armazena o resultado no cache
            print(f"CACHE MISS: Executando função '{func.__name__}'.")
            result = await func(*args, **kwargs)
            cache[cache_key] = (result, datetime.now())
            return result

        return wrapper
    return decorator
