import pandas as pd
import requests
import numpy as np
from io import BytesIO
from src.google_drive_utils import update_base

def funcao_anp_preco_combustivel():
# URL do arquivo para download
    url = 'https://www.gov.br/anp/pt-br/assuntos/precos-e-defesa-da-concorrencia/precos/precos-revenda-e-de-distribuicao-combustiveis/shlp/mensal/mensal-municipios-jan2022-2025.xlsx'

    try:
        response = requests.get(url)
        response.raise_for_status()
        df = pd.read_excel(BytesIO(response.content), header=16)
    except requests.exceptions.RequestException as e:
        print(f"Erro ao baixar o arquivo: {e}")
        df = pd.DataFrame()  # ou outra forma de lidar com o erro

    df = df.replace('-', np.nan)

    # Convert problematic columns to string     
    for col in df.columns:
        if df[col].dtype == 'datetime64[ns]':
            df[col] = df[col].astype(str)

    parquet_buffer = BytesIO()
    df.to_parquet(parquet_buffer, index=False)
    parquet_buffer.seek(0)  
    update_base(parquet_buffer, 'anp_preco_combustivel.parquet')
