import pandas as pd
import requests
from io import BytesIO
from src.google_drive_utils import update_base

def funcao_mdic_comercio_exterior():
        
    def consulta_comex(flow, ano_inicio, ano_fim):
        url = "https://api-comexstat.mdic.gov.br/cities?language=pt"
        payload = {
            "flow": flow,
            "monthDetail": True,
            "period": {
                "from": f"{ano_inicio}-01",
                "to": f"{ano_fim}-12"
            },
            "filters": [
                {
                    "filter": "state",
                    "values": [27]
                }
            ],
            "details": ["city", "country", "chapter", "economicBlock"],
            "metrics": ["metricFOB"]
        }

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        response = requests.post(url, json=payload, headers=headers, verify=False)

        if response.status_code == 200:
            data = response.json()
            if data.get("data") and data["data"].get("list"):
                df = pd.DataFrame(data["data"]["list"])
                df["flow"] = flow
                return df
        return pd.DataFrame()

    df_export = consulta_comex('export', 1997, 2025)
    df_import = consulta_comex('import', 1997, 2025)
    df = pd.concat([df_import, df_export], ignore_index=True)

    df['DATA'] = pd.to_datetime(df['year'].astype(str) + '-' + df['monthNumber'].astype(str) + '-01')

    df.rename(columns={
        'noMunMinsgUf': 'NO_MUN',
        'country': 'NO_PAIS',
        'chapter': 'NO_SH2_POR',
        'metricFOB': 'VL_FOB',
        'flow': 'CATEGORIA'
    }, inplace=True)

    df.drop(columns=['year', 'monthNumber', 'chapterCode'], inplace=True)
    df['CATEGORIA'] = df['CATEGORIA'].replace({'export': 'EXPORTACAO', 'import': 'IMPORTACAO'})
    df['NO_MUN'] = df['NO_MUN'].str.replace(' - AL', '', regex=False)
    df['VL_FOB'] = df['VL_FOB'].astype(float).round(2)

    parquet_buffer = BytesIO()
    df.to_parquet(parquet_buffer, index=False)
    parquet_buffer.seek(0)  
    update_base(parquet_buffer, 'mdic_comercio_exterior.parquet')