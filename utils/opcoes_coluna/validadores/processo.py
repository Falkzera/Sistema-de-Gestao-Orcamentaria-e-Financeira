from .numero_processo import validar_numero_processo
from .valor import validar_valor
from .objetivo import validar_objetivo
from .data import validar_data_recebimento, validar_data_publicacao
from .validar_campos_livres import validar_sanitizar_campos_livres
from datetime import datetime

def validar_processamento_campos(numero_processo, valor_input, data_recebimento, data_publicacao, numero_decreto=None, objetivo=None, observacao=None, obs_sop=None):
    ano_corrente = datetime.now().year
    erros = []
    campos_sanitizados = {}

    if not numero_processo:
        erros.append("Por favor, insira o número do processo.")
    elif not validar_numero_processo(numero_processo):
        
        erros.append(f"❌ Número do processo inválido. Use o formato: E:00000.0000000000/{ano_corrente}")

    if valor_input and not validar_valor(valor_input):
        erros.append("❌ VALOR inválido. Use o formato: 1.000,00 (vírgula para centavos, ponto para milhar)")

    if not validar_data_recebimento(data_recebimento):
        erros.append(f"❌ DATA de recebimento inválida. NÃO é possível cadastrar um processo com o ano de recebimento diferente do ano corrente ({ano_corrente}), ceritfique-se também de utilizar o formato correto: DD/MM/AAAA")

    if data_publicacao and not validar_data_publicacao(data_publicacao):
        erros.append("❌ Data de publicação inválida. Use o formato: DD/MM/AAAA")

    if objetivo is not None:
        if objetivo:
                valido, sanitizado = validar_sanitizar_campos_livres(objetivo)
                if valido:
                    campos_sanitizados['objetivo'] = sanitizado
                else:
                    erros.append("❌ O campo Objetivo não pode estar vazio.")
        else:
            erros.append("❌ Por favor, preencha o campo Objetivo.")

        # Observação (opcional)
    if observacao is not None:
        if observacao:
            valido, sanitizado = validar_sanitizar_campos_livres(observacao)
            if valido:
                campos_sanitizados['observacao'] = sanitizado
        else:
            campos_sanitizados['observacao'] = ""  # Campo opcional

    # Observação SOP (opcional)
    if obs_sop is not None:
        if obs_sop:
            valido, sanitizado = validar_sanitizar_campos_livres(obs_sop)
            if valido:
                campos_sanitizados['obs_sop'] = sanitizado
        else:
            campos_sanitizados['obs_sop'] = ""  # Campo opcional


    return erros, campos_sanitizados

