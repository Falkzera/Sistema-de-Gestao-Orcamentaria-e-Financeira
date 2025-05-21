# utils/validadores/observacao.py

def validar_observacao(texto: str) -> bool:
    """Valida se a observação não está vazia ou só com espaços."""
    return bool(texto and texto.strip())
