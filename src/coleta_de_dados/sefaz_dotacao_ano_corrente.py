import pandas as pd
from datetime import datetime, timedelta
import requests
from io import BytesIO
from src.google_drive_utils import read_parquet_file_from_drive, update_base

data_atual = datetime.now()
data_ontem = data_atual - timedelta(days=1)
data_atual = data_atual.date().strftime('%d-%m-%Y')
data_ontem = data_ontem.date().strftime('%d-%m-%Y')

def funcao_sefaz_dotacao_ano_corrente():
    try:
        print(' ')
        print('Atualizando DOTAÇÃO...')
        print(' ')

        try:
            url = f'https://extrator.sefaz.al.gov.br/DESPESAS/COMPARATIVO-DOTACOES/comparativo_dotacao_despesa_2025_siafe_gerado_em_{data_ontem}.xlsx'

            response = requests.get(url, verify=False)
            df = pd.read_excel(BytesIO(response.content))
        except: 
            url = f'https://extrator.sefaz.al.gov.br/DESPESAS/COMPARATIVO-DOTACOES/comparativo_dotacao_despesa_2025_siafe_gerado_em_{data_atual}.xlsx'
            response = requests.get(url, verify=False)
            df = pd.read_excel(BytesIO(response.content))
        
    except Exception as e:
        print('Erro na atualização da DOTAÇÃO:')
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

    df = df[['DATA', 'PODER', 'SIGLA_UO', 'UO', 'DESCRICAO_UO', 'UG', 'DESCRICAO_UG', 'FUNCAO',
        'DESCRICAO_FUNCAO', 'SUB_FUNCAO', 'DESCRICAO_SUB_FUNCAO', 'PROGRAMA',
        'PROGRAMA_DESCRICAO', 'PROJETO', 'PROJETO_DESCRICAO', 'PT',
        'PT_DESCRICAO', 'FONTE_MAE', 'DESCRICAO_FONTE_MAE', 'FONTE',
        'DESCRICAO_FONTE', 'NATUREZA1', 'DESCRICAO_NATUREZA1', 'NATUREZA2',
        'DESCRICAO_NATUREZA2', 'NATUREZA3', 'DESCRICAO_NATUREZA3', 'NATUREZA4',
        'DESCRICAO_NATUREZA4', 'NATUREZA5', 'DESCRICAO_NATUREZA5', 'NATUREZA6',
        'DESCRICAO_NATUREZA6', 'NATUREZA', 'DESCRICAO_NATUREZA', 'PO',
        'DESCRICAO_PO', 'CODIGO_EMENDA', 'TIT_EMENDA', 'AUTOR_EMENDA',
        'CODIGO_FAVORECIDO', 'NOME_FAVORECIDO', 'COD_CONTA_CONTABIL',
        'VALOR_DOTACAO_INICIAL', 'VALOR_CREDITO_ADICIONAL',
        'VALOR_REMANEJAMENTO', 'VALOR_DESTAQUE_PROVISAO_RECEBIDO',
        'VALOR_DESTAQUE_PROVISAO_CONCEDIDO', 'VALOR_CREDITO_INDISPONIVEL',
        'VALOR_ATUALIZADO', 'VALOR_ATUALIZADO_COM_DESTAQUE_PROVISAO',
        'VALOR_EMPENHADO', 'VALOR_LIQUIDADO', 'VALOR_PAGO']]

    colunas_str = ['DATA', 'PODER', 'UO', 'DESCRICAO_UO', 'UG', 'DESCRICAO_UG', 'FUNCAO',
        'DESCRICAO_FUNCAO', 'SUB_FUNCAO', 'DESCRICAO_SUB_FUNCAO', 'PROGRAMA',
        'PROGRAMA_DESCRICAO', 'PROJETO', 'PROJETO_DESCRICAO', 'PT',
        'PT_DESCRICAO', 'FONTE_MAE', 'DESCRICAO_FONTE_MAE', 'FONTE',
        'DESCRICAO_FONTE', 'NATUREZA1', 'DESCRICAO_NATUREZA1', 'NATUREZA2',
        'DESCRICAO_NATUREZA2', 'NATUREZA3', 'DESCRICAO_NATUREZA3', 'NATUREZA4',
        'DESCRICAO_NATUREZA4', 'NATUREZA5', 'DESCRICAO_NATUREZA5', 'NATUREZA6',
        'DESCRICAO_NATUREZA6', 'NATUREZA', 'DESCRICAO_NATUREZA', 'PO',
        'DESCRICAO_PO', 'CODIGO_EMENDA', 'TIT_EMENDA', 'AUTOR_EMENDA',
        'CODIGO_FAVORECIDO', 'NOME_FAVORECIDO', 'COD_CONTA_CONTABIL']

    for column in colunas_str:
        df[column] = df[column].astype(str)

    df = df.replace('nan', '')
    df['PT'] = df['PT'].str[:13]
    df['FONTE'] = df['FONTE'].str[:4]
    df['CREDITO_DISPONIVEL'] = df['VALOR_ATUALIZADO'] - (df["VALOR_EMPENHADO"] + df['VALOR_CREDITO_INDISPONIVEL'])

    print('Subindo no DRIVE...')

    parquet_buffer = BytesIO()
    df.to_parquet(parquet_buffer, index=False)
    parquet_buffer.seek(0)  
    update_base(parquet_buffer, 'sefaz_dotacao_ano_corrente.parquet')
    print('Atualização concluída com sucesso!')