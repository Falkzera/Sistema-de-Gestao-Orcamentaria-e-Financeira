import requests
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from unidecode import unidecode
from io import BytesIO
from src.google_drive_utils import read_parquet_file_from_drive, update_base

data_atual = datetime.now()
data_ontem = data_atual - timedelta(days=1)
data_atual = data_atual.date().strftime('%d-%m-%Y')
data_ontem = data_ontem.date().strftime('%d-%m-%Y')

import pandas as pd
from datetime import datetime, timedelta
import requests
from io import BytesIO
from src.google_drive_utils import read_parquet_file_from_drive, update_base

data_atual = datetime.now()
data_ontem = data_atual - timedelta(days=1)
data_atual = data_atual.date().strftime('%d-%m-%Y')
data_ontem = data_ontem.date().strftime('%d-%m-%Y')

def funcao_sefaz_receita_completo():
    try:
        print(' ')
        print('Atualizando DOTAÇÃO...')
        print(' ')

        try:
            url = f'https://extrator.sefaz.al.gov.br/RECEITAS/receita_consolidado_2018_2025_siafe_gerado_em_{data_ontem}.xlsx'

            response = requests.get(url, verify=False)
            df = pd.read_excel(BytesIO(response.content))
        except: 
            url = f'https://extrator.sefaz.al.gov.br/RECEITAS/receita_consolidado_2018_2025_siafe_gerado_em_{data_atual}.xlsx'
            response = requests.get(url, verify=False)
            df = pd.read_excel(BytesIO(response.content))
        
    except Exception as e:
        print('Erro na atualização da DOTAÇÃO:')
        print(e)

    df['DATA'] = df['ANO'].astype(str) + '-' + df['MES'].astype(str)
    df['DATA'] = pd.to_datetime(df['DATA'], format='%Y-%m')
    df['DATA'] = df['DATA'].dt.strftime('%m-%Y')
    df.drop(['ANO', 'MES'], axis=1, inplace=True)

    colunas_str = ['PODER', 'COD_TIPO_ADMIN', 'NOM_TIPO_ADMIN', 'UG', 'DESCRICAO_UG',
        'FONTE_MAE', 'DESCRICAO_FONTE_MAE', 'FONTE', 'DESCRICAO_FONTE',
        'NATUREZA1', 'DESCRICAO_NATUREZA1', 'NATUREZA2', 'DESCRICAO_NATUREZA2',
        'NATUREZA3', 'DESCRICAO_NATUREZA3', 'NATUREZA4', 'DESCRICAO_NATUREZA4',
        'NATUREZA5', 'DESCRICAO_NATUREZA5', 'NATUREZA6', 'DESCRICAO_NATUREZA6']


    for column in colunas_str:
        df[column] = df[column].astype(str)


    df = df[['DATA', 'PODER', 'COD_TIPO_ADMIN', 'NOM_TIPO_ADMIN', 'UG', 'DESCRICAO_UG',
        'FONTE_MAE', 'DESCRICAO_FONTE_MAE', 'FONTE', 'DESCRICAO_FONTE',
        'NATUREZA1', 'DESCRICAO_NATUREZA1', 'NATUREZA2', 'DESCRICAO_NATUREZA2',
        'NATUREZA3', 'DESCRICAO_NATUREZA3', 'NATUREZA4', 'DESCRICAO_NATUREZA4',
        'NATUREZA5', 'DESCRICAO_NATUREZA5', 'NATUREZA6', 'DESCRICAO_NATUREZA6',
        'VALOR_INICIAL_BRUTO_ATUALIZADO', 'VAL_INICIAL_DEDU_FUNDEB',
        'VAL_INICIAL_DEDU_MUNICIPIOS', 'VAL_INICIAL_DEDU_FUN_MUNI',
        'VAL_INICIAL_LIQUIDO', 'VAL_INICIAL_ATUALIZADO', 'VAL_REALIZADO_BRUTO',
        'VAL_REALIZADO_DEDU_FUNDEB', 'VAL_REALIZADO_DEDU_MUNICIPIO',
        'VAL_REALIZADO_DEDU_OUTROS', 'VALOR_REALIZADO_LIQUIDO']]

    df = df.replace('nan', '')
    df['FONTE'] = df['FONTE'].str[:3]

    df_itcmd = df[df['DESCRICAO_NATUREZA6'].str.startswith('Imposto sobre Transmissão Causa Mortis')]
    df_icms = df[df['DESCRICAO_NATUREZA6'].str.startswith('Imposto sobre Operações Relativas à Circulação de Mercadorias')]
    df_ipva = df[df['DESCRICAO_NATUREZA6'].str.startswith('Imposto sobre a Propriedade de Veículos Automotores')]
    df_irrf = df[df['DESCRICAO_NATUREZA6'].str.startswith('Imposto sobre a Renda - Retido na Fonte')]
    df_ipi = df[df['DESCRICAO_NATUREZA6'].str.startswith('Cota-Parte do Imposto Sobre Produtos Industrializados - Estados Exportadores de Produtos Industrializados')]

    df_itcmd.reset_index(drop=True, inplace=True)
    df_icms.reset_index(drop=True, inplace=True)
    df_ipva.reset_index(drop=True, inplace=True)
    df_irrf.reset_index(drop=True, inplace=True)
    df_ipi.reset_index(drop=True, inplace=True)

    print('Subindo no DRIVE...')


    bases = [
        ('df', 'sefaz_dotacao_ano_corrente.parquet'),
        ('df_itcmd', 'sefaz_itcmd_completo.parquet'),
        ('df_icms', 'sefaz_icms_completo.parquet'),
        ('df_ipva', 'sefaz_ipva_completo.parquet'),
        ('df_irrf', 'sefaz_irrf_completo.parquet'),
        ('df_ipi', 'sefaz_ipi_completo.parquet')
    ]

    for nome_base, file_name in bases:
        parquet_buffer = BytesIO()
        eval(nome_base).to_parquet(parquet_buffer, index=False)
        parquet_buffer.seek(0)
        update_base(parquet_buffer, file_name)
        print(f'{file_name} atualizado com sucesso!')