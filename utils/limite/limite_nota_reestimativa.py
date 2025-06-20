import pandas as pd
import streamlit as st
from src.base import func_load_base_credito_sop_geo

NOTA_REESTIMATIVA_1 = 1_240_891_583
FONTE_500_REESTIMATIVA_1 = 1_159_168_352
FONTE_501_REESTIMATIVA_1 = 19_613_824
FONTE_761_REESTIMATIVA_1 = 62_109_406

NOTA_REESTIMATIVA_2 = 20_000_000_00
NOTA_REESTIMATIVA_3 = 30_000_000_00
NOTA_REESTIMATIVA_4 = 30_000_000_00

def calcular_nota_reestimativa():

    df = func_load_base_credito_sop_geo()
    df['Valor'] = df['Valor'].astype(float)
  
    df_valor_utilizado_nota_1 = df[df['Origem de Recursos'] == 'Sem Cobertura - Atendido pela 1º NR']
    df_valor_utilizado_nota_2 = df[df['Origem de Recursos'] == 'Sem Cobertura - Atendido pela 2º NR']
    df_valor_utilizado_nota_3 = df[df['Origem de Recursos'] == 'Sem Cobertura - Atendido pela 3º NR']
    df_valor_utilizado_nota_4 = df[df['Origem de Recursos'] == 'Sem Cobertura - Atendido pela 4º NR']

    df_valor_utilizado_fonte_500 = df[(df['Origem de Recursos'] == 'Sem Cobertura - Atendido pela 1º NR') & (df['Fonte de Recursos'] == '500')]
    df_valor_utilizado_fonte_501 = df[(df['Origem de Recursos'] == 'Sem Cobertura - Atendido pela 1º NR') & (df['Fonte de Recursos'] == '501')]
    df_valor_utilizado_fonte_761 = df[(df['Origem de Recursos'] == 'Sem Cobertura - Atendido pela 1º NR') & (df['Fonte de Recursos'] == '761')]

    valor_utilizado_fonte_500 = df_valor_utilizado_fonte_500['Valor'].sum()
    valor_utilizado_fonte_501 = df_valor_utilizado_fonte_501['Valor'].sum()
    valor_utilizado_fonte_761 = df_valor_utilizado_fonte_761['Valor'].sum()

    valor_utilizado_nota_1 = df_valor_utilizado_nota_1['Valor'].sum()
    valor_utilizado_nota_2 = df_valor_utilizado_nota_2['Valor'].sum()
    valor_utilizado_nota_3 = df_valor_utilizado_nota_3['Valor'].sum()
    valor_utilizado_nota_4 = df_valor_utilizado_nota_4['Valor'].sum()

    return {
        "valor_utilizado_nota_reestimativa_1": valor_utilizado_nota_1,
        "valor_utilizado_nota_reestimativa_2": valor_utilizado_nota_2,
        "valor_utilizado_nota_reestimativa_3": valor_utilizado_nota_3,
        "valor_utilizado_nota_reestimativa_4": valor_utilizado_nota_4,
        "nota_reestimativa_1": NOTA_REESTIMATIVA_1,
        "nota_reestimativa_2": NOTA_REESTIMATIVA_2,
        "nota_reestimativa_3": NOTA_REESTIMATIVA_3,
        "nota_reestimativa_4": NOTA_REESTIMATIVA_4,
        "saldo_disponivel_nota_reestimativa_1": NOTA_REESTIMATIVA_1 - valor_utilizado_nota_1,
        "saldo_disponivel_nota_reestimativa_2": NOTA_REESTIMATIVA_2 - valor_utilizado_nota_2,
        "saldo_disponivel_nota_reestimativa_3": NOTA_REESTIMATIVA_3 - valor_utilizado_nota_3,
        "saldo_disponivel_nota_reestimativa_4": NOTA_REESTIMATIVA_4 - valor_utilizado_nota_4,
        "percentual_executado_nota_reestimativa_1": (valor_utilizado_nota_1 / NOTA_REESTIMATIVA_1) * 100,
        "percentual_executado_nota_reestimativa_2": (valor_utilizado_nota_2 / NOTA_REESTIMATIVA_2) * 100,
        "percentual_executado_nota_reestimativa_3": (valor_utilizado_nota_3 / NOTA_REESTIMATIVA_3) * 100,
        "percentual_executado_nota_reestimativa_4": (valor_utilizado_nota_4 / NOTA_REESTIMATIVA_4) * 100,
        "valor_utilizado_fonte_500": valor_utilizado_fonte_500,
        "valor_utilizado_fonte_501": valor_utilizado_fonte_501,
        "valor_utilizado_fonte_761": valor_utilizado_fonte_761,
        "fonte_500_reestimativa_1": FONTE_500_REESTIMATIVA_1,
        "fonte_501_reestimativa_1": FONTE_501_REESTIMATIVA_1,
        "fonte_761_reestimativa_1": FONTE_761_REESTIMATIVA_1,
        "saldo_disponivel_fonte_500": FONTE_500_REESTIMATIVA_1 - valor_utilizado_fonte_500,
        "saldo_disponivel_fonte_501": FONTE_501_REESTIMATIVA_1 - valor_utilizado_fonte_501,
        "saldo_disponivel_fonte_761": FONTE_761_REESTIMATIVA_1 - valor_utilizado_fonte_761,
        "percentual_executado_fonte_500": (valor_utilizado_fonte_500 / FONTE_500_REESTIMATIVA_1) * 100,
        "percentual_executado_fonte_501": (valor_utilizado_fonte_501 / FONTE_501_REESTIMATIVA_1) * 100,
        "percentual_executado_fonte_761": (valor_utilizado_fonte_761 / FONTE_761_REESTIMATIVA_1) * 100,
    }