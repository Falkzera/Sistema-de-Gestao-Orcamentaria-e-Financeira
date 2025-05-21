import streamlit as st
import pandas as pd
import numpy as np

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
    menor_pico_producao,
    ranking_producao,
    recorte_temporal_ano_passado,
    formatar_valor,
    formatar_valor2,
    formatar_valor_sem_cifrao,
    por_extenso,

)

with st.container(): # CORES
    color_tres = ['#095aa2', '#0e89f7', '#042b4d']
    degrade1 = ['#095aa2', '#085192', '#074882', '#063f71', '#053661', '#052d51', '#042441', '#031b31', '#021220', '#010910', '#000000']
    degrade2 = ['#095aa2', '#226bab', '#3a7bb5', '#538cbe', '#6b9cc7', '#84add1', '#9dbdda', '#b5cee3', '#cedeec', '#e6eff6', '#ffffff']
    fonte = '22px'
    CACHE_TTL = 60 * 60 * 24

def montar_relatorio_ibge_leite_industrializado(df):
    
    with st.container(): # PREPARAÇÃO DOS DADOS - LEITE CRU INDUSTRIALIZADO
        
        # leite()
        df = read_parquet_file_from_drive('ibge_leite_industrializado.parquet')

    ano_max = df['DATA'].dt.year.max()

    with st.container(): 
        titulo_dinamico('## Leite Cru Industrializado')
        # st.info(f"Fonte: IBGE - Coletado em: {last_collected}")

        with st.container():

            mes_atual_do_ano_atual = df[df['DATA'].dt.year == ano_max]['DATA'].dt.month.max() 

            def selecionar_trimestre_atual(mes_atual_do_ano_atual, df=df):
                if mes_atual_do_ano_atual == 1:
                    trimestre_atual = 'Primeiro'
                    df_tri_estado = df[df['DATA'].dt.month == 1]
                elif mes_atual_do_ano_atual == 2:
                    trimestre_atual = 'Segundo'
                    df_tri_estado = df[df['DATA'].dt.month == 2]
                elif mes_atual_do_ano_atual == 3:
                    trimestre_atual = 'Terceiro'
                    df_tri_estado = df[df['DATA'].dt.month == 3]
                else:
                    trimestre_atual = 'Quarto'
                    df_tri_estado = df[df['DATA'].dt.month == 4]
                return trimestre_atual, df_tri_estado
            
            trimestre_atual, df_tri_estado = selecionar_trimestre_atual(mes_atual_do_ano_atual)
            df_alagoas = df[df['UF'] == 'Alagoas']
            df_alagoas_anual_media = df_alagoas.groupby([df_alagoas['DATA'].dt.year])['VALOR'].mean().reset_index()
            df_alagoas_anual = df_alagoas.groupby([df_alagoas['DATA'].dt.year])['VALOR'].sum().reset_index()
            ranking_estado_serie = df.groupby(['UF'])[['VALOR']].sum().sort_values(by='VALOR', ascending=False).reset_index()
            ranking_estado_serie.index += 1

        with st.container():

            digitacao(f" \
                        Abaixo é possível observar graficamente a série histórica trimestral do Estado de Alagoas, \
                        referente a quantidade de leite cru industrializado ao longo dos anos, que varia de \
                        {df['DATA'].dt.year.min()} até o {trimestre_atual.lower()} trimestre de {df['DATA'].dt.year.max()}. \
                        ")
        
        with st.container(): 

            # Preparar os dados
            x = [df_alagoas['DATA'], df_alagoas_anual_media['DATA']]
            y = [df_alagoas['VALOR'], df_alagoas_anual_media['VALOR']]
            nomes_series = ['Trimestral', 'Média']
            cores = [degrade1[0], degrade1[1]]  # assumindo que degrade1 seja uma lista com pelo menos duas cores

            # Gerar gráfico com a função
            gerar_grafico_linha(
                x=x,
                y=y,
                titulo_pdf=f'Série histórica de produção de leite cru industrializado em Alagoas',
                nomes_series=nomes_series,
                cores=cores,
            )

        with st.container(): 

            trimestre_maior_valor = (df_alagoas.loc[df_alagoas['VALOR'].idxmax()])

            digitacao(f" \
                Podemos visualizar que até a presente análise, \
                o maior trimestre de volume de leite cru industrializado ocorreu no {trimestre_maior_valor['DATA'].month}° trimestre do ano de {df_alagoas.loc[df_alagoas['VALOR'].idxmax(), 'DATA'].year}, \
                com um total de {formatar_valor_sem_cifrao(df_alagoas['VALOR'].max())} litros. \
                Já em relação ao máximo anual, o estado registrou um total de {formatar_valor_sem_cifrao(df_alagoas_anual['VALOR'].max())} litros ocorridos no ano de {df_alagoas_anual.loc[df_alagoas_anual['VALOR'].idxmax(), 'DATA']}. \
                E referente a toda série histórica Alagoas registrou um total de {formatar_valor_sem_cifrao(df_alagoas['VALOR'].sum())} litros, isso garantiu que Alagoas ocupasse \
                a {ranking_estado_serie.index[ranking_estado_serie['UF'] == 'Alagoas'].values[0]}° posição no ranking de produção de leite industrializado do Nordeste. \
                Ficando atraś dos seguintes estados: {ranking_estado_serie['UF'].values[0]} (com {formatar_valor_sem_cifrao(ranking_estado_serie['VALOR'].values[0])}), \
                {ranking_estado_serie['UF'].values[1]} (com {formatar_valor_sem_cifrao(ranking_estado_serie['VALOR'].values[1])}), {ranking_estado_serie['UF'].values[2]} (com {formatar_valor_sem_cifrao(ranking_estado_serie['VALOR'].values[2])}) e \
                {ranking_estado_serie['UF'].values[3]} (com {formatar_valor_sem_cifrao(ranking_estado_serie['VALOR'].values[3])}). \
                O demais ranking pode ser visualizado na tabela abaixo. \
                ")

        with st.container(): 

            ranking_estado_serie['VALOR'] = ranking_estado_serie['VALOR'].apply(lambda x: f'{x:.0f}')
            ranking_estado_serie['VALOR'] = ranking_estado_serie['VALOR'].apply(lambda x: f'{int(x):,}'.replace(',', '.'))
            mostrar_tabela_pdf(ranking_estado_serie, nome_tabela='Ranking de produção de leite cru industrializado por Estado')


    with st.container(): 
        st.write('---')
        titulo_dinamico(f'Análise {ano_max} - Produção de leite cru industrializado')

        with st.container(): 

            mes_atual_do_ano_atual = df[df['DATA'].dt.year == ano_max]['DATA'].dt.month.max() 

            def selecionar_trimestre_atual(mes_atual_do_ano_atual, df=df):
                if mes_atual_do_ano_atual == 1:
                    trimestre_atual = 'Primeiro'
                    df_tri_estado = df[df['DATA'].dt.month == 1]
                elif mes_atual_do_ano_atual == 2:
                    trimestre_atual = 'Segundo'
                    df_tri_estado = df[df['DATA'].dt.month == 2]
                elif mes_atual_do_ano_atual == 3:
                    trimestre_atual = 'Terceiro'
                    df_tri_estado = df[df['DATA'].dt.month == 3]
                else:
                    trimestre_atual = 'Quarto'
                    df_tri_estado = df[df['DATA'].dt.month == 4]
                return trimestre_atual, df_tri_estado
            
            trimestre_atual, df_tri_estado = selecionar_trimestre_atual(mes_atual_do_ano_atual)

            df_tri = df_tri_estado.copy()
            df_tri_alagoas = df_tri[df_tri['UF'] == 'Alagoas']
            df_tri_alagoas = df_tri_alagoas.copy()
            df_tri_alagoas.sort_values(by='DATA', ascending=False, inplace=True)
            df_tri_alagoas.reset_index(drop=True, inplace=True)

            ano_atual = df['DATA'].dt.year.max()
            ano_anterior = df['DATA'].dt.year.max() - 1
            df_ano_atual = df[df['DATA'].dt.year == ano_atual]
            df_alagoas_ano_atual = df[(df['UF'] == 'Alagoas') & (df['DATA'].dt.year == ano_atual)]
            ranking_estado_serie_ano_atual = df_ano_atual.groupby(['UF'])[['VALOR']].sum().sort_values(by='VALOR', ascending=False).reset_index()
            ranking_estado_serie_ano_atual.index += 1

        with st.container():

            digitacao(f" \
                        Ao realizar o recorte para o ano de {ano_atual} é possível observar e analisar as métricas de produção de leite cru industrializado em Alagoas e no Nordeste. \
                        O gráfico abaixo representa o percentual de produção no Estado de Alagoas por trimestre.\
                        ")
        
        with st.container(): 

            # Preparar os dados
            df_alagoas_ano_atual_graph = df_alagoas_ano_atual.copy()
            df_alagoas_ano_atual_graph['DATA'] = df_alagoas_ano_atual_graph['DATA'].apply(lambda x: f'{x.year} - {x.month}T')

            labels = df_alagoas_ano_atual_graph['DATA']
            values = df_alagoas_ano_atual_graph['VALOR']
            cores = ['#095aa2', '#0e89f7', '#042b4d']  # color_tres

            # Gerar gráfico com a função
            gerar_grafico_pizza(
                labels=labels,
                values=values,
                titulo_pdf=f'Produção de leite cru industrializado em Alagoas por Trimestre de {ano_atual}',
                cores=cores,
            )


        with st.container(): 

            df_alagoas = df_alagoas.copy()
            df_alagoas.sort_values(by='DATA', ascending=False, inplace=True)
            df_alagoas.reset_index(drop=True, inplace=True) 

            aumento_reducao_ano = 'um aumento' if (df_alagoas['VALOR'].values[0] - df_alagoas['VALOR'].values[1]) > 0 else 'uma redução'
            percentual = (df_alagoas['VALOR'].values[0] - df_alagoas['VALOR'].values[1]) / df_alagoas['VALOR'].values[1] * 100
        
            aumento_reducao_ano2 = 'um aumento' if (df_tri_alagoas['VALOR'].values[0] - df_tri_alagoas['VALOR'].values[1]) > 0 else 'uma redução'
            percentual2 = (df_tri_alagoas['VALOR'].values[0] - df_tri_alagoas['VALOR'].values[1]) / df_tri_alagoas['VALOR'].values[1] * 100

            digitacao(f" \
                Com base nos dados mais recentes, referentes ao {trimestre_atual.lower()} trimestre de {ano_atual}, \
                Alagoas registrou um total de {formatar_valor_sem_cifrao(df_alagoas['VALOR'].values[0])} litros, \
                representando {aumento_reducao_ano} de {formatar_valor2(percentual)} \
                em relação ao trimestre anterior, quando o estado registrou {formatar_valor_sem_cifrao(df_alagoas['VALOR'].values[1])} litros, \
                resultando em uma diferença nominal de {formatar_valor_sem_cifrao(df_alagoas['VALOR'].values[0] - df_alagoas['VALOR'].values[1])} litros. \
                \
                Comparando com o mesmo trimestre do ano anterior, nota-se que Alagoas teve {aumento_reducao_ano2} de {formatar_valor_sem_cifrao(percentual2)}, \
                quando foram registrados {formatar_valor_sem_cifrao(df_tri_alagoas['VALOR'].values[1])} litros, \
                resultando em uma diferença nominal de {formatar_valor_sem_cifrao(df_tri_alagoas['VALOR'].values[0] - df_tri_alagoas['VALOR'].values[1])}l litros. \
                \
                No total acumulado do ano, Alagoas registrou um volume de {formatar_valor_sem_cifrao(df_alagoas_ano_atual['VALOR'].sum())} litros, o que garantiu ao estado \
                a {ranking_estado_serie_ano_atual.index[ranking_estado_serie_ano_atual['UF'] == 'Alagoas'].values[0]}ª posição no ranking de produção de leite cru industrializado do Nordeste. \
                Os estados que ficaram à frente de Alagoas foram: {ranking_estado_serie_ano_atual['UF'].values[0]} (com {formatar_valor_sem_cifrao(ranking_estado_serie_ano_atual['VALOR'].values[0])}), \
                {ranking_estado_serie_ano_atual['UF'].values[1]} (com {formatar_valor_sem_cifrao(ranking_estado_serie_ano_atual['VALOR'].values[1])}), \
                {ranking_estado_serie_ano_atual['UF'].values[2]} (com {formatar_valor_sem_cifrao(ranking_estado_serie_ano_atual['VALOR'].values[2])}) e \
                {ranking_estado_serie_ano_atual['UF'].values[3]} (com {formatar_valor_sem_cifrao(ranking_estado_serie_ano_atual['VALOR'].values[3])}). \
                O ranking completo pode ser consultado no gráfico e na tabela abaixo. \
                ")

        with st.container(): 

        # Preparar os dados
            ranking_estado_serie_ano_atual['COLOR'] = np.where(
            ranking_estado_serie_ano_atual['UF'] == 'Alagoas',
            '#FCDC20',  # Amarelo para Alagoas
            '#095AA2'   # Azul padrão para os demais
        )

        x = ranking_estado_serie_ano_atual['UF']
        y = ranking_estado_serie_ano_atual['VALOR']
        cores = ranking_estado_serie_ano_atual['COLOR']
        titulo = f'Ranking de produção de leite cru industrializado por Estado - {df["DATA"].dt.year.max()}'

        # Gerar gráfico com a função
        gerar_grafico_barra(
            x=x,
            y=y,
            titulo_pdf=titulo,
            cores=cores,
        )

        with st.container(): 

            with st.expander(f":orange[Tabela 4.2.2] - Visualização da Série Histórica de produção de leite cru industrializado em Alagoas"):

                ranking_estado_serie_ano_atual['VALOR'] = ranking_estado_serie_ano_atual['VALOR'].apply(formatar_valor_sem_cifrao)
                ranking_estado_serie_ano_atual.drop(columns='COLOR', inplace=True)
                mostrar_tabela_pdf(ranking_estado_serie_ano_atual, nome_tabela='Ranking de produção de leite cru industrializado por Estado')

            st.write('---')