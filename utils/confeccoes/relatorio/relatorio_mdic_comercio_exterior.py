import streamlit as st
import pandas as pd

from src.google_drive_utils import read_parquet_file_from_drive
from utils.confeccoes.formatar import (
    digitacao,
    titulo_dinamico,
    gerar_grafico_linha,
    mostrar_tabela_pdf,
    formatar_valor2,
    formatar_valor_usd,

)

with st.container(): # CORES
    color_tres = ['#095aa2', '#0e89f7', '#042b4d']
    degrade1 = ['#095aa2', '#085192', '#074882', '#063f71', '#053661', '#052d51', '#042441', '#031b31', '#021220', '#010910', '#000000']
    degrade2 = ['#095aa2', '#226bab', '#3a7bb5', '#538cbe', '#6b9cc7', '#84add1', '#9dbdda', '#b5cee3', '#cedeec', '#e6eff6', '#ffffff']
    fonte = '22px'
    CACHE_TTL = 60 * 60 * 24

def montar_relatorio_mdic_comercio_exterior(df):

    with st.container():  # CARREGAMENTO DATASET

        # comercio_exterior()
        df = read_parquet_file_from_drive('mdic_comercio_exterior.parquet')


    with st.container(): # SESSÃO 1.1 - SÉRIE HISTÓRICA DAS EXPORTAÇÕES E IMPORTAÇÕES
        titulo_dinamico(f' ## Série Histórica das Exportações e Importações: {df["DATA"].min().year} a {df["DATA"].max().year}')

        with st.container(): # SESSÃO 1.1 - TEXTO 1 MUNICIPIOS QUE MAIS EXPORTARAM E IMPORTARAM

           digitacao(f"O gráfico abaixo representa a série histórica das exportações e importações \
            no Estado de Alagoas, referente ao período de {df['DATA'].min().year} a {df['DATA'].max().year}. \
            Através dele, é possível visualizar a evolução das exportações e importações ao longo do tempo. \
            Podemos observar que durante todo o périodo, o volume de exportações foi de {formatar_valor_usd(df[df['CATEGORIA'] == 'EXPORTACAO']['VL_FOB'].sum())} \
            e o volume das importações foi de {formatar_valor_usd(df[df['CATEGORIA'] == 'IMPORTACAO']['VL_FOB'].sum())}. \
            Resultando em uma balança comercial {formatar_valor_usd(df[df['CATEGORIA'] == 'EXPORTACAO']['VL_FOB'].sum() - df[df['CATEGORIA'] == 'IMPORTACAO']['VL_FOB'].sum())}. \
            Durante esses périodos, os três Municípios que mais exportaram foram: {df[df['CATEGORIA'] == 'EXPORTACAO'].groupby('NO_MUN')['VL_FOB'].sum().nlargest(3).iloc[0:].idxmax().title()} , \
            seguido de {df[df['CATEGORIA'] == 'EXPORTACAO'].groupby('NO_MUN')['VL_FOB'].sum().nlargest(3).iloc[1:].idxmax().title()}   \
            e {df[df['CATEGORIA'] == 'EXPORTACAO'].groupby('NO_MUN')['VL_FOB'].sum().nlargest(3).iloc[2:].idxmax().title()}. \
            Representando nominalmente {formatar_valor_usd(df[df['CATEGORIA'] == 'EXPORTACAO'].groupby('NO_MUN')['VL_FOB'].sum().nlargest(3).iloc[0:].max())}, \
            {formatar_valor_usd(df[df['CATEGORIA'] == 'EXPORTACAO'].groupby('NO_MUN')['VL_FOB'].sum().nlargest(3).iloc[1:].max())} e \
            {formatar_valor_usd(df[df['CATEGORIA'] == 'EXPORTACAO'].groupby('NO_MUN')['VL_FOB'].sum().nlargest(3).iloc[2:].max())} respectivamente. \
            Já referente as importações temos: {df[df['CATEGORIA'] == 'IMPORTACAO'].groupby('NO_MUN')['VL_FOB'].sum().nlargest(3).iloc[0:].idxmax().title()} , \
            seguido de {df[df['CATEGORIA'] == 'IMPORTACAO'].groupby('NO_MUN')['VL_FOB'].sum().nlargest(3).iloc[1:].idxmax().title()}   \
            e {df[df['CATEGORIA'] == 'IMPORTACAO'].groupby('NO_MUN')['VL_FOB'].sum().nlargest(3).iloc[2:].idxmax().title()}. \
            Representando nominalmente {formatar_valor_usd(df[df['CATEGORIA'] == 'IMPORTACAO'].groupby('NO_MUN')['VL_FOB'].sum().nlargest(3).iloc[0:].max())}, \
            {formatar_valor_usd(df[df['CATEGORIA'] == 'IMPORTACAO'].groupby('NO_MUN')['VL_FOB'].sum().nlargest(3).iloc[1:].max())} e \
            {formatar_valor_usd(df[df['CATEGORIA'] == 'IMPORTACAO'].groupby('NO_MUN')['VL_FOB'].sum().nlargest(3).iloc[2:].max())} respectivamente.")


        with st.container(): # SESSÃO 1.1 - FORMATO TABULAR 1 - MUNICIPIOS QUE MAIS EXPORTARAM E IMPORTARAM

            with st.expander(f":orange[Tabela 1.1] - Top 10 Municípios que mais exportaram e importaram durante todo o período"):
                df_exportacao_graph = df[df['CATEGORIA'] == 'EXPORTACAO'].groupby('NO_MUN')['VL_FOB'].sum().nlargest(10)
                df_importacao_graph = df[df['CATEGORIA'] == 'IMPORTACAO'].groupby('NO_MUN')['VL_FOB'].sum().nlargest(10)
                df_exportacao = df[df['CATEGORIA'] == 'EXPORTACAO'].groupby('NO_MUN')['VL_FOB'].sum().nlargest(10)
                df_importacao = df[df['CATEGORIA'] == 'IMPORTACAO'].groupby('NO_MUN')['VL_FOB'].sum().nlargest(10)
                df_exportacao = df_exportacao.reset_index()
                df_importacao = df_importacao.reset_index()
                df_exportacao.columns = ['Município', 'Exportação']
                df_importacao.columns = ['Município', 'Importação']
                df_exportacao['Exportação'] = df_exportacao['Exportação'].apply(formatar_valor_usd)
                df_importacao['Importação'] = df_importacao['Importação'].apply(formatar_valor_usd)
                df_exportacao['Município'] = df_exportacao['Município'].str.title()
                df_importacao['Município'] = df_importacao['Município'].str.title()
                df_exportacao_importacao = pd.concat([df_exportacao, df_importacao], axis=1)


                mostrar_tabela_pdf(df_exportacao_importacao, nome_tabela="Top 10 Municípios que mais exportaram e importaram durante todo o período")

        with st.container(): # SESSÃO 1.1 - GRÁFICO 
                municipios_selecionados = df_exportacao_graph.index.tolist()


                df_export = df[df['CATEGORIA'] == 'EXPORTACAO'].groupby('DATA')[['VL_FOB']].sum().reset_index()
                df_import = df[df['CATEGORIA'] == 'IMPORTACAO'].groupby('DATA')[['VL_FOB']].sum().reset_index()

                gerar_grafico_linha(
                    x=[df_export['DATA'], df_import['DATA']],
                    y=[df_export['VL_FOB'], df_import['VL_FOB']],
                    nomes_series=["Exportação", "Importação"],
                    titulo_pdf=f"Exportação Vs. Importação",
                )

                x_series = []
                y_series = []
                nomes_series = []

                for municipio in municipios_selecionados:
                    df_graph = df[(df['NO_MUN'] == municipio) & (df['CATEGORIA'] == 'EXPORTACAO')].groupby('DATA')[['VL_FOB']].sum().reset_index()
                    x_series.append(df_graph['DATA'])
                    y_series.append(df_graph['VL_FOB'])
                    nomes_series.append(municipio)

                gerar_grafico_linha(
                    x=x_series,
                    y=y_series,
                    nomes_series=nomes_series,
                    titulo_pdf=f"Exportação por Municípios",
                )

                x_series = []
                y_series = []
                nomes_series = []

                for municipio in municipios_selecionados:
                    df_graph = df[(df['NO_MUN'] == municipio) & (df['CATEGORIA'] == 'IMPORTACAO')].groupby('DATA')[['VL_FOB']].sum().reset_index()
                    x_series.append(df_graph['DATA'])
                    y_series.append(df_graph['VL_FOB'])
                    nomes_series.append(municipio)

                gerar_grafico_linha(
                    x=x_series,
                    y=y_series,
                    nomes_series=nomes_series,
                    titulo_pdf=f"Importação por Municípios",
                )

        with st.container(): # SESSÃO 1.1 - TEXTO 2- PRODUTOS MAIS EXPORTADOS E IMPORTADOS

            digitacao(f"Ainda durante o mesmo período as categorias mais exportadas \
                        foram: {df[df['CATEGORIA'] == 'EXPORTACAO'].groupby('NO_SH2_POR')['VL_FOB'].sum().nlargest(3).iloc[0:].idxmax().lower()} , \
                        seguido de {df[df['CATEGORIA'] == 'EXPORTACAO'].groupby('NO_SH2_POR')['VL_FOB'].sum().nlargest(3).iloc[1:].idxmax().lower()} \
                        e {df[df['CATEGORIA'] == 'EXPORTACAO'].groupby('NO_SH2_POR')['VL_FOB'].sum().nlargest(3).iloc[2:].idxmax().lower()}. \
                        Já as categorias mais importadas foram: {df[df['CATEGORIA'] == 'IMPORTACAO'].groupby('NO_SH2_POR')['VL_FOB'].sum().nlargest(3).iloc[0:].idxmax().lower()} \
                        seguido de {df[df['CATEGORIA'] == 'IMPORTACAO'].groupby('NO_SH2_POR')['VL_FOB'].sum().nlargest(3).iloc[1:].idxmax().lower()} \
                        e {df[df['CATEGORIA'] == 'IMPORTACAO'].groupby('NO_SH2_POR')['VL_FOB'].sum().nlargest(3).iloc[2:].idxmax().lower()}.")
        

    with st.container(): # SESSÃO 1.2 - ANÁLISE 2024

        titulo_dinamico(f' ### Análise {df["DATA"].max().year}')
        df_ano_atual = df[df['DATA'].dt.year == df['DATA'].max().year]

        with st.container(): # SESSÃO 1.2 - TEXTO 2 - MUNICIPIOS QUE MAIS EXPORTARAM E IMPORTARAM

            mes_min = df_ano_atual['DATA'].min().month
            mes_max = df_ano_atual['DATA'].max().month
            ano_max = df_ano_atual['DATA'].max().year
            exportacoes_2024 = df_ano_atual[df_ano_atual['CATEGORIA'] == 'EXPORTACAO']['VL_FOB'].sum()
            importacoes_2024 = df_ano_atual[df_ano_atual['CATEGORIA'] == 'IMPORTACAO']['VL_FOB'].sum()
            balanca_comercial_2024 = exportacoes_2024 - importacoes_2024
            balanca_comercial_status = 'superavitária' if balanca_comercial_2024 > 0 else 'deficitária'

            
            digitacao(f"Compreendendo os meses de {mes_min}/{ano_max} até {mes_max}/{ano_max} \
            o volume total exportações foi de {formatar_valor_usd(exportacoes_2024)}, \
            já o volume total importações foi de {formatar_valor_usd(importacoes_2024)}. \
            Isso representa uma balança comercial {balanca_comercial_status} de {formatar_valor_usd(balanca_comercial_2024)}. \
            Durante esse período, os três Municípios que mais exportaram foram: {df_ano_atual[df_ano_atual['CATEGORIA'] == 'EXPORTACAO'].groupby('NO_MUN')['VL_FOB'].sum().nlargest(3).iloc[0:].idxmax().title()} , \
            seguido de {df_ano_atual[df_ano_atual['CATEGORIA'] == 'EXPORTACAO'].groupby('NO_MUN')['VL_FOB'].sum().nlargest(3).iloc[1:].idxmax().title()}   \
            e {df_ano_atual[df_ano_atual['CATEGORIA'] == 'EXPORTACAO'].groupby('NO_MUN')['VL_FOB'].sum().nlargest(3).iloc[2:].idxmax().title()}. \
            Representando nominalmente {formatar_valor_usd(df_ano_atual[df_ano_atual['CATEGORIA'] == 'EXPORTACAO'].groupby('NO_MUN')['VL_FOB'].sum().nlargest(3).iloc[0:].max())}, \
            {formatar_valor_usd(df_ano_atual[df_ano_atual['CATEGORIA'] == 'EXPORTACAO'].groupby('NO_MUN')['VL_FOB'].sum().nlargest(3).iloc[1:].max())} e \
            {formatar_valor_usd(df_ano_atual[df_ano_atual['CATEGORIA'] == 'EXPORTACAO'].groupby('NO_MUN')['VL_FOB'].sum().nlargest(3).iloc[2:].max())} respectivamente. \
            Já referente as importações temos: {df_ano_atual[df_ano_atual['CATEGORIA'] == 'IMPORTACAO'].groupby('NO_MUN')['VL_FOB'].sum().nlargest(3).iloc[0:].idxmax().title()} , \
            seguido de {df_ano_atual[df_ano_atual['CATEGORIA'] == 'IMPORTACAO'].groupby('NO_MUN')['VL_FOB'].sum().nlargest(3).iloc[1:].idxmax().title()}   \
            e {df_ano_atual[df_ano_atual['CATEGORIA'] == 'IMPORTACAO'].groupby('NO_MUN')['VL_FOB'].sum().nlargest(3).iloc[2:].idxmax().title()}. \
            Representando nominalmente {formatar_valor_usd(df_ano_atual[df_ano_atual['CATEGORIA'] == 'IMPORTACAO'].groupby('NO_MUN')['VL_FOB'].sum().nlargest(3).iloc[0:].max())}, \
            {formatar_valor_usd(df_ano_atual[df_ano_atual['CATEGORIA'] == 'IMPORTACAO'].groupby('NO_MUN')['VL_FOB'].sum().nlargest(3).iloc[1:].max())} \
            {formatar_valor_usd(df_ano_atual[df_ano_atual['CATEGORIA'] == 'IMPORTACAO'].groupby('NO_MUN')['VL_FOB'].sum().nlargest(3).iloc[2:].max())} respectivamente. \
            ")

        with st.container(): # SESSÃO 1.2 - FORMATO TABULAR 2 - MUNICIPIOS QUE MAIS EXPORTARAM E IMPORTARAM

            with st.expander(f":orange[Tabela 1.2] - Top 10 Municípios que mais exportaram e importaram em {ano_max}"):
                # Cálculo para Exportação
                df_exportacao_graph = df_ano_atual[df_ano_atual['CATEGORIA'] == 'EXPORTACAO'].groupby('NO_MUN')['VL_FOB'].sum().nlargest(10)
                df_exportacao = df_ano_atual[df_ano_atual['CATEGORIA'] == 'EXPORTACAO'].groupby('NO_MUN')['VL_FOB'].sum().nlargest(10)
                total_exportacao = df_exportacao.sum()
                df_exportacao = df_exportacao.reset_index()
                df_exportacao.columns = ['Município', 'Exportação']
                df_exportacao['Município'] = df_exportacao['Município'].str.title()
                df_exportacao['% Participação'] = (df_exportacao['Exportação'] / total_exportacao * 100).round(2)
                df_exportacao['Exportação'] =  df_exportacao['Exportação'].apply(formatar_valor_usd)
                df_exportacao['% Participação'] = df_exportacao['% Participação'].apply(formatar_valor2)
                # df_exportacao = df_exportacao.set_index('Município')

                # Cálculo para Importação
                df_importacao_graph = df_ano_atual[df_ano_atual['CATEGORIA'] == 'IMPORTACAO'].groupby('NO_MUN')['VL_FOB'].sum().nlargest(10)
                df_importacao = df_ano_atual[df_ano_atual['CATEGORIA'] == 'IMPORTACAO'].groupby('NO_MUN')['VL_FOB'].sum().nlargest(10)
                total_importacao = df_importacao.sum() 
                df_importacao = df_importacao.reset_index()
                df_importacao.columns = ['Município', 'Importação']
                df_importacao['Município'] = df_importacao['Município'].str.title()
                df_importacao['% Participação'] = (df_importacao['Importação'] / total_importacao * 100).round(2)
                df_importacao['Importação'] =  df_importacao['Importação'].apply(formatar_valor_usd)
                df_importacao['% Participação'] = df_importacao['% Participação'].apply(formatar_valor2)
    
                # df_importacao = df_importacao.set_index('Município')
                df_exportacao_importacao = pd.concat([df_exportacao, df_importacao], axis=1)

                mostrar_tabela_pdf(df_exportacao_importacao, nome_tabela="Top 10 Municípios que mais exportaram e importaram em 2024")


        with st.container(): # SESSÃO 1.2 - TEXTO 3 - PRODUTOS MAIS EXPORTADOS E IMPORTADOS

            digitacao(f"Ainda durante o mesmo período as categorias mais exportadas \
            foram: {df_ano_atual[df_ano_atual['CATEGORIA'] == 'EXPORTACAO'].groupby('NO_SH2_POR')['VL_FOB'].sum().nlargest(3).iloc[0:].idxmax().lower()} , \
            seguido de {df_ano_atual[df_ano_atual['CATEGORIA'] == 'EXPORTACAO'].groupby('NO_SH2_POR')['VL_FOB'].sum().nlargest(3).iloc[1:].idxmax().lower()} \
            e {df_ano_atual[df_ano_atual['CATEGORIA'] == 'EXPORTACAO'].groupby('NO_SH2_POR')['VL_FOB'].sum().nlargest(3).iloc[2:].idxmax().lower()}. \
            Já as categorias mais importadas foram: {df_ano_atual[df_ano_atual['CATEGORIA'] == 'IMPORTACAO'].groupby('NO_SH2_POR')['VL_FOB'].sum().nlargest(3).iloc[0:].idxmax().lower()}</b> \
            seguido de {df_ano_atual[df_ano_atual['CATEGORIA'] == 'IMPORTACAO'].groupby('NO_SH2_POR')['VL_FOB'].sum().nlargest(3).iloc[1:].idxmax().lower()} \
            e {df_ano_atual[df_ano_atual['CATEGORIA'] == 'IMPORTACAO'].groupby('NO_SH2_POR')['VL_FOB'].sum().nlargest(3).iloc[2:].idxmax().lower()}. \
            ")

    with st.container(): # SESSÃO 1.3 - ANÁLISE TRIMESTRAL

        titulo_dinamico(f'### Análise Trimestral {df["DATA"].max().year}')

        with st.container(): # SESSÃO 1.3 - METRÍCAS (DEFININDO TRIMESTRE ANTERIOR)
        
            mes_atual_do_ano_atual = df[df['DATA'].dt.year == ano_max]['DATA'].dt.month.max() # Último mês do ano atual

            # Trimestre Atual!
            def selecionar_trimestre_atual(mes_atual_do_ano_atual, df=df, df_tri_ano_atual=df_ano_atual):
                if 1 <= mes_atual_do_ano_atual <= 3:
                    trimestre_atual = 'Primeiro'
                    df_tri_serie = df[df['DATA'].dt.month <= 3]
                    df_tri_ano_atual = df_tri_ano_atual[df_tri_ano_atual['DATA'].dt.month <= 3]
                elif 4 <= mes_atual_do_ano_atual <= 6:
                    trimestre_atual = 'Segundo'
                    df_tri_serie = df[(df['DATA'].dt.month > 3) & (df['DATA'].dt.month <= 6)]
                    df_tri_ano_atual = df_tri_ano_atual[(df_tri_ano_atual['DATA'].dt.month > 3) & (df_tri_ano_atual['DATA'].dt.month <= 6)]
                elif 7 <= mes_atual_do_ano_atual <= 9:
                    trimestre_atual = 'Terceiro'
                    df_tri_serie = df[(df['DATA'].dt.month > 6) & (df['DATA'].dt.month <= 9)]
                    df_tri_ano_atual = df_tri_ano_atual[(df_tri_ano_atual['DATA'].dt.month > 6) & (df_tri_ano_atual['DATA'].dt.month <= 9)]
                else:
                    trimestre_atual = 'Quarto'
                    df_tri_serie = df[(df['DATA'].dt.month > 9) & (df['DATA'].dt.month <= 12)]
                    df_tri_ano_atual = df_tri_ano_atual[(df_tri_ano_atual['DATA'].dt.month > 9) & (df_tri_ano_atual['DATA'].dt.month <= 12)]
                return trimestre_atual, df_tri_serie, df_tri_ano_atual
            
            trimestre_atual, df_tri_serie, df_tri_ano_atual = selecionar_trimestre_atual(mes_atual_do_ano_atual)

        with st.container(): # SESSÃO 1.3 - TEXTO 4 - MUNICIPIOS QUE MAIS EXPORTARAM E IMPORTARAM

            exportacoes_tri_atual = df_tri_ano_atual[df_tri_ano_atual['CATEGORIA'] == 'EXPORTACAO']['VL_FOB'].sum()
            importacoes_tri_atual = df_tri_ano_atual[df_tri_ano_atual['CATEGORIA'] == 'IMPORTACAO']['VL_FOB'].sum()
            balanca_comercial_tri_atual = exportacoes_tri_atual - importacoes_tri_atual
            balanca_comercial_tri_atual_status = 'superavitária' if balanca_comercial_tri_atual > 0 else 'deficitária'

            digitacao(f"Realizando o recorte para o {trimestre_atual.lower()} trimestre de {ano_max}, \
            o volume total exportações foi de {formatar_valor_usd(exportacoes_tri_atual)}, \
            já o volume total de importações foi de {formatar_valor_usd(importacoes_tri_atual)}. \
            Isso representa uma balança comercial {balanca_comercial_tri_atual_status} de {formatar_valor_usd(balanca_comercial_tri_atual)}. \
            Durante esse período os três Municípios que mais exportaram foram: {df_tri_ano_atual[df_tri_ano_atual['CATEGORIA'] == 'EXPORTACAO'].groupby('NO_MUN')['VL_FOB'].sum().nlargest(3).iloc[0:].idxmax().title()} , \
            seguido de {df_tri_ano_atual[df_tri_ano_atual['CATEGORIA'] == 'EXPORTACAO'].groupby('NO_MUN')['VL_FOB'].sum().nlargest(3).iloc[1:].idxmax().title()}   \
            e {df_tri_ano_atual[df_tri_ano_atual['CATEGORIA'] == 'EXPORTACAO'].groupby('NO_MUN')['VL_FOB'].sum().nlargest(3).iloc[2:].idxmax().title()}. \
            Representando nominalmente {formatar_valor_usd(df_tri_ano_atual[df_tri_ano_atual['CATEGORIA'] == 'EXPORTACAO'].groupby('NO_MUN')['VL_FOB'].sum().nlargest(3).iloc[0:].max())}, \
            {formatar_valor_usd(df_tri_ano_atual[df_tri_ano_atual['CATEGORIA'] == 'EXPORTACAO'].groupby('NO_MUN')['VL_FOB'].sum().nlargest(3).iloc[1:].max())} e \
            {formatar_valor_usd(df_tri_ano_atual[df_tri_ano_atual['CATEGORIA'] == 'EXPORTACAO'].groupby('NO_MUN')['VL_FOB'].sum().nlargest(3).iloc[2:].max())} respectivamente. \
            ")
        
        with st.container(): # SESSÃO 1.3 - FORMATO TABULAR 3 - MUNICIPIOS QUE MAIS EXPORTARAM E IMPORTARAM

            with st.expander(f":orange[Tabela 1.3] - Top 10 Municípios que mais exportaram e importaram no {trimestre_atual.lower()} trimestre de {ano_max}"):
                df_exportacao_graph = df_tri_ano_atual[df_tri_ano_atual['CATEGORIA'] == 'EXPORTACAO'].groupby('NO_MUN')['VL_FOB'].sum().nlargest(10)
                df_exportacao = df_tri_ano_atual[df_tri_ano_atual['CATEGORIA'] == 'EXPORTACAO'].groupby('NO_MUN')['VL_FOB'].sum().nlargest(10)
                df_importacao = df_tri_ano_atual[df_tri_ano_atual['CATEGORIA'] == 'IMPORTACAO'].groupby('NO_MUN')['VL_FOB'].sum().nlargest(10)
                df_exportacao = df_exportacao.reset_index()
                df_importacao = df_importacao.reset_index()
                df_exportacao.columns = ['Município', 'Exportação']
                df_importacao.columns = ['Município', 'Importação']
                df_exportacao['Exportação'] = df_exportacao['Exportação'].apply(formatar_valor_usd)
                df_importacao['Importação'] = df_importacao['Importação'].apply(formatar_valor_usd)
                df_importacao['Município'] = df_importacao['Município'].str.title()
                df_exportacao['Município'] = df_exportacao['Município'].str.title()
                # df_exportacao = df_exportacao.set_index('Município')
                # df_importacao = df_importacao.set_index('Município')

                df_exportacao_importacao = pd.concat([df_exportacao, df_importacao], axis=1)
                mostrar_tabela_pdf(df_exportacao_importacao, nome_tabela="Top 10 Municípios que mais exportaram e importaram no 1º trimestre de 2024")

        with st.container(): # SESSÃO 1.3 - TEXTO 5 - PRODUTOS MAIS EXPORTADOS E IMPORTADOS

            digitacao(f"Ainda durante o mesmo período as categorias mais exportadas \
            foram: {df_tri_ano_atual[df_tri_ano_atual['CATEGORIA'] == 'EXPORTACAO'].groupby('NO_SH2_POR')['VL_FOB'].sum().nlargest(3).iloc[0:].idxmax().lower()} , \
            seguido de {df_tri_ano_atual[df_tri_ano_atual['CATEGORIA'] == 'EXPORTACAO'].groupby('NO_SH2_POR')['VL_FOB'].sum().nlargest(3).iloc[1:].idxmax().lower()} \
            e {df_tri_ano_atual[df_tri_ano_atual['CATEGORIA'] == 'EXPORTACAO'].groupby('NO_SH2_POR')['VL_FOB'].sum().nlargest(3).iloc[2:].idxmax().lower()}. \
            Já as categorias mais importadas foram: {df_tri_ano_atual[df_tri_ano_atual['CATEGORIA'] == 'IMPORTACAO'].groupby('NO_SH2_POR')['VL_FOB'].sum().nlargest(3).iloc[0:].idxmax().lower()}</b> \
            seguido de {df_tri_ano_atual[df_tri_ano_atual['CATEGORIA'] == 'IMPORTACAO'].groupby('NO_SH2_POR')['VL_FOB'].sum().nlargest(3).iloc[1:].idxmax().lower()}</b> \
            e {df_tri_ano_atual[df_tri_ano_atual['CATEGORIA'] == 'IMPORTACAO'].groupby('NO_SH2_POR')['VL_FOB'].sum().nlargest(3).iloc[2:].idxmax().lower()}</b>. \
            ")