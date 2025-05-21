import pandas as pd
import sidrapy
from io import BytesIO
from src.google_drive_utils import update_base

def funcao_ibge_abate_animais():

    lista_nordeste = '21', '22', '23', '24', '25', '26', '27', '28', '29'
    ibge_territorial_code = ','.join(lista_nordeste)
    data = sidrapy.get_table(table_code='1092', # Pesquisa trimestral do abate de animais
                                territorial_level='3', # Selecionado por unidade de federação
                                ibge_territorial_code=ibge_territorial_code, # Unidades do nordeste
                                variable='284', # Animais abatidos (cabeças)
                                period='all', # Todos os períodos        
                            )

    data.columns = data.iloc[0]
    df = data.iloc[1:, [6,8,4,10]]
    df['ANO'] = df['Trimestre'].str.extract(r'(\d{4})')
    df['Trimestre'] = df['Trimestre'].str.extract(r'(\d{1})')
    df['DATA'] = df['ANO'] + '-' + df['Trimestre']
    df['DATA'] = pd.to_datetime(df['DATA'])
    df = df.drop(columns=['ANO', 'Trimestre'])
    df['Valor'] = df['Valor'].replace('X', pd.NA)
    df['Valor'] = df['Valor'].replace('...', pd.NA)
    df['Valor'] = df['Valor'].replace(pd.NA, float('nan')).astype(float)
    df = df.rename(columns={'Unidade da Federação': 'UF', 'Valor': 'VALOR'})
    df = df[['DATA', 'UF', 'VALOR']]

    parquet_buffer = BytesIO()
    df.to_parquet(parquet_buffer, index=False)
    parquet_buffer.seek(0)  
    update_base(parquet_buffer, 'ibge_abate_animais.parquet')