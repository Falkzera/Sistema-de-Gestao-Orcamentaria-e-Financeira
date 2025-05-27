import re

def validar_numero_ata(numero: str) -> bool:
    """
    Valida se é um número
    """
    if numero.isnumeric():
        return True
    else:
        return False
