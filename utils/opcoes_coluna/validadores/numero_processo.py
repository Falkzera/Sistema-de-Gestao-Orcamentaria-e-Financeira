regex_numero_processo = r"^E:\d{5}\.\d{10}/\d{4}$"

def validar_numero_processo(valor: str) -> bool:
    """Valida o número do processo no formato: E:23010.0000000000/2025"""
    import re
    return re.match(regex_numero_processo, valor) is not None
