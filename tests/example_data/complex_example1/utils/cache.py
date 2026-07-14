from functools import lru_cache


@lru_cache(maxsize=256)
def expensive_lookup(text: str) -> str:
    return f"[cached:{text}]"
