# utils/validadores/data.py
import streamlit as st
from datetime import datetime

def validar_data_br(data_str: str) -> bool:
    """
    Valida se a data está no formato brasileiro: DD/MM/AAAA.
    """
    if not data_str:
        return False
    try:
        datetime.strptime(data_str.strip(), "%d/%m/%Y")
        return True
    except ValueError:
        return False

def validar_data_recebimento(data_str: str) -> bool:
    """
    Valida a data de recebimento como obrigatória, no formato DD/MM/AAAA,
    impede que seja uma data futura e verifica se está no ano corrente.
    """
    if not validar_data_br(data_str):
        return False
    data = datetime.strptime(data_str.strip(), "%d/%m/%Y")
    now = datetime.now()
    return data <= now and data.year == now.year

def validar_data_publicacao(data_str: str) -> bool:
    """
    Valida a data de publicação como opcional, permitindo que esteja em branco,
    mas se preenchida, deve estar no formato DD/MM/AAAA e não pode ser uma data futura.
    """
    if not data_str or data_str.strip() == "":
        return True  # Permitir campo em branco
    if not validar_data_br(data_str):
        return False
    data = datetime.strptime(data_str.strip(), "%d/%m/%Y")
    now = datetime.now()
    return data <= now  # Impedir data futura
