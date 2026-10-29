import importlib.util


def is_ai_available() -> bool:
    """True si les dépendances IA (édition « full ») sont présentes."""
    return all(importlib.util.find_spec(pkg) is not None for pkg in ("torch", "birder"))


AI_AVAILABLE = is_ai_available()
