import requests
import pandas as pd
from datetime import datetime, timedelta
from unidecode import unidecode
from io import BytesIO
from src.google_drive_utils import read_parquet_file_from_drive, update_base

data_atual = datetime.now()
data_ontem = data_atual - timedelta(days=1)
data_atual = data_atual.date().strftime('%d-%m-%Y')
data_ontem = data_ontem.date().strftime('%d-%m-%Y')

def funcao_sefaz_despesa_ano_corrente():
    try:
        print(' ')
        print('Atualizando DESPESA...')
        print(' ')

        try:
            url = f'https://extrator.sefaz.al.gov.br/DESPESAS/COMPARATIVO-DESPESAS/despesa_empenhado_liquidado_pago_2025_siafe_gerado_em_{data_ontem}.xlsx'
            response = requests.get(url, verify=False)
            df = pd.read_excel(BytesIO(response.content))
        except: 
            url = f'https://extrator.sefaz.al.gov.br/DESPESAS/COMPARATIVO-DESPESAS/despesa_empenhado_liquidado_pago_2025_siafe_gerado_em_{data_atual}.xlsx'
            response = requests.get(url, verify=False)
            df = pd.read_excel(BytesIO(response.content))

    except Exception as e:
        print('Erro na atualização da DESPESA:')
        print(e)

    sigla = read_parquet_file_from_drive('sigla.parquet')
    sigla['UO'] = sigla['UO'].astype('object')
    print('Antes da adição da coluna, o df tinha:', df.shape)
    sigla_dict = sigla.set_index('UO')['SIGLA_UO'].to_dict()
    df['SIGLA_UO'] = df['UO'].map(sigla_dict)
    print('Depois da adição da coluna, o df tem:', df.shape)
    df['DATA'] = df['ANO'].astype(str) + '-' + df['MES'].astype(str)
    df['DATA'] = pd.to_datetime(df['DATA'], format='%Y-%m')
    df['DATA'] = df['DATA'].dt.strftime('%m-%Y')
    df.drop(['ANO', 'MES'], axis=1, inplace=True)

    df = df[['DATA','PODER', 'UO', 'SIGLA_UO', 'DESCRICAO_UO', 'UG', 'DESCRICAO_UG', 'FUNCAO',
        'DESCRICAO_FUNCAO', 'SUB_FUNCAO', 'DESCRICAO_SUB_FUNCAO', 'PROGRAMA',
        'PROGRAMA_DESCRICAO', 'PROJETO', 'PROJETO_DESCRICAO', 'PT',
        'PT_DESCRICAO', 'FONTE_MAE', 'DESCRICAO_FONTE_MAE', 'FONTE',
        'DESCRICAO_FONTE', 'NATUREZA1', 'DESCRICAO_NATUREZA1', 'NATUREZA2',
        'DESCRICAO_NATUREZA2', 'NATUREZA3', 'DESCRICAO_NATUREZA3', 'NATUREZA4',
        'DESCRICAO_NATUREZA4', 'NATUREZA5', 'DESCRICAO_NATUREZA5', 'NATUREZA6',
        'DESCRICAO_NATUREZA6', 'NATUREZA', 'DESCRICAO_NATUREZA', 'CODIGO_FAVORECIDO', 'NOME_FAVORECIDO', 'COD_CREDOR_RETENCAO', 'NOME_CREDOR_RETENCAO',
        'COD_TIPO_LICITACAO', 'TIPO_LICITACAO', 
        'VALOR_EMPENHADO', 'VALOR_LIQUIDADO', 'VALOR_PAGO']]

    df['SIGLA_UO'] = df['SIGLA_UO'].fillna(df['DESCRICAO_UO'])

    colunas_str = ['DATA','PODER', 'UO', 'SIGLA_UO', 'DESCRICAO_UO', 'UG', 'DESCRICAO_UG', 'FUNCAO',
            'DESCRICAO_FUNCAO', 'SUB_FUNCAO', 'DESCRICAO_SUB_FUNCAO', 'PROGRAMA',
            'PROGRAMA_DESCRICAO', 'PROJETO', 'PROJETO_DESCRICAO', 'PT',
            'PT_DESCRICAO', 'FONTE_MAE', 'DESCRICAO_FONTE_MAE', 'FONTE',
            'DESCRICAO_FONTE', 'NATUREZA1', 'DESCRICAO_NATUREZA1', 'NATUREZA2',
            'DESCRICAO_NATUREZA2', 'NATUREZA3', 'DESCRICAO_NATUREZA3', 'NATUREZA4',
            'DESCRICAO_NATUREZA4', 'NATUREZA5', 'DESCRICAO_NATUREZA5', 'NATUREZA6',
            'DESCRICAO_NATUREZA6', 'NATUREZA', 'DESCRICAO_NATUREZA', 'CODIGO_FAVORECIDO', 'NOME_FAVORECIDO', 'COD_CREDOR_RETENCAO', 'NOME_CREDOR_RETENCAO',
            'COD_TIPO_LICITACAO', 'TIPO_LICITACAO']

    for column in colunas_str:
        df[column] = df[column].astype(str)

    df = df.replace('nan', '')
    df['PT'] = df['PT'].str[:13]

    print('Subindo no DRIVE...')

    parquet_buffer = BytesIO()
    df.to_parquet(parquet_buffer, index=False)
    parquet_buffer.seek(0)  
    update_base(parquet_buffer, 'sefaz_despesa_ano_corrente.parquet')
    print('Atualização concluída com sucesso!')