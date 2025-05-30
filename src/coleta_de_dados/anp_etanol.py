import requests
import pandas as pd
from io import BytesIO
from src.google_drive_utils import update_base

def funcao_anp_etanol():

    url = 'https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos/arquivos/arquivos-producao-de-biocombustiveis/producao-etanol-anidro-hidratado-m3-2012-2025.csv'

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        df = pd.read_csv(BytesIO(response.content), delimiter=';')
        parquet_buffer = BytesIO()
        df.to_parquet(parquet_buffer, index=False)
        parquet_buffer.seek(0)  
        update_base(parquet_buffer, 'anp_etanol.parquet')
    except requests.exceptions.RequestException as e:
        print(f"HTTP request failed: {e}")
    except pd.errors.ParserError as e:
        print(f"CSV parsing failed: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")