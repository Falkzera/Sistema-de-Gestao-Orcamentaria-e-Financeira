import streamlit as st
import pandas as pd

from src.google_drive_utils import read_parquet_file_from_drive
from utils.confeccoes.formatar import (
    digitacao,
    titulo_dinamico,
    gerar_grafico_barra,
    gerar_grafico_linha,
    gerar_grafico_pizza,
    mostrar_tabela_pdf,
    formatar_valor_arredondado_sem_cifrao,
    maior_pico_producao,
    media_producao,
    ranking_producao,
    recorte_temporal_ano_passado
)

def montar_relatorio_anp_lgn(df):

    with st.container():  # CARREGAMENTO DATASET

        def load_data():
             
            df = read_parquet_file_from_drive('anp_lgn.parquet')

            return df
        
        df = load_data()

    with st.container(): # MANIPULAÇÃO DO DATASET

        df.loc[:, 'MÊS'] = df['MÊS'].replace({'JAN': 1, 'FEV': 2, 'MAR': 3, 'ABR': 4,'MAI': 5, 'JUN': 6, 'JUL': 7, 'AGO': 8, 'SET': 9, 'OUT': 10, 'NOV': 11, 'DEZ': 12}).infer_objects(copy=False)
        df.loc[:, 'DATA'] = pd.to_datetime(df['ANO'].astype(str) + '-' + df['MÊS'].astype(str) + '-01')
        df = df.drop(columns=['ANO', 'MÊS'])
        df = df[['DATA', 'GRANDE REGIÃO', 'UNIDADE DA FEDERAÇÃO', 'PRODUTO', 'PRODUÇÃO']]
        df.loc[:, 'PRODUÇÃO'] = df['PRODUÇÃO'].str.replace(',', '.').astype(float)

        df = df.groupby(['DATA', 'GRANDE REGIÃO', 'UNIDADE DA FEDERAÇÃO', 'PRODUTO'])[['PRODUÇÃO']].sum().reset_index()

    with st.container(): # TODOS OS DF NECESSÁRIOS: AL, NE, REGIÃO

        df_al = df[(df['UNIDADE DA FEDERAÇÃO'] == 'ALAGOAS')].copy()
        df_ne = df[(df['GRANDE REGIÃO'] == 'REGIÃO NORDESTE')].copy()
        df_regioes = df.groupby(['GRANDE REGIÃO', 'PRODUTO'])[['PRODUÇÃO']].sum().reset_index()
        produto = df['PRODUTO'].unique()[0]

    with st.container(): # CABEÇALHO 
        titulo_dinamico(f"# Produção de {produto.upper()} em Alagoas")
        titulo_dinamico(f"## Série histórica {df['DATA'].min().year} - {df['DATA'].max().year}")

    with st.container(): # Análise série histórica

        digitacao(f" \
            O gráfico apresenta a série histórica da produção de Líquido de Gás Natural ({produto.upper()}) em Alagoas, abrangendo o período de \
            {df['DATA'].min().year} a {df['DATA'].max().year}. A evolução ao longo do tempo revela tendências importantes \
            dessa produção. \
            Durante esse intervalo, a produção de {df_al['PRODUTO'].values[-1].upper()} atingiu seu pico máximo \
            em {maior_pico_producao(df_al)} m³. \
            Além disso, a produção apresentou uma média de {media_producao(df_al)} m³ ao longo dos anos. \
           ")
        
        with st.container(): # Gráfico!

            df_data_al = df_al.groupby('DATA')['PRODUÇÃO'].sum().reset_index()

            gerar_grafico_linha(
                x=[df_data_al['DATA']],
                y=[df_data_al['PRODUÇÃO']],
                titulo_pdf=f'Produção de {produto.upper()} em Alagoas - {df_al["DATA"].max().year}',
                nomes_series=[f'Produção de {produto.upper()}'],
                cores=['#095AA2'],  # Escolha a cor desejada
                empilhar=True  # Ativa o empilhamento
            )

        with st.container(): # RANKING
            digitacao(f" \
            Abaixo podemos observar o ranking de produção de {produto.upper()} por estado e por região. \
            ")

            df_ne['UNIDADE DA FEDERAÇÃO'] = df_ne['UNIDADE DA FEDERAÇÃO'].str.title()
            gerar_grafico_pizza(labels=df_ne['UNIDADE DA FEDERAÇÃO'], values=df_ne['PRODUÇÃO'], titulo_pdf=f'Produção de {produto.upper()} por Estados do Nordeste')
            mostrar_tabela_pdf(ranking_producao(df_ne), nome_tabela=f"Ranking de Produção de {produto.upper()} - Nordeste")

            df_regioes['GRANDE REGIÃO'] = df_regioes['GRANDE REGIÃO'].str.title()
            mostrar_tabela_pdf(ranking_producao(df_regioes), nome_tabela=f"Ranking de Produção de {produto.upper()} - Regiões")
            gerar_grafico_pizza(labels=df_regioes['GRANDE REGIÃO'], values=df_regioes['PRODUÇÃO'], titulo_pdf=f'Produção de {produto.upper()} por Região')

