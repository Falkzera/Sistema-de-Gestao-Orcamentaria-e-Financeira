from .numero_processo import validar_numero_processo
from .valor import validar_valor
from .objetivo import validar_objetivo
from .data import validar_data_recebimento, validar_data_publicacao
from datetime import datetime

def validar_processamento_campos(numero_processo, valor_input, objetivo, data_recebimento, data_publicacao, numero_decreto):
    ano_corrente = datetime.now().year
    erros = []

    if not numero_processo:
        erros.append("Por favor, insira o número do processo.")
    elif not validar_numero_processo(numero_processo):
        
        erros.append(f"❌ Número do processo inválido. Use o formato: E:00000.0000000000/{ano_corrente}")

    if valor_input and not validar_valor(valor_input):
        erros.append("❌ VALOR inválido. Use o formato: 1.000,00 (vírgula para centavos, ponto para milhar)")


    if not validar_objetivo(objetivo):
        erros.append("⚠️ Campo 'Objetivo' está vazio ou inválido.")

    if not validar_data_recebimento(data_recebimento):
        ano_corrente = datetime.now().year
        erros.append(f"❌ DATA de recebimento inválida. NÃO é possível cadastrar um processo com o ano de recebimento diferente do ano corrente ({ano_corrente}), ceritfique-se também de utilizar o formato correto: DD/MM/AAAA")

    if data_publicacao and not validar_data_publicacao(data_publicacao):
        erros.append("❌ Data de publicação inválida. Use o formato: DD/MM/AAAA")


    return erros
