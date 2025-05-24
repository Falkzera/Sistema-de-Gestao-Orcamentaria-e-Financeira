def validar_sanitizar_campos_livres(texto: str) -> tuple[bool, str]:
    """
    Valida se a observação não está vazia e sanitiza para evitar injeção de fórmulas.

    Retorna:
        tuple: (é_válido, texto_sanitizado)
    """
    # Verifica se não está vazio
    if not (texto and texto.strip()):
        return False, ""

    # Sanitiza para evitar injeção de fórmulas
    texto_sanitizado = texto.strip()
    if texto_sanitizado and texto_sanitizado[0] in ['=', '+', '-', '@']:
        texto_sanitizado = "'" + texto_sanitizado

    return True, texto_sanitizado