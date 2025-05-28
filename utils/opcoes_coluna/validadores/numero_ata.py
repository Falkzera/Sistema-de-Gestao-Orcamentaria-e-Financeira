import re

def validar_numero_ata(numero: str) -> bool:
    """
    Valida se é um número, porém permite caso seja vazio
    """
    if numero.isnumeric():
        return True
    elif numero == "":
        return True
    else:
        return False
