import requests
import pandas as pd
from io import BytesIO
from src.google_drive_utils import update_base

def funcao_anp_producao_combustivel():
        
    def processar_e_salvar_csv(url, nome_arquivo_parquet):
        try:
            response = requests.get(url)
            response.raise_for_status()
            df = pd.read_csv(BytesIO(response.content), sep=';', encoding='utf-8') 
        except requests.exceptions.RequestException as e:
            print(f"Erro ao baixar o arquivo {nome_arquivo_parquet}: {e}")
            df = pd.DataFrame() 
        
        for col in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                df[col] = df[col].astype(str)

        parquet_buffer = BytesIO()
        df.to_parquet(parquet_buffer, index=False)
        parquet_buffer.seek(0)

        update_base(parquet_buffer, nome_arquivo_parquet)

    url_petroleo = 'https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos/arquivos/ppgn-el/producao-petroleo-m3-1997-2025.csv'
    url_lgn = 'https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos/arquivos/ppgn-el/producao-lgn-m3-1997-2025.csv'
    url_gn = 'https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos/arquivos/ppgn-el/producao-gas-natural-1000m3-1997-2025.csv'
    url_etanol = 'https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos/arquivos/arquivos-producao-de-biocombustiveis/producao-etanol-anidro-hidratado-m3-2012-2025.csv'

    processar_e_salvar_csv(url_petroleo, 'anp_petroleo.parquet')
    processar_e_salvar_csv(url_lgn, 'anp_lgn.parquet')
    processar_e_salvar_csv(url_gn, 'anp_gn.parquet')
    processar_e_salvar_csv(url_etanol, 'anp_etanol.parquet')