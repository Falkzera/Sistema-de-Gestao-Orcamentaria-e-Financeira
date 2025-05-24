import pandas as pd
from siconfipy import get_fiscal, get_budget, br_cods
from datetime import datetime
from src.google_drive_utils import update_base
from io import BytesIO

ano_atual = datetime.now().year
ano_passado = ano_atual - 1
anos = list(range(2023, ano_atual))


def funcao_rgf():

    RGF = get_fiscal(anos, period=[1,2,3,4], cod=27)

    RGF['DATA'] = (RGF['exercicio'].astype(str) + '-' + RGF['periodo'].astype(str)) + ' Q'

    DESPESA_COM_PESSOAL_SOBRE_RCL_AJUSTADA = RGF.iloc[0:,[11,15,13,14]].copy()
    DESPESA_COM_PESSOAL_SOBRE_RCL_AJUSTADA = DESPESA_COM_PESSOAL_SOBRE_RCL_AJUSTADA[DESPESA_COM_PESSOAL_SOBRE_RCL_AJUSTADA['coluna'].isin(['% sobre a RCL Ajustada'])]
    DESPESA_COM_PESSOAL_SOBRE_RCL_AJUSTADA = DESPESA_COM_PESSOAL_SOBRE_RCL_AJUSTADA.drop(columns=['coluna'])
    DESPESA_COM_PESSOAL_SOBRE_RCL_AJUSTADA = DESPESA_COM_PESSOAL_SOBRE_RCL_AJUSTADA[DESPESA_COM_PESSOAL_SOBRE_RCL_AJUSTADA['conta'].isin(['DESPESA TOTAL COM PESSOAL - DTP (VI) = (IIIa + IIIb)', 'DESPESA TOTAL COM PESSOAL - DTP (VII) = (IIIa + IIIb)', 'DESPESA TOTAL COM PESSOAL - DTP (VIII) = (IIIa + IIIb)'])].reset_index(drop=True)

    DIVIDIDA_CONSOLIDADA_LIQUIDA_SOBRE_RCL = RGF.iloc[0:,[15,11,13,14]].copy()
    DIVIDIDA_CONSOLIDADA_LIQUIDA_SOBRE_RCL = DIVIDIDA_CONSOLIDADA_LIQUIDA_SOBRE_RCL[DIVIDIDA_CONSOLIDADA_LIQUIDA_SOBRE_RCL['conta'].isin(['% da DCL sobre a RCL (III/RCL)', '% da DCL sobre a RCL AJUSTADA (III/VI)'])].reset_index(drop=True)

    DIVIDA_CONSOLIDADA_SOBRE_RCL = RGF.iloc[0:,[15,11,13,14]].copy()
    DIVIDA_CONSOLIDADA_SOBRE_RCL = DIVIDA_CONSOLIDADA_SOBRE_RCL[DIVIDA_CONSOLIDADA_SOBRE_RCL['conta'].isin(['% da DC sobre a RCL (I/RCL)', '% da DC sobre a RCL AJUSTADA (I/VI)'])].reset_index(drop=True)

    bases = [
        ('RGF', RGF),
        ('DESPESA_COM_PESSOAL_SOBRE_RCL_AJUSTADA', DESPESA_COM_PESSOAL_SOBRE_RCL_AJUSTADA),
        ('DIVIDIDA_CONSOLIDADA_LIQUIDA_SOBRE_RCL', DIVIDIDA_CONSOLIDADA_LIQUIDA_SOBRE_RCL),
        ('DIVIDA_CONSOLIDADA_SOBRE_RCL', DIVIDA_CONSOLIDADA_SOBRE_RCL)
    ]

    # Salva os DataFrames em arquivos Parquet
    for nome_base, base in bases:
        parquet_buffer = BytesIO()
        base.to_parquet(parquet_buffer, index=False)
        parquet_buffer.seek(0)

        # Usando o nome da base como parte do nome do arquivo
        file_name = nome_base + '.parquet'
        update_base(parquet_buffer, file_name)