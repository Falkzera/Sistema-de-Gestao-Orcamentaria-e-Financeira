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
    menor_pico_producao,
    ranking_producao,
    recorte_temporal_ano_passado,
    formatar_valor,
    formatar_valor2,
)


with st.container(): # CORES
    color_tres = ['#095aa2', '#0e89f7', '#042b4d']
    degrade1 = ['#095aa2', '#085192', '#074882', '#063f71', '#053661', '#052d51', '#042441', '#031b31', '#021220', '#010910', '#000000']
    degrade2 = ['#095aa2', '#226bab', '#3a7bb5', '#538cbe', '#6b9cc7', '#84add1', '#9dbdda', '#b5cee3', '#cedeec', '#e6eff6', '#ffffff']
    fonte = '22px'
    CACHE_TTL = 60 * 60 * 24

def montar_relatorio_anp_preco_combustivel(df):

    with st.container(): # PREPRARAÇÃO DOS DADOS
         
        # abate_bovinos()
        df = read_parquet_file_from_drive('anp_preco_combustivel.parquet')


    with st.container(): # Introdução

        titulo_dinamico(f"# Preço Médio de Revenda de Combustíveis - Alagoas")
        digitacao(f" Nesta seção, será abordada a variação dos preços dos combustíveis ao longo dos anos, com foco no ano e trimestre corrente. Serão analisados os combustíveis derivados de petróleo, como gasolina comum e óleo diesel, além dos biocombustíveis renováveis, como o etanol, e dos combustíveis gasosos, como o Gás Natural Veicular (GNV).")

        with st.container(): # CONFIGURAÇÃO DE DATA E COLUNA

            df = df.rename(columns={'MÊS': 'DATA'})
            df['DATA'] = pd.to_datetime(df['DATA'], format='%Y-%m-%d') ##############
            df.sort_index(inplace=True)
            df = df[['DATA', 'PRODUTO', 'REGIÃO', 'ESTADO', 'MUNICÍPIO', 'PREÇO MÉDIO REVENDA']].sort_values(by='DATA').reset_index(drop=True)

        with st.container(): # CONFIGURANDO OS PRODUTOS
            # esta seleção é inutil, mas iniciei o código com ela
            produtos_selecionados = ['GASOLINA COMUM', 'OLEO DIESEL', 'ETANOL HIDRATADO', 'GNV']

        with st.container(): # CONFIGURAÇÃO DE ANO MAX/MIN & MES MAX/MIN
            
            ano_min = df['DATA'].min().year 
            ano_max = df['DATA'].max().year
            mes_min = df['DATA'].min().month
            mes_max_ano = df[df['DATA'].dt.year == ano_max]['DATA'].dt.month.max()

        with st.container(): # CONFIGURAÇÃO DE FILTROS & CRIAÇÃO DE DATAFRAMES A SEREM UTILIZADOS
            # Filtros Avançados
            df_filtrado = df[(df['REGIÃO'] == 'NORDESTE') & 
                            (df['ESTADO'] == 'ALAGOAS') & 
                            (df['PRODUTO'].isin(['GASOLINA COMUM', 'OLEO DIESEL', 'ETANOL HIDRATADO', 'GNV']))].reset_index(drop=True)

            df_municipio = df_filtrado [['DATA', 'PRODUTO', 'ESTADO', 'MUNICÍPIO', 'PREÇO MÉDIO REVENDA']]
            df_municipio_ano_max = df_municipio[df_municipio['DATA'].dt.year == ano_max].reset_index(drop=True)
            df_estado = df_filtrado.groupby(['DATA', 'PRODUTO', 'ESTADO'])[['PREÇO MÉDIO REVENDA']].mean().reset_index()
            df_estado_ano_max = df_estado[df_estado['DATA'].dt.year == ano_max].reset_index(drop=True)

    with st.container(): # SESSÃO 2.1
        
        with st.container(): # MÉTRICAS 1 - MÁXIMOS HISTÓRICOS - 2013-2024 - ESTADO DE ALAGOAS SESSÃO 2.2.1
            maximo_historico = df_estado[df_estado['PRODUTO'].isin((['GASOLINA COMUM', 'OLEO DIESEL', 'ETANOL HIDRATADO', 'GNV']))].groupby(['PRODUTO']).apply(lambda x: x.loc[x['PREÇO MÉDIO REVENDA'].idxmax()]).reset_index(drop=True)
            maximo_historico = maximo_historico.sort_values(by='DATA')

            # Valor Máximo do Produto 1
            valor_maximo_produto_1 = maximo_historico[maximo_historico['PRODUTO'] == produtos_selecionados[0]]['PREÇO MÉDIO REVENDA'].values[0]
            valor_maximo_produto_1_data_ano = maximo_historico[maximo_historico['PRODUTO'] == produtos_selecionados[0]]['DATA'].dt.year.values[0]
            valor_maximo_produto_1_data_mes = maximo_historico[maximo_historico['PRODUTO'] == produtos_selecionados[0]]['DATA'].dt.month.values[0]
            valor_maximo_nome_produto_1 = maximo_historico[maximo_historico['PRODUTO'] == produtos_selecionados[0]]['PRODUTO'].values[0]

            # Valor Máximo do Produto 2
            valor_maximo_produto_2 = maximo_historico[maximo_historico['PRODUTO'] == produtos_selecionados[1]]['PREÇO MÉDIO REVENDA'].values[0]
            valor_maximo_produto_2_data_ano = maximo_historico[maximo_historico['PRODUTO'] == produtos_selecionados[1]]['DATA'].dt.year.values[0]
            valor_maximo_produto_2_data_mes = maximo_historico[maximo_historico['PRODUTO'] == produtos_selecionados[1]]['DATA'].dt.month.values[0]
            valor_maximo_nome_produto_2 = maximo_historico[maximo_historico['PRODUTO'] == produtos_selecionados[1]]['PRODUTO'].values[0]

            # Valor Máximo do Produto 3
            valor_maximo_produto_3 = maximo_historico[maximo_historico['PRODUTO'] == produtos_selecionados[2]]['PREÇO MÉDIO REVENDA'].values[0]
            valor_maximo_produto_3_data_ano = maximo_historico[maximo_historico['PRODUTO'] == produtos_selecionados[2]]['DATA'].dt.year.values[0]
            valor_maximo_produto_3_data_mes = maximo_historico[maximo_historico['PRODUTO'] == produtos_selecionados[2]]['DATA'].dt.month.values[0]
            valor_maximo_nome_produto_3 = maximo_historico[maximo_historico['PRODUTO'] == produtos_selecionados[2]]['PRODUTO'].values[0]

            # Valor Máximo do Produto 4
            valor_maximo_produto_4 = maximo_historico[maximo_historico['PRODUTO'] == produtos_selecionados[3]]['PREÇO MÉDIO REVENDA'].values[0]
            valor_maximo_produto_4_data_ano = maximo_historico[maximo_historico['PRODUTO'] == produtos_selecionados[3]]['DATA'].dt.year.values[0]
            valor_maximo_produto_4_data_mes = maximo_historico[maximo_historico['PRODUTO'] == produtos_selecionados[3]]['DATA'].dt.month.values[0]
            valor_maximo_nome_produto_4 = maximo_historico[maximo_historico['PRODUTO'] == produtos_selecionados[3]]['PRODUTO'].values[0]
            
        with st.container(): # CABEÇALHO 1 SESSÃO 2.1
            titulo_dinamico(f'## Série Histórica do Preço Médio de Revenda de Combustíveis: {ano_min} - {ano_max}')

        with st.container(): # TEXTO 1 SESSÃO 4.2.1
            digitacao(f"O gráfico retrata uma série histórica de preço médio de revenda de combustíveis que varia de \
            {mes_min}/{ano_min} até {mes_max_ano}/{ano_max}. \
            Mostrando a evolução do preço médio de revenda ao longo do tempo.")

            digitacao(f" \
            Podemos observar que, o preço médio de revenda de {valor_maximo_nome_produto_1.title()} \
            atingiu o seu máximo histórico em {valor_maximo_produto_1_data_mes}/{valor_maximo_produto_1_data_ano}, \
            chegando a um valor médio de {formatar_valor(valor_maximo_produto_1)} por litro. \
            \
            Já o {valor_maximo_nome_produto_2.title()} atingiu o seu ápice histórico em \
            {valor_maximo_produto_2_data_mes}/{valor_maximo_produto_2_data_ano}, chegando a um valor médio de \
            {formatar_valor(valor_maximo_produto_2)} por litro. \
            \
            O produto {valor_maximo_nome_produto_3.title()} atingiu o seu máximo histórico em \
            {valor_maximo_produto_3_data_mes}/{valor_maximo_produto_3_data_ano}, chegando a um valor médio de \
            {formatar_valor(valor_maximo_produto_3)} por litro. \
            \
            Por fim, o produto {valor_maximo_nome_produto_4.title()} atingiu o seu máximo histórico em \
            {valor_maximo_produto_4_data_mes}/{valor_maximo_produto_4_data_ano}, chegando a um valor médio de \
            {formatar_valor(valor_maximo_produto_4)} por m³. ")

        with st.container():  # GRÁFICO 1 SESSÃO 4.2.1

            # Preparando dados para a função
            x_series = []
            y_series = []
            nomes_series = []

            for produto in produtos_selecionados:
                df_graph = df_estado[df_estado['PRODUTO'] == produto].groupby('DATA')[['PREÇO MÉDIO REVENDA']].mean().reset_index()
                x_series.append(df_graph['DATA'])
                y_series.append(df_graph['PREÇO MÉDIO REVENDA'])
                nomes_series.append(produto)

            # Chamando função com tudo preparado
            gerar_grafico_linha(
                x=x_series,
                y=y_series,
                titulo_pdf=f'Série Histórica - Combustíveis',
                nomes_series=nomes_series,
                cores=color_tres,
            )

        with st.container():  # MÉTRICAS 2 - TAXA DE CRESCIMENTO 2013-2024 - ESTADO DE ALAGOAS SESSÃO 4.2.1
            # Filtrar os dados do estado de Alagoas
            df_estado_agrupado = df_estado.groupby([df_estado['DATA'].dt.year, 'PRODUTO'])[['PREÇO MÉDIO REVENDA']].mean().reset_index()

            # Valores iniciais (primeiro ano) e finais (último ano) para cada produto
            cagr_ano_min = df_estado_agrupado['DATA'].min()
            cagr_ano_max = df_estado_agrupado['DATA'].max()

            # Filtrar valores do primeiro e último ano
            preco_inicial = df_estado_agrupado[df_estado_agrupado['DATA'] == cagr_ano_min][['PRODUTO', 'PREÇO MÉDIO REVENDA']].set_index('PRODUTO')
            preco_final = df_estado_agrupado[df_estado_agrupado['DATA'] == cagr_ano_max][['PRODUTO', 'PREÇO MÉDIO REVENDA']].set_index('PRODUTO')

            # Calcular o CAGR para cada produto
            cagr = (preco_final['PREÇO MÉDIO REVENDA'] / preco_inicial['PREÇO MÉDIO REVENDA']) * (1 / (cagr_ano_max - cagr_ano_min)) - 1

            # Ordenar o DataFrame pelo CAGR
            cagr = cagr.reset_index().sort_values(by='PREÇO MÉDIO REVENDA', ascending=False)

            # Extrair o CAGR para os produtos selecionados
            cagr_produto_1 = cagr[cagr['PRODUTO'] == produtos_selecionados[0]]['PREÇO MÉDIO REVENDA'].values[0] * 100
            cagr_nome_produto_1 = cagr[cagr['PRODUTO'] == produtos_selecionados[0]]['PRODUTO'].values[0] 
            cagr_produto_2 = cagr[cagr['PRODUTO'] == produtos_selecionados[1]]['PREÇO MÉDIO REVENDA'].values[0] * 100
            cagr_nome_produto_2 = cagr[cagr['PRODUTO'] == produtos_selecionados[1]]['PRODUTO'].values[0]
            cagr_produto_3 = cagr[cagr['PRODUTO'] == produtos_selecionados[2]]['PREÇO MÉDIO REVENDA'].values[0] * 100
            cagr_nome_produto_3 = cagr[cagr['PRODUTO'] == produtos_selecionados[2]]['PRODUTO'].values[0]
            cagr_produto_4 = cagr[cagr['PRODUTO'] == produtos_selecionados[3]]['PREÇO MÉDIO REVENDA'].values[0] * 100
            cagr_nome_produto_4 = cagr[cagr['PRODUTO'] == produtos_selecionados[3]]['PRODUTO'].values[0]

        with st.container(): # TEXTO 2 SESSÃO 4.2.1
            digitacao(f" \
            A Taxa de Crescimento Anual Composto (CAGR) para {cagr_nome_produto_1.title()} \
            foi de {formatar_valor2(cagr_produto_1)}, \
            já para {cagr_nome_produto_2.title()} foi de {formatar_valor2(cagr_produto_2)}, \
            por sua vez o {cagr_nome_produto_3.title()} obteve uma taxa de crescimento de {formatar_valor2(cagr_produto_3)} e   \
            por fim para o {cagr_nome_produto_4.title()} a taxa foi de {formatar_valor2(cagr_produto_4)} ")

        with st.container(): # MÉTRICAS 3 SESSÃO 4.2.1 (VARIAÇÃO PERCENTUAL SÉRIE HISTÓRICA)

            df_comp_estado_anual = df_estado.groupby([df_estado['DATA'].dt.year, 'PRODUTO', 'ESTADO'])[['PREÇO MÉDIO REVENDA']].mean().reset_index()

            # Implementação coluna de variação percentual referente ao ano anterior para cada produto
            df_comp_estado_anual_etanol = df_comp_estado_anual[df_comp_estado_anual['PRODUTO'] == 'ETANOL HIDRATADO']
            df_comp_estado_anual_etanol['VARIAÇÃO %'] = df_comp_estado_anual_etanol.groupby(['PRODUTO', 'ESTADO'])['PREÇO MÉDIO REVENDA'].pct_change() * 100
            df_comp_estado_anual_etanol['DIFERENCA'] = df_comp_estado_anual_etanol['PREÇO MÉDIO REVENDA'].diff()

            df_comp_estado_anual_gasolina = df_comp_estado_anual[df_comp_estado_anual['PRODUTO'] == 'GASOLINA COMUM']
            df_comp_estado_anual_gasolina['VARIAÇÃO %'] = df_comp_estado_anual_gasolina.groupby(['PRODUTO', 'ESTADO'])['PREÇO MÉDIO REVENDA'].pct_change() * 100
            df_comp_estado_anual_gasolina['DIFERENCA'] = df_comp_estado_anual_gasolina['PREÇO MÉDIO REVENDA'].diff()

            df_comp_estado_anual_diesel = df_comp_estado_anual[df_comp_estado_anual['PRODUTO'] == 'OLEO DIESEL']
            df_comp_estado_anual_diesel['VARIAÇÃO %'] = df_comp_estado_anual_diesel.groupby(['PRODUTO', 'ESTADO'])['PREÇO MÉDIO REVENDA'].pct_change() * 100
            df_comp_estado_anual_diesel['DIFERENCA'] = df_comp_estado_anual_diesel['PREÇO MÉDIO REVENDA'].diff()

            df_comp_estado_anual_gnv = df_comp_estado_anual[df_comp_estado_anual['PRODUTO'] == 'GNV']
            df_comp_estado_anual_gnv['VARIAÇÃO %'] = df_comp_estado_anual_gnv.groupby(['PRODUTO', 'ESTADO'])['PREÇO MÉDIO REVENDA'].pct_change() * 100
            df_comp_estado_anual_gnv['DIFERENCA'] = df_comp_estado_anual_gnv['PREÇO MÉDIO REVENDA'].diff()

        with st.container(): # TEXTO 3 SESSÃO 4.2.1

            digitacao(f"O gráfico abaixo representa a variação percentual e monetária dos combustíveis ao longo de toda série histórica. ")

        with st.container(): # FORMATO TABULAR 1 SESSÃO 4.2.1

            titulo_dinamico(f"Visualização das Tabelas de Variação Percentual {ano_min - 1} - {ano_max}")


            df_comp_estado_anual_etanol_table = df_comp_estado_anual_etanol.copy()
            df_comp_estado_anual_etanol_table['PREÇO MÉDIO REVENDA'] = df_comp_estado_anual_etanol_table['PREÇO MÉDIO REVENDA'].apply(formatar_valor)
            df_comp_estado_anual_etanol_table = df_comp_estado_anual_etanol_table.iloc[1:]
            df_comp_estado_anual_etanol_table['DIFERENCA'] = df_comp_estado_anual_etanol_table['DIFERENCA'].apply(formatar_valor)
            df_comp_estado_anual_etanol_table['VARIAÇÃO %'] = df_comp_estado_anual_etanol_table['VARIAÇÃO %'].apply(formatar_valor2)
            df_comp_estado_anual_etanol_table = df_comp_estado_anual_etanol_table.reset_index(drop=True)
            mostrar_tabela_pdf(df_comp_estado_anual_etanol_table, nome_tabela='Etanol Hidratado')

            df_comp_estado_anual_gasolina_table = df_comp_estado_anual_gasolina.copy()
            df_comp_estado_anual_gasolina_table['PREÇO MÉDIO REVENDA'] = df_comp_estado_anual_gasolina_table['PREÇO MÉDIO REVENDA'].apply(formatar_valor)
            df_comp_estado_anual_gasolina_table = df_comp_estado_anual_gasolina_table.iloc[1:]
            df_comp_estado_anual_gasolina_table['DIFERENCA'] = df_comp_estado_anual_gasolina_table['DIFERENCA'].apply(formatar_valor)
            df_comp_estado_anual_gasolina_table['VARIAÇÃO %'] = df_comp_estado_anual_gasolina_table['VARIAÇÃO %'].apply(formatar_valor2)
            df_comp_estado_anual_gasolina_table = df_comp_estado_anual_gasolina_table.reset_index(drop=True)
            mostrar_tabela_pdf(df_comp_estado_anual_gasolina_table, nome_tabela='Gasolina Comum')
        
            df_comp_estado_anual_diesel_table = df_comp_estado_anual_diesel.copy()
            df_comp_estado_anual_diesel_table['PREÇO MÉDIO REVENDA'] = df_comp_estado_anual_diesel_table['PREÇO MÉDIO REVENDA'].apply(formatar_valor)
            df_comp_estado_anual_diesel_table = df_comp_estado_anual_diesel_table.iloc[1:]
            df_comp_estado_anual_diesel_table['DIFERENCA'] = df_comp_estado_anual_diesel_table['DIFERENCA'].apply(formatar_valor)
            df_comp_estado_anual_diesel_table['VARIAÇÃO %'] = df_comp_estado_anual_diesel_table['VARIAÇÃO %'].apply(formatar_valor2)
            df_comp_estado_anual_diesel_table = df_comp_estado_anual_diesel_table.reset_index(drop=True)
            mostrar_tabela_pdf(df_comp_estado_anual_diesel_table, nome_tabela='Óleo Diesel')

            df_comp_estado_anual_gnv_table = df_comp_estado_anual_gnv.copy()
            df_comp_estado_anual_gnv_table['PREÇO MÉDIO REVENDA'] = df_comp_estado_anual_gnv_table['PREÇO MÉDIO REVENDA'].apply(formatar_valor)
            df_comp_estado_anual_gnv_table = df_comp_estado_anual_gnv_table.iloc[1:]
            df_comp_estado_anual_gnv_table['DIFERENCA'] = df_comp_estado_anual_gnv_table['DIFERENCA'].apply(formatar_valor)
            df_comp_estado_anual_gnv_table['VARIAÇÃO %'] = df_comp_estado_anual_gnv_table['VARIAÇÃO %'].apply(formatar_valor2)
            df_comp_estado_anual_gnv_table = df_comp_estado_anual_gnv_table.reset_index(drop=True)
            mostrar_tabela_pdf(df_comp_estado_anual_gnv_table, nome_tabela='GNV')

        with st.container(): # TEXTO 4 SESSÃO 4.2.1

            digitacao(f" \
            A variação percentual do preço médio de revenda do Etanol referente ao ano de {ano_max} \
            em relação ao {ano_max - 1} foi de {formatar_valor2(df_comp_estado_anual_etanol['VARIAÇÃO %'].values[-1])}. \
            Isso significa uma mudança no preço médio de {formatar_valor(df_comp_estado_anual_etanol['DIFERENCA'].values[-1])}. \
            \
            Já para a Gasolina Comum foi de {formatar_valor2(df_comp_estado_anual_gasolina['VARIAÇÃO %'].values[-1])}. \
            Representando uma modificação no preço médio de {formatar_valor(df_comp_estado_anual_gasolina['DIFERENCA'].values[-1])}. \
            \
            Em relação ao Óleo Diesel obteve uma alteração de {formatar_valor2(df_comp_estado_anual_diesel['VARIAÇÃO %'].values[-1])}, \
            demonstrando uma mudança no preço médio de {formatar_valor(df_comp_estado_anual_diesel['DIFERENCA'].values[-1])}. \
            \
            Por fim, o GNV obteve uma variação de {formatar_valor2(df_comp_estado_anual_gnv['VARIAÇÃO %'].values[-1])}, \
            significando uma mudança no preço médio de {formatar_valor(df_comp_estado_anual_gnv['DIFERENCA'].values[-1])}. ")

    with st.container(): # SESSÃO 4.2.2
        pass

        with st.container(): # MÉTRICAS 4 - MÁXIMOS HISTÓRICOS - 2024 - ESTADO DE ALAGOAS SESSÃO 4.2.2
            maximo_historico_ano_max = df_estado_ano_max[df_estado_ano_max['PRODUTO'].isin(['GASOLINA COMUM', 'OLEO DIESEL', 'ETANOL HIDRATADO', 'GNV'])].groupby(['PRODUTO']).apply(lambda x: x.loc[x['PREÇO MÉDIO REVENDA'].idxmax()]).reset_index(drop=True)

            # Valor Máximo do Produto 1
            valor_maximo_produto_1 = maximo_historico_ano_max[maximo_historico_ano_max['PRODUTO'] == produtos_selecionados[0]]['PREÇO MÉDIO REVENDA'].values[0]
            valor_maximo_produto_1_data_ano = maximo_historico_ano_max[maximo_historico_ano_max['PRODUTO'] == produtos_selecionados[0]]['DATA'].dt.year.values[0]
            valor_maximo_produto_1_data_mes = maximo_historico_ano_max[maximo_historico_ano_max['PRODUTO'] == produtos_selecionados[0]]['DATA'].dt.month.values[0]
            valor_maximo_nome_produto_1 = maximo_historico_ano_max[maximo_historico_ano_max['PRODUTO'] == produtos_selecionados[0]]['PRODUTO'].values[0]

            # Valor Máximo do Produto 2
            valor_maximo_produto_2 = maximo_historico_ano_max[maximo_historico_ano_max['PRODUTO'] == produtos_selecionados[1]]['PREÇO MÉDIO REVENDA'].values[0]
            valor_maximo_produto_2_data_ano = maximo_historico_ano_max[maximo_historico_ano_max['PRODUTO'] == produtos_selecionados[1]]['DATA'].dt.year.values[0]
            valor_maximo_produto_2_data_mes = maximo_historico_ano_max[maximo_historico_ano_max['PRODUTO'] == produtos_selecionados[1]]['DATA'].dt.month.values[0]
            valor_maximo_nome_produto_2 = maximo_historico_ano_max[maximo_historico_ano_max['PRODUTO'] == produtos_selecionados[1]]['PRODUTO'].values[0]

            # Valor Máximo do Produto 3
            valor_maximo_produto_3 = maximo_historico_ano_max[maximo_historico_ano_max['PRODUTO'] == produtos_selecionados[2]]['PREÇO MÉDIO REVENDA'].values[0]
            valor_maximo_produto_3_data_ano = maximo_historico_ano_max[maximo_historico_ano_max['PRODUTO'] == produtos_selecionados[2]]['DATA'].dt.year.values[0]
            valor_maximo_produto_3_data_mes = maximo_historico_ano_max[maximo_historico_ano_max['PRODUTO'] == produtos_selecionados[2]]['DATA'].dt.month.values[0]
            valor_maximo_nome_produto_3 = maximo_historico_ano_max[maximo_historico_ano_max['PRODUTO'] == produtos_selecionados[2]]['PRODUTO'].values[0]

            # Valor Máximo do Produto 4
            valor_maximo_produto_4 = maximo_historico_ano_max[maximo_historico_ano_max['PRODUTO'] == produtos_selecionados[3]]['PREÇO MÉDIO REVENDA'].values[0]
            valor_maximo_produto_4_data_ano = maximo_historico_ano_max[maximo_historico_ano_max['PRODUTO'] == produtos_selecionados[3]]['DATA'].dt.year.values[0]
            valor_maximo_produto_4_data_mes = maximo_historico_ano_max[maximo_historico_ano_max['PRODUTO'] == produtos_selecionados[3]]['DATA'].dt.month.values[0]
            valor_maximo_nome_produto_4 = maximo_historico_ano_max[maximo_historico_ano_max['PRODUTO'] == produtos_selecionados[3]]['PRODUTO'].values[0]
            
        with st.container(): # CABEÇALHO 2 SESSÃO 4.2.2
            titulo_dinamico(f'## Análise: {ano_max}')

        with st.container(): # TEXTO 4 SESSÃO 4.2.2
            digitacao(f" \
            Já para o ano corrente, observamos que, o preço médio de revenda de {valor_maximo_nome_produto_1.title()} \
            atingiu o seu máximo em {valor_maximo_produto_1_data_mes}/{valor_maximo_produto_1_data_ano}, \
            chegando a um valor médio de {formatar_valor(valor_maximo_produto_1)} por litro. \
            \
            Já o {valor_maximo_nome_produto_2.title()} atingiu o seu máximo em \
            {valor_maximo_produto_2_data_mes}/{valor_maximo_produto_2_data_ano}, chegando a um valor médio de \
            {formatar_valor(valor_maximo_produto_2)} por litro. \
            \
            Em relação ao {valor_maximo_nome_produto_3.title()} atingiu o seu pico em \
            {valor_maximo_produto_3_data_mes}/{valor_maximo_produto_3_data_ano}, chegando a um valor médio de \
            {formatar_valor(valor_maximo_produto_3)} por litro. \
            \
            Por fim, o {valor_maximo_nome_produto_4.title()} atingiu o seu máximo em \
            {valor_maximo_produto_4_data_mes}/{valor_maximo_produto_4_data_ano}, chegando a um valor médio de \
            {formatar_valor(valor_maximo_produto_4)} por m³. ")

        # se a quantiadade de meses do ano atual for maior que 1
        if len(df_estado_ano_max['DATA'].dt.month.unique()) > 1:


            with st.container():  # MÉTRICAS 5 - TAXA DE CRESCIMENTO 2024 - ESTADO DE ALAGOAS
                # Filtrar os dados do estado de Alagoas
                df_estado_agrupado = df_estado_ano_max.groupby([df_estado_ano_max['DATA'].dt.month, 'PRODUTO'])[['PREÇO MÉDIO REVENDA']].mean().reset_index()

                # Valores iniciais (primeiro ano) e finais (último ano) para cada produto
                cagr_mes_min = df_estado_agrupado['DATA'].min()
                cagr_mes_max = df_estado_agrupado['DATA'].max()

                # Filtrar valores do primeiro e último ano
                preco_inicial = df_estado_agrupado[df_estado_agrupado['DATA'] == cagr_mes_min][['PRODUTO', 'PREÇO MÉDIO REVENDA']].set_index('PRODUTO')
                preco_final = df_estado_agrupado[df_estado_agrupado['DATA'] == cagr_mes_max][['PRODUTO', 'PREÇO MÉDIO REVENDA']].set_index('PRODUTO')

                # Calcular o CAGR para cada produto
                cagr = (preco_final['PREÇO MÉDIO REVENDA'] / preco_inicial['PREÇO MÉDIO REVENDA']) * (1 / (cagr_mes_max - cagr_mes_min)) - 1

                # Ordenar o DataFrame pelo CAGR
                cagr = cagr.reset_index().sort_values(by='PREÇO MÉDIO REVENDA', ascending=False)

                # Extrair o CAGR para os produtos selecionados
                cagr_produto_1 = cagr[cagr['PRODUTO'] == produtos_selecionados[0]]['PREÇO MÉDIO REVENDA'].values[0] * 100
                cagr_nome_produto_1 = cagr[cagr['PRODUTO'] == produtos_selecionados[0]]['PRODUTO'].values[0]
                cagr_produto_2 = cagr[cagr['PRODUTO'] == produtos_selecionados[1]]['PREÇO MÉDIO REVENDA'].values[0] * 100
                cagr_nome_produto_2 = cagr[cagr['PRODUTO'] == produtos_selecionados[1]]['PRODUTO'].values[0]
                cagr_produto_3 = cagr[cagr['PRODUTO'] == produtos_selecionados[2]]['PREÇO MÉDIO REVENDA'].values[0] * 100
                cagr_nome_produto_3 = cagr[cagr['PRODUTO'] == produtos_selecionados[2]]['PRODUTO'].values[0]
                cagr_produto_4 = cagr[cagr['PRODUTO'] == produtos_selecionados[3]]['PREÇO MÉDIO REVENDA'].values[0] * 100
                cagr_nome_produto_4 = cagr[cagr['PRODUTO'] == produtos_selecionados[3]]['PRODUTO'].values[0]

            with st.container(): # TEXTO 5 SESSÃO 4.2.2
                digitacao(f" \
                A Taxa de Crescimento Mensal para o ano de {ano_max}, para o produto {cagr_nome_produto_1.title()} \
                foi de {cagr_produto_1:.2f}%. \
                \
                Já para o {cagr_nome_produto_2.title()} foi de {cagr_produto_2:.2f}%. \
                \
                Em relação ao {cagr_nome_produto_3.title()} obteve uma taxa de crescimento de {cagr_produto_3:.2f}%. \
                \
                Por fim, o {cagr_nome_produto_4.title()} obteve uma taxa de {cagr_produto_4:.2f}%. ")

            with st.container(): # MÉTRICAS 3 SESSÃO 4.2.1 (VARIAÇÃO PERCENTUAL SÉRIE HISTÓRICA - ANO DE 2024)

                df_comp_estado_anual = df_estado_ano_max.groupby([df_estado_ano_max['DATA'].dt.month, 'PRODUTO', 'ESTADO'])[['PREÇO MÉDIO REVENDA']].mean().reset_index()

                # Implementação coluna de variação percentual referente ao ano anterior para cada produto
                df_comp_estado_anual_etanol = df_comp_estado_anual[df_comp_estado_anual['PRODUTO'] == 'ETANOL HIDRATADO']
                df_comp_estado_anual_etanol['VARIAÇÃO %'] = df_comp_estado_anual_etanol.groupby(['PRODUTO', 'ESTADO'])['PREÇO MÉDIO REVENDA'].pct_change() * 100
                df_comp_estado_anual_etanol['DIFERENCA'] = df_comp_estado_anual_etanol['PREÇO MÉDIO REVENDA'].diff()

                df_comp_estado_anual_gasolina = df_comp_estado_anual[df_comp_estado_anual['PRODUTO'] == 'GASOLINA COMUM']
                df_comp_estado_anual_gasolina['VARIAÇÃO %'] = df_comp_estado_anual_gasolina.groupby(['PRODUTO', 'ESTADO'])['PREÇO MÉDIO REVENDA'].pct_change() * 100
                df_comp_estado_anual_gasolina['DIFERENCA'] = df_comp_estado_anual_gasolina['PREÇO MÉDIO REVENDA'].diff()

                df_comp_estado_anual_diesel = df_comp_estado_anual[df_comp_estado_anual['PRODUTO'] == 'OLEO DIESEL']
                df_comp_estado_anual_diesel['VARIAÇÃO %'] = df_comp_estado_anual_diesel.groupby(['PRODUTO', 'ESTADO'])['PREÇO MÉDIO REVENDA'].pct_change() * 100
                df_comp_estado_anual_diesel['DIFERENCA'] = df_comp_estado_anual_diesel['PREÇO MÉDIO REVENDA'].diff()

                df_comp_estado_anual_gnv = df_comp_estado_anual[df_comp_estado_anual['PRODUTO'] == 'GNV']
                df_comp_estado_anual_gnv['VARIAÇÃO %'] = df_comp_estado_anual_gnv.groupby(['PRODUTO', 'ESTADO'])['PREÇO MÉDIO REVENDA'].pct_change() * 100
                df_comp_estado_anual_gnv['DIFERENCA'] = df_comp_estado_anual_gnv['PREÇO MÉDIO REVENDA'].diff()

            with st.container(): # TEXTO 4 SESSÃO 4.2.1

                digitacao(f" \
                A variação percentual do preço médio de revenda do Etanol referente ao ano de {ano_max} \
                em relação aos seus meses foi de {(df_comp_estado_anual_etanol['VARIAÇÃO %'].values[-1])}. \
                Isso significa uma mudança no preço médio de {(df_comp_estado_anual_etanol['DIFERENCA'].values[-1])}. \
                \
                Já para a Gasolina Comum foi de {(df_comp_estado_anual_gasolina['VARIAÇÃO %'].values[-1])}. \
                Isso significa uma mudança no preço médio de {(df_comp_estado_anual_gasolina['DIFERENCA'].values[-1])}. \
                \
                Em relação ao Óleo Diesel obteve uma variação de {(df_comp_estado_anual_diesel['VARIAÇÃO %'].values[-1])}, \
                significando uma mudança no preço médio de R$ {df_comp_estado_anual_diesel['DIFERENCA'].values[-1]:.2f}. \
                \
                Por fim, o GNV obteve uma variação de {(df_comp_estado_anual_gnv['VARIAÇÃO %'].values[-1])}, \
                significando uma mudança no preço médio de {(df_comp_estado_anual_gnv['DIFERENCA'].values[-1])}. ")

    with st.container(): # SESSÃO 4.2.3
        pass
        
        with st.container(): # CABEÇALHO 3 SESSÃO 4.2.3
            titulo_dinamico(f'## Comparação entre Municípios - {ano_max}')

        with st.container(): # MÉTRICAS 6 SESSÃO 4.2.3
            
            # ranking dos municipios
            ranking_municipio = df_municipio_ano_max.groupby(['MUNICÍPIO', 'PRODUTO'])[['PREÇO MÉDIO REVENDA']].mean().reset_index()
            ranking_municipio_graph = df_municipio_ano_max.groupby(['MUNICÍPIO', 'PRODUTO'])[['PREÇO MÉDIO REVENDA']].mean().reset_index()
            #sort values by PREÇO MÉDIO REVENDA
            ranking_municipio = ranking_municipio.sort_values(by='PREÇO MÉDIO REVENDA', ascending=False)

            # Valor Máximo do Produto 1
            valor_maximo_produto_1 = ranking_municipio[ranking_municipio['PRODUTO'] == produtos_selecionados[0]].head(3)
            valor_maximo_produto_1_data_ano = valor_maximo_produto_1['PREÇO MÉDIO REVENDA'].values
            valor_maximo_produto_1_data_mes = valor_maximo_produto_1['MUNICÍPIO'].values
            valor_maximo_nome_produto_1 = valor_maximo_produto_1['PRODUTO'].values[0]

            # Valor Máximo do Produto 2
            valor_maximo_produto_2 = ranking_municipio[ranking_municipio['PRODUTO'] == produtos_selecionados[1]].head(3)
            valor_maximo_produto_2_data_ano = valor_maximo_produto_2['PREÇO MÉDIO REVENDA'].values
            valor_maximo_produto_2_data_mes = valor_maximo_produto_2['MUNICÍPIO'].values
            valor_maximo_nome_produto_2 = valor_maximo_produto_2['PRODUTO'].values[0]

            # Valor Máximo do Produto 3
            valor_maximo_produto_3 = ranking_municipio[ranking_municipio['PRODUTO'] == produtos_selecionados[2]].head(3)
            valor_maximo_produto_3_data_ano = valor_maximo_produto_3['PREÇO MÉDIO REVENDA'].values
            valor_maximo_produto_3_data_mes = valor_maximo_produto_3['MUNICÍPIO'].values
            valor_maximo_nome_produto_3 = valor_maximo_produto_3['PRODUTO'].values[0]

            # Valor Máximo do Produto 4
            valor_maximo_produto_4 = ranking_municipio[ranking_municipio['PRODUTO'] == produtos_selecionados[3]].head(3)
            valor_maximo_produto_4_data_ano = valor_maximo_produto_4['PREÇO MÉDIO REVENDA'].values
            valor_maximo_produto_4_data_mes = valor_maximo_produto_4['MUNICÍPIO'].values
            valor_maximo_nome_produto_4 = valor_maximo_produto_4['PRODUTO'].values[0]

        
        with st.container():  # TEXTO 6 SESSÃO 4.2.3
            # Preços médios de revenda dos produtos
            digitacao(f" Ao realizar uma análise de comparação de preços entre os municípios, foi observado que\
            em {ano_max}, os três municípios com maior preço médio de revenda de {valor_maximo_nome_produto_1.title()} foram: \
            {valor_maximo_produto_1_data_mes[0].title()} ({formatar_valor(valor_maximo_produto_1_data_ano[0])}/litro), \
            seguido por {valor_maximo_produto_1_data_mes[1].title()} ({formatar_valor(valor_maximo_produto_1_data_ano[1])}/litro) e {valor_maximo_produto_1_data_mes[2].title()} \
            ({formatar_valor(valor_maximo_produto_1_data_ano[2])}/litro).")

            digitacao(f" \
            Para o {valor_maximo_nome_produto_2.title()}, os maiores preços foram registrados em: {valor_maximo_produto_2_data_mes[0].title()} \
            ({formatar_valor(valor_maximo_produto_2_data_ano[0])}/litro), {valor_maximo_produto_2_data_mes[1].title()} ({formatar_valor(valor_maximo_produto_2_data_ano[1])}/litro) e {valor_maximo_produto_2_data_mes[2].title()} \
            ({formatar_valor(valor_maximo_produto_2_data_ano[2])}/litro).")

            digitacao(f" \
            No caso do {valor_maximo_nome_produto_3.title()}, os três municípios com os maiores preços médios foram: {valor_maximo_produto_3_data_mes[0].title()} \
            ({formatar_valor(valor_maximo_produto_3_data_ano[0])}/litro), {valor_maximo_produto_3_data_mes[1].title()} ({formatar_valor(valor_maximo_produto_3_data_ano[1])}/litro) e {valor_maximo_produto_3_data_mes[2].title()} \
            ({formatar_valor(valor_maximo_produto_3_data_ano[2])}/litro).")

            digitacao(f" \
            Por fim, os maiores preços médios de revenda de {valor_maximo_nome_produto_4} ocorreram em: {valor_maximo_produto_4_data_mes[0].title()} \
            ({formatar_valor(valor_maximo_produto_4_data_ano[0])}/m³), {valor_maximo_produto_4_data_mes[1].title()} ({formatar_valor(valor_maximo_produto_4_data_ano[1])}/m³) e {valor_maximo_produto_4_data_mes[2].title()} \
            ({formatar_valor(valor_maximo_produto_4_data_ano[2])}/m³).")

        with st.container():  # GRÁFICO COMPARAÇÃO MUNICÍPIOS - SESSÃO 2.3

            # Preparando os dados
            x_series = []
            y_series = []
            cores = []
            nomes_series = []

            for i, produto in enumerate(produtos_selecionados):
                df_graph = ranking_municipio_graph[ranking_municipio_graph['PRODUTO'] == produto]
                x_series.extend(df_graph['MUNICÍPIO'])
                y_series.extend(df_graph['PREÇO MÉDIO REVENDA'])
                cores.extend([color_tres[i % len(color_tres)]] * len(df_graph))
                nomes_series.extend([produto] * len(df_graph))  # Não usado agora, mas se quiser agrupar por produto, tá pronto

            # Título formatado
            titulo = f'Comparação do preço médio de revenda por Município em {ano_max}'

            # Gerar gráfico com a função
            gerar_grafico_barra(
                x=x_series,
                y=y_series,
                titulo_pdf=titulo,
                cores=cores,
            )

    with st.container(): # SESSÃO 4.2.4
        pass

        with st.container(): # MÉTRICAS 7 SESSÃO 4.2.4 (DEFININDO TRIMESTRE ANTERIOR)
                        
                        mes_atual_do_ano_atual = df[df['DATA'].dt.year == ano_max]['DATA'].dt.month.max() # Último mês do ano atual

                        # Trimestre Atual!
                        def selecionar_trimestre_atual(mes_atual_do_ano_atual, df=df_estado, base=df_municipio):
                            if 1 <= mes_atual_do_ano_atual <= 3:
                                trimestre_atual = 'Primeiro'
                                df_tri_estado = df[df['DATA'].dt.month <= 3]
                                df_tri_municipio = base[base['DATA'].dt.month <= 3]
                            elif 4 <= mes_atual_do_ano_atual <= 6:
                                trimestre_atual = 'Segundo'
                                df_tri_estado = df[(df['DATA'].dt.month > 3) & (df['DATA'].dt.month <= 6)]
                                df_tri_municipio = base[(base['DATA'].dt.month > 3) & (base['DATA'].dt.month <= 6)]
                            elif 7 <= mes_atual_do_ano_atual <= 9:
                                trimestre_atual = 'Terceiro'
                                df_tri_estado = df[(df['DATA'].dt.month > 6) & (df['DATA'].dt.month <= 9)]
                                df_tri_municipio = base[(base['DATA'].dt.month > 6) & (base['DATA'].dt.month <= 9)]
                            else:
                                trimestre_atual = 'Quarto'
                                df_tri_estado = df[(df['DATA'].dt.month > 9) & (df['DATA'].dt.month <= 12)]
                                df_tri_municipio = base[(base['DATA'].dt.month > 9) & (base['DATA'].dt.month <= 12)]
                            return trimestre_atual, df_tri_estado, df_tri_municipio
                        
                        trimestre_atual, df_tri_estado, df_tri_municipio = selecionar_trimestre_atual(mes_atual_do_ano_atual)

        with st.container(): # CABEÇALHO 4 SESSÃO 4.2.4
            titulo_dinamico(f'## Comparação de Variação: {trimestre_atual} Trimestre de {ano_min + 1} - {ano_max}')

        with st.container(): # MÉTRICAS 8 SESSÃO 4.2.4 (VARIAÇÃO PERCENTUAL TRIMESTRAL PARA O ULTIMO TRIMESTRE)

            df_tri_estado_anual = df_tri_estado.groupby([df_tri_estado['DATA'].dt.year, 'PRODUTO', 'ESTADO'])[['PREÇO MÉDIO REVENDA']].mean().reset_index()
            df_tri_municipio_anual = df_tri_municipio.groupby([df_tri_municipio['DATA'].dt.year, 'PRODUTO', 'MUNICÍPIO'])[['PREÇO MÉDIO REVENDA']].mean().reset_index()

            # Implementação coluna de variação percentual referente ao ano anterior para cada produto
            df_tri_estado_anual_etanol = df_tri_estado_anual[df_tri_estado_anual['PRODUTO'] == 'ETANOL HIDRATADO']
            df_tri_estado_anual_etanol['VARIAÇÃO %'] = df_tri_estado_anual_etanol.groupby(['PRODUTO', 'ESTADO'])['PREÇO MÉDIO REVENDA'].pct_change() * 100
            df_tri_estado_anual_etanol['DIFERENCA'] = df_tri_estado_anual_etanol['PREÇO MÉDIO REVENDA'].diff()

            df_tri_estado_anual_gasolina = df_tri_estado_anual[df_tri_estado_anual['PRODUTO'] == 'GASOLINA COMUM']
            df_tri_estado_anual_gasolina['VARIAÇÃO %'] = df_tri_estado_anual_gasolina.groupby(['PRODUTO', 'ESTADO'])['PREÇO MÉDIO REVENDA'].pct_change() * 100
            df_tri_estado_anual_gasolina['DIFERENCA'] = df_tri_estado_anual_gasolina['PREÇO MÉDIO REVENDA'].diff()

            df_tri_estado_anual_diesel = df_tri_estado_anual[df_tri_estado_anual['PRODUTO'] == 'OLEO DIESEL']
            df_tri_estado_anual_diesel['VARIAÇÃO %'] = df_tri_estado_anual_diesel.groupby(['PRODUTO', 'ESTADO'])['PREÇO MÉDIO REVENDA'].pct_change() * 100
            df_tri_estado_anual_diesel['DIFERENCA'] = df_tri_estado_anual_diesel['PREÇO MÉDIO REVENDA'].diff()

            df_tri_estado_anual_gnv = df_tri_estado_anual[df_tri_estado_anual['PRODUTO'] == 'GNV']
            df_tri_estado_anual_gnv.loc[: ,'VARIAÇÃO %'] = df_tri_estado_anual_gnv.groupby(['PRODUTO', 'ESTADO'])['PREÇO MÉDIO REVENDA'].pct_change() * 100
            df_tri_estado_anual_gnv.loc[:, 'DIFERENCA'] = df_tri_estado_anual_gnv['PREÇO MÉDIO REVENDA'].diff()

        with st.container(): # TEXTO 7 SESSÃO 4.2.4

            digitacao(f" \
            A variação percentual do preço médio de revenda do Etanol no {trimestre_atual} trimestre de {ano_max} \
            foi de {formatar_valor2(df_tri_estado_anual_etanol['VARIAÇÃO %'].values[-1])}. \
            \
            Já para a Gasolina Comum foi de {formatar_valor2(df_tri_estado_anual_gasolina['VARIAÇÃO %'].values[-1])}. \
            \
            Referente ao Óleo Diesel obteve uma variação de {formatar_valor2(df_tri_estado_anual_diesel['VARIAÇÃO %'].values[-1])}. \
            \
            Por fim, o GNV obteve uma variação de {formatar_valor2(df_tri_estado_anual_gnv['VARIAÇÃO %'].values[-1])}. ")

        with st.container():  # TEXTO 8 SESSÃO 4.2.4

            digitacao(f" \
            A variação percentual no preço médio de revenda do Etanol no {trimestre_atual.lower()} trimestre de {ano_max}, \
            comparado ao mesmo período de {ano_max - 1}, foi de {formatar_valor2(df_tri_estado_anual_etanol['VARIAÇÃO %'].values[-1])}, \
            refletindo uma mudança de {formatar_valor(df_tri_estado_anual_etanol['DIFERENCA'].values[-1])} no preço médio. \
            \
            A Gasolina Comum apresentou uma variação de {formatar_valor2(df_tri_estado_anual_gasolina['VARIAÇÃO %'].values[-1])}, \
            resultando em uma alteração de {formatar_valor(df_tri_estado_anual_gasolina['DIFERENCA'].values[-1])}. \
            \
            O Óleo Diesel teve uma variação de {df_tri_estado_anual_diesel['VARIAÇÃO %'].values[-1]:.2f}%, \
            correspondendo a uma mudança de {formatar_valor(df_tri_estado_anual_diesel['DIFERENCA'].values[-1])} no preço médio. \
            \
            Por fim, o GNV registrou uma variação de {formatar_valor2(df_tri_estado_anual_gnv['VARIAÇÃO %'].values[-1])}, \
            com uma alteração de {formatar_valor(df_tri_estado_anual_gnv['DIFERENCA'].values[-1])} no preço médio. ")