##########################################################

    with st.container(): # ANO

        df = recorte_temporal_ano_passado(df)
        df_al = recorte_temporal_ano_passado(df_al)
        df_ne = recorte_temporal_ano_passado(df_ne)
        df_regioes = df.groupby(['GRANDE REGIÃO', 'PRODUTO'])[['PRODUÇÃO']].sum().reset_index()

        titulo_dinamico(f"## Produção de LGN em {df['DATA'].max().year}")

        digitacao(f"O gráfico retrata uma série histórica de produção de {produto.upper()} em Alagoas, referente ao ano de {df_al['DATA'].max().year}. \
        Mostrando a evolução da produção ao longo do tempo.   \
        Podemos observar que, a produção de {df_al['PRODUTO'].values[-1].upper()}\
        atingiu o seu máximo {maior_pico_producao(df_al)} m³.")

        with st.container(): # Gráfico!

            df_data_al = df_al.groupby('DATA')['PRODUÇÃO'].sum().reset_index()

            # Gráfico
            gerar_grafico_barra(
                x=df_data_al['DATA'],
                y=df_data_al['PRODUÇÃO'],
                titulo_pdf=f'Produção de {produto.upper()} em Alagoas - {df_al["DATA"].max().year}',
                cores=['#095AA2'] * len(df_data_al),  # Defina a cor desejada
                texto_formatado=df_data_al['PRODUÇÃO'].apply(formatar_valor_arredondado_sem_cifrao),
            )

            digitacao(f" \
            Abaixo podemos observar o ranking de produção de {produto.upper()} por estado e por região. \
            ")

        with st.container(): # RANKING

            df_ne['UNIDADE DA FEDERAÇÃO'] = df_ne['UNIDADE DA FEDERAÇÃO'].str.title()
            gerar_grafico_pizza(labels=df_ne['UNIDADE DA FEDERAÇÃO'], values=df_ne['PRODUÇÃO'], titulo_pdf=f'Produção de {produto.upper()} por Estados do Nordeste')
            mostrar_tabela_pdf(ranking_producao(df_ne), nome_tabela=f"Ranking de Produção de {produto.upper()} - Nordeste")

            df_regioes['GRANDE REGIÃO'] = df_regioes['GRANDE REGIÃO'].str.title()
            mostrar_tabela_pdf(ranking_producao(df_regioes), nome_tabela=f"Ranking de Produção de {produto.upper()} - Regiões")
            gerar_grafico_pizza(labels=df_regioes['GRANDE REGIÃO'], values=df_regioes['PRODUÇÃO'], titulo_pdf=f'Produção de {produto.upper()} por Região')