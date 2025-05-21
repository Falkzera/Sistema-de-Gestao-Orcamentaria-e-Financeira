# utils/validadores/valor.py

import re

def validar_valor(valor_str: str) -> bool:
    """
    Valida se o valor está no formato brasileiro corretamente:
    - Obrigatório
    - Decimal separado por vírgula
    - Milhar separado por ponto
    - Duas casas decimais apenas
    Ex: '123.456,78' ✅
    """
    if not valor_str or not valor_str.strip():
        return False

    # Regex para validar formato exato BR: 1.234.567,89 ou 12,34
    padrao = r"^(\d{1,3}(\.\d{3})*|\d+),\d{2}$"
    if not re.match(padrao, valor_str):
        return False

    try:
        # Converte para float removendo milhar e trocando decimal
        valor_normalizado = valor_str.replace('.', '').replace(',', '.')
        float(valor_normalizado)
        return True
    except ValueError:
        return False


def formatar_valor_br(valor_str: str) -> str:
    """
    Formata para padrão brasileiro:
    - Insere ponto como separador de milhar
    - Usa vírgula como separador decimal
    Ex: '1234567.89' → '1.234.567,89'
    """
    try:
        # Remove tudo que não for número ou vírgula
        valor_normalizado = valor_str.replace('.', '').replace(',', '.')
        valor_float = float(valor_normalizado)
        return f"{valor_float:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    except:
        return valor_str  # Retorna original se erro
