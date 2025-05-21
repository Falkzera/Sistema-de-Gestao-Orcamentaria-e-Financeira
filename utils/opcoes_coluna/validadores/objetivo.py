# utils/validadores/objetivo.py

def validar_objetivo(texto: str) -> bool:
    """Valida se o objetivo não está vazio ou só com espaços."""
    return bool(texto and texto.strip())
