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

def funcao_sefaz_dotacao_completo():
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


    df_drive = read_parquet_file_from_drive('sefaz_dotacao_completo.parquet')
    df_drive['DATA'] = pd.to_datetime(df_drive['DATA'], format='%Y-%m')
    df_drive['ANO'] = df_drive['DATA'].dt.year
    df_drive = df_drive[df_drive['ANO'] != 2025]
    df_drive = df_drive.drop(columns=['ANO'])
    sigla = read_parquet_file_from_drive('sigla.parquet')
    sigla['UO'] = sigla['UO'].astype('object')
    print('Antes da adição da coluna, o df tinha:', df.shape)
    sigla_dict = sigla.set_index('UO')['SIGLA_UO'].to_dict()
    df['SIGLA_UO'] = df['UO'].map(sigla_dict)
    print('Depois da adição da coluna, o df tem:', df.shape)
    df['DATA'] = df['ANO'].astype(str) + '-' + df['MES'].astype(str)
    df['DATA'] = pd.to_datetime(df['DATA'], format='%Y-%m')
    df.drop(['ANO', 'MES'], axis=1, inplace=True)

    df = df[['DATA','PODER', 'UO', 'SIGLA_UO', 'DESCRICAO_UO', 'UG', 'DESCRICAO_UG', 'FUNCAO',
        'DESCRICAO_FUNCAO', 'SUB_FUNCAO', 'DESCRICAO_SUB_FUNCAO', 'PROGRAMA',
        'PROGRAMA_DESCRICAO', 'PROJETO', 'PROJETO_DESCRICAO', 'PT',
        'PT_DESCRICAO', 'FONTE_MAE', 'DESCRICAO_FONTE_MAE', 'FONTE',
        'DESCRICAO_FONTE', 'NATUREZA1', 'DESCRICAO_NATUREZA1', 'NATUREZA2',
        'DESCRICAO_NATUREZA2', 'NATUREZA3', 'DESCRICAO_NATUREZA3', 'NATUREZA4',
        'DESCRICAO_NATUREZA4', 'NATUREZA5', 'DESCRICAO_NATUREZA5', 'NATUREZA6',
        'DESCRICAO_NATUREZA6', 'NATUREZA', 'DESCRICAO_NATUREZA',
        'VALOR_EMPENHADO', 'VALOR_LIQUIDADO', 'VALOR_PAGO']]

    df['SIGLA_UO'] = df['SIGLA_UO'].fillna(df['DESCRICAO_UO'])
    df['PROJETO_DESCRICAO'] = df['PROJETO_DESCRICAO'].fillna('NÃO INFORMADO')
    df['PT_DESCRICAO'] = df['PT_DESCRICAO'].fillna('NÃO INFORMADO')
    df['DESCRICAO_FONTE'] = df['DESCRICAO_FONTE'].fillna('NÃO INFORMADO')
    df['DESCRICAO_NATUREZA5'] = df['DESCRICAO_NATUREZA5'].fillna('NÃO INFORMADO')

    convertendo_obj = ['PODER', 'UO', 'SIGLA_UO', 'DESCRICAO_UO', 'UG', 'DESCRICAO_UG', 'FUNCAO',
        'DESCRICAO_FUNCAO', 'SUB_FUNCAO', 'DESCRICAO_SUB_FUNCAO', 'PROGRAMA',
        'PROGRAMA_DESCRICAO', 'PROJETO', 'PROJETO_DESCRICAO', 'PT',
        'PT_DESCRICAO', 'FONTE_MAE', 'DESCRICAO_FONTE_MAE', 'FONTE',
        'DESCRICAO_FONTE', 'NATUREZA1', 'DESCRICAO_NATUREZA1', 'NATUREZA2',
        'DESCRICAO_NATUREZA2', 'NATUREZA3', 'DESCRICAO_NATUREZA3', 'NATUREZA4',
        'DESCRICAO_NATUREZA4', 'NATUREZA5', 'DESCRICAO_NATUREZA5', 'NATUREZA6',
        'DESCRICAO_NATUREZA6', 'NATUREZA', 'DESCRICAO_NATUREZA']
    for column in convertendo_obj:
        df[column] = df[column].astype('object')
        convertendo_obj = ['VALOR_EMPENHADO', 'VALOR_LIQUIDADO', 'VALOR_PAGO']
    convertendo_obj = ['VALOR_EMPENHADO', 'VALOR_LIQUIDADO', 'VALOR_PAGO']
    for column in convertendo_obj:
        df[column] = df[column].astype(str).str.replace(',', '.').astype(float)
    # ----------------------------------------------- #

    df['DESCRICAO_UO'] = df['DESCRICAO_UO'].astype(str)
    df['DESCRICAO_UG'] = df['DESCRICAO_UG'].astype(str)
    df['DESCRICAO_UG'] = df['DESCRICAO_UG'].str.upper().str.strip().apply(lambda x: unidecode(x))
    df['DESCRICAO_UG'] = df['DESCRICAO_UG'].str.upper().str.strip()

    def unificar_descricao(df):

        maiores_descricoes_ug = df.groupby('UG')['DESCRICAO_UG'].apply(lambda x: x.loc[x.str.len().idxmax()])
        maiores_descricoes_uo = df.groupby('UO')['DESCRICAO_UO'].apply(lambda x: x.loc[x.str.len().idxmax()])
        
        df['DESCRICAO_UG'] = df['UG'].map(maiores_descricoes_ug)
        df['DESCRICAO_UO'] = df['UO'].map(maiores_descricoes_uo)
        
        return df

    df = unificar_descricao(df)

    df_final = pd.concat([df, df_drive], ignore_index=True)

    print('Subindo no DRIVE...')

    parquet_buffer = BytesIO()
    df_final.to_parquet(parquet_buffer, index=False)
    parquet_buffer.seek(0)  
    update_base(parquet_buffer, 'sefaz_dotacao_completo.parquet')
    print('Atualização concluída com sucesso!')