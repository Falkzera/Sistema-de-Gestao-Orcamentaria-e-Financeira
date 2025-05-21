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
    formatar_valor_usd,
    mes_por_extenso,
    por_extenso_reais

)
def montar_relatorio_sefaz_despesa(df):          

    with st.container(): # CARREGAMENTO DO DATASET
        df = read_parquet_file_from_drive('sefaz_despesa_completo.parquet')
        # st.write(df)

        with st.container(): #CONFIGURAÇÃO INICIAL -> SELECIONANDO AS UNIDADES ORÇAMENTÁRIAS PARA O RELATÓRIO.
            apenas_esses = ['SECRETARIA DE ESTADO DA EDUCACAO E DO ESPORTE', 'POLICIA MILITAR DO ESTADO DE ALAGOAS', 'POLICIA CIVIL DO ESTADO DE ALAGOAS', 'SECRETARIA DE ESTADO DE RESSOCIALIZACAO E INCLUSAO SOCIAL', 'SECRETARIA DE ESTADO DA INFRA-ESTRUTURA', 'DEPARTAM DE ESTRADAS DE RODAGEM DO EST DE AL', 'SECRETARIA DE ESTADO DA SAUDE', 'FUNDO ESTADUAL DE SAUDE', 'SECRETARIA DE ESTADO DA SEGURANCA PUBLICA', 'FUNDO ESPECIAL DE SEGURANCA PUBLICA DO ESTADO DE ALAGOAS']
            df = df[df['DESCRICAO_UG'].isin(apenas_esses)]
            df['DESCRICAO_UG'] = df['DESCRICAO_UG'].replace('FUNDO ESTADUAL DE SAUDE', 'SECRETARIA E FUNDO ESTADUAL DE SAUDE')
            df['DESCRICAO_UG'] = df['DESCRICAO_UG'].replace('SECRETARIA DE ESTADO DA SAUDE', 'SECRETARIA E FUNDO ESTADUAL DE SAUDE')
            df['DESCRICAO_UG'] = df['DESCRICAO_UG'].replace('FUNDO ESPECIAL DE SEGURANCA PUBLICA DO ESTADO DE ALAGOAS', 'SECRETARIA E FUNDO ESTADUAL DE SAUDE')
            df['DESCRICAO_UG'] = df['DESCRICAO_UG'].replace('SECRETARIA DE ESTADO DA SEGURANCA PUBLICA', 'SECRETARIA E FUNDO ESTADUAL DE SAUDE')

            df = df[['DATA', 'DESCRICAO_UG', 'FONTE_MAE', 'DESCRICAO_FONTE_MAE', 'DESCRICAO_NATUREZA3', 'DESCRICAO_NATUREZA6', 'VALOR_EMPENHADO', 'VALOR_LIQUIDADO', 'VALOR_PAGO']]

        todas_descricao_ug = df['DESCRICAO_UG'].unique()  # Lista de todas as UGs

        for descricao_ug in todas_descricao_ug:

            titulo_dinamico(f" ## {descricao_ug.title()}")
            df_filtrado = df.copy()  # Cópia do dataframe original
            df_filtrado = df_filtrado[df_filtrado['DESCRICAO_UG'] == descricao_ug]  # Filtrar pela UG
            # st.write(df_filtrado)

            ano_min = df_filtrado['DATA'].dt.year.min() # Primeiro ano da série histórica filtrado
            ano_max = df_filtrado['DATA'].dt.year.max() # Último ano da série histórica filtrado
            ano_anterior = ano_max - 1 # Ano anterior ao último ano da série histórica filtrado

            df_ug_selecionada = df_filtrado.copy()
            df_ug_selecionada = df_ug_selecionada[['DATA', 'VALOR_PAGO']]
            df_ug_selecionada = df_ug_selecionada.rename(columns={'VALOR_PAGO':'VALOR_PAGO_UG_SELECIONADA'})
            df_ug_selecionada = df_ug_selecionada.reset_index(drop=True)
            df_ug_selecionada = df_ug_selecionada.groupby('DATA').sum().reset_index()

            df_ug_todas = df.copy()
            df_ug_todas = df_ug_todas[['DATA', 'VALOR_PAGO']]
            df_ug_todas = df_ug_todas.rename(columns={'VALOR_PAGO':'VALOR_PAGO_TODAS_UG'})
            df_ug_todas = df_ug_todas.reset_index(drop=True)
            df_ug_todas = df_ug_todas.groupby('DATA').sum().reset_index()

            # Junção
            df_ug_selecionada_vs_todas_ug = pd.merge(df_ug_selecionada, df_ug_todas, on='DATA', how='inner')

            # Criação de coluna de participação
            df_ug_selecionada_vs_todas_ug['PARTICIPACAO'] = (df_ug_selecionada_vs_todas_ug['VALOR_PAGO_UG_SELECIONADA'] / df_ug_selecionada_vs_todas_ug['VALOR_PAGO_TODAS_UG']) * 100

            with st.container(): # TEXTO 1
                # st.write(df_ug_selecionada_vs_todas_ug)
                # st.write(df_ug_selecionada_vs_todas_ug.dtypes)

                digitacao(f"A seguir, é possível observar o nível da participação dos gastos da {descricao_ug.title()} nas despesas totais do Estado, \
                            sem deduções. \
                            De acordo com a série histórica dos gastos, que compreende desde \
                            {mes_por_extenso(df_ug_selecionada_vs_todas_ug[df_ug_selecionada_vs_todas_ug['DATA'].dt.year == ano_min]['DATA'].dt.month.min())} de {ano_min}, \
                            até {mes_por_extenso(df_ug_selecionada_vs_todas_ug[df_ug_selecionada_vs_todas_ug['DATA'].dt.year == ano_max]['DATA'].dt.month.max())} de {ano_max}, \
                            podemos observar que o nível médio dos direcionamentos ao órgão desde {ano_min} é de \
                            {formatar_valor2(df_ug_selecionada_vs_todas_ug['PARTICIPACAO'].mean())}, \
                            e em {ano_anterior} apresentou a média de \
                            {formatar_valor2(df_ug_selecionada_vs_todas_ug[df_ug_selecionada_vs_todas_ug['DATA'].dt.year == ano_anterior]['PARTICIPACAO'].mean())}. \
                            Em valores absolutos, essa média representa aproximadamente \
                            {formatar_valor(df_ug_selecionada_vs_todas_ug[df_ug_selecionada_vs_todas_ug['DATA'].dt.year == ano_anterior]['VALOR_PAGO_UG_SELECIONADA'].mean())} \
                            ({por_extenso_reais(df_ug_selecionada_vs_todas_ug[df_ug_selecionada_vs_todas_ug['DATA'].dt.year == ano_anterior]['VALOR_PAGO_UG_SELECIONADA'].mean())})\
                            despendidos por mês durante o referido ano.")

            with st.container(): # TABELA 1
                

                df_ug_selecionada_vs_todas_ug_tabela = df_ug_selecionada_vs_todas_ug.copy()
                df_ug_selecionada_vs_todas_ug_tabela['DATA'] = df_ug_selecionada_vs_todas_ug['DATA'].dt.to_period('M')
                df_ug_selecionada_vs_todas_ug_tabela = df_ug_selecionada_vs_todas_ug_tabela.rename(columns={'VALOR_PAGO_UG_SELECIONADA': f'VALOR PAGO {descricao_ug.title()}'})
                df_ug_selecionada_vs_todas_ug_tabela = df_ug_selecionada_vs_todas_ug_tabela.rename(columns={'VALOR_PAGO_TODAS_UG': 'VALOR PAGO TODAS UG'})
                df_ug_selecionada_vs_todas_ug_tabela[f'VALOR PAGO {descricao_ug.title()}'] = df_ug_selecionada_vs_todas_ug_tabela[f'VALOR PAGO {descricao_ug.title()}'].apply(formatar_valor)
                df_ug_selecionada_vs_todas_ug_tabela['VALOR PAGO TODAS UG'] = df_ug_selecionada_vs_todas_ug_tabela['VALOR PAGO TODAS UG'].apply(formatar_valor)
                df_ug_selecionada_vs_todas_ug_tabela['PARTICIPACAO'] = df_ug_selecionada_vs_todas_ug_tabela['PARTICIPACAO'].apply(formatar_valor2)
                df_ug_selecionada_vs_todas_ug_tabela = df_ug_selecionada_vs_todas_ug_tabela.rename(columns={'DATA': 'Data', f'VALOR PAGO {descricao_ug.title()}': f'Valor Pago {descricao_ug.title()}', 'VALOR PAGO TODAS UG': 'Valor Pago Todas UGs', 'PARTICIPACAO': 'Participação'})
                mostrar_tabela_pdf(df_ug_selecionada_vs_todas_ug_tabela, nome_tabela=f"Participação {descricao_ug.title()} na Despesa Estadual")

            with st.container(): # GRÁFICO 1 PARTICIPAÇÃO DA UG SELECIONADA NA DESPESA ESTADUAL

                gerar_grafico_linha(
                    x=df_ug_selecionada_vs_todas_ug['DATA'],
                    y=df_ug_selecionada_vs_todas_ug['PARTICIPACAO'],
                    titulo_pdf=f"Participação da {descricao_ug.title()} na Despesa Estadual",
                )

            with st.container(): # DEFINIÇÃO TRIMESTRAL 
                mes_atual_do_ano_atual = df_filtrado[df_filtrado['DATA'].dt.year == ano_max]['DATA'].dt.month.max() # Último mês do ano atual

                # Trimestre Anterior!
                def selecionar_trimestre_anterior(mes_atual_do_ano_atual, df=df_ug_selecionada_vs_todas_ug):
                    if 1 <= mes_atual_do_ano_atual <= 3:
                        trimestre_anterior = 'Quarto'
                        df_tri = df[(df['DATA'].dt.month > 9) & (df['DATA'].dt.month <= 12)]
                    elif 4 <= mes_atual_do_ano_atual <= 6:
                        trimestre_anterior = 'Primeiro'
                        df_tri = df[df['DATA'].dt.month <= 3]
                    elif 7 <= mes_atual_do_ano_atual <= 9:
                        trimestre_anterior = 'Segundo'
                        df_tri = df[(df['DATA'].dt.month > 3) & (df['DATA'].dt.month <= 6)]
                    else:
                        trimestre_anterior = 'Terceiro'
                        df_tri = df[(df['DATA'].dt.month > 6) & (df['DATA'].dt.month <= 9)]
                    return trimestre_anterior, df_tri

                trimestre_anterior, df_tri = selecionar_trimestre_anterior(mes_atual_do_ano_atual)

            with st.container(): # MÉTRICAS DE ANOS PARA DF_TRI -> Necessário, para não quebrar o código!!!!!
                ano_min = df_tri['DATA'].dt.year.min() # Primeiro ano da série histórica filtrado
                ano_max = df_tri['DATA'].dt.year.max() # Último ano da série histórica filtrado
                ano_anterior = ano_max - 1 # Ano anterior ao último ano da série histórica filtrado

            with st.container(): # TEXTO 2
            # TEXTO 2
                digitacao(f"Para o {trimestre_anterior.lower()} trimestre de {ano_max}, \
                        a média dos gastos foi de {formatar_valor2(df_tri[df_tri['DATA'].dt.year == ano_max]['PARTICIPACAO'].mean())}, \
                        representando um valor nominal médio de {formatar_valor(df_tri[df_tri['DATA'].dt.year == ano_max]['VALOR_PAGO_UG_SELECIONADA'].mean())} \
                        ({por_extenso_reais(df_tri[df_tri['DATA'].dt.year == ano_max]['VALOR_PAGO_UG_SELECIONADA'].mean())}) gastos no período. \
                        Comparado ao mesmo trimestre do ano anterior, houve uma variação percentual de \
                        {((df_tri[df_tri['DATA'].dt.year == ano_max]['VALOR_PAGO_UG_SELECIONADA'].mean() / df_tri[df_tri['DATA'].dt.year == ano_anterior]['VALOR_PAGO_UG_SELECIONADA'].mean()) -1)*100:.2f}%, \
                        dos gastos, que reflete um montante de um pouco mais de \
                        {formatar_valor((df_tri[df_tri['DATA'].dt.year == ano_max]['VALOR_PAGO_UG_SELECIONADA'].mean() - df_tri[df_tri['DATA'].dt.year == ano_anterior]['VALOR_PAGO_UG_SELECIONADA'].mean()))} para o período atual. \
                        ({por_extenso_reais((df_tri[df_tri['DATA'].dt.year == ano_max]['VALOR_PAGO_UG_SELECIONADA'].mean() - df_tri[df_tri['DATA'].dt.year == ano_anterior]['VALOR_PAGO_UG_SELECIONADA'].mean()))}) \
                        ")

            with st.container(): # TABELA 2

                # Personalização da tabela
                df_tri_tabela = df_tri.copy()
                df_tri_tabela['DATA'] = df_tri['DATA'].dt.to_period('M')
                df_tri_tabela = df_tri_tabela.rename(columns={'VALOR_PAGO_UG_SELECIONADA': f'VALOR PAGO {descricao_ug.title()}'})
                df_tri_tabela = df_tri_tabela.rename(columns={'VALOR_PAGO_TODAS_UG': 'VALOR PAGO TODAS UG'})
                df_tri_tabela[f'VALOR PAGO {descricao_ug.title()}'] = df_tri_tabela[f'VALOR PAGO {descricao_ug.title()}'].apply(formatar_valor)
                df_tri_tabela['VALOR PAGO TODAS UG'] = df_tri_tabela['VALOR PAGO TODAS UG'].apply(formatar_valor)
                df_tri_tabela['PARTICIPACAO'] = df_tri_tabela['PARTICIPACAO'].apply(formatar_valor2)
                # Renomear: DATA > Data, VALOR PAGO {descricao_ug.title()} > Valor Pago {descricao_ug.title()}; VALOR_PAGO_TODAS_UG > Valor Pago Todas UGs; PARTICIPAÇÃO -> Participação
                df_tri_tabela = df_tri_tabela.rename(columns={'DATA': 'Data', f'VALOR PAGO {descricao_ug.title()}': f'Valor Pago {descricao_ug.title()}', 'VALOR PAGO TODAS UG': 'Valor Pago Todas UGs', 'PARTICIPACAO': 'Participação'})
                mostrar_tabela_pdf(df_tri_tabela, nome_tabela=f"Participação {descricao_ug.title()} na Despesa Estadual - {trimestre_anterior} Trimestre de {ano_max}")

            with st.container(): # SESSÃO 2: SUBHEADER
                titulo_dinamico(f'### Detalhamento das Despesas Natureza 03: {descricao_ug.title()}')

            with st.container(): # CRIAÇÃO DO DATAFRAME DE COMPARAÇÃO/PARTICIPAÇÃO PERCENTUAL NA DESPESA

                df_tri_nat3 = df_filtrado.copy() # Cópia do dataframe
                df_tri_nat3 = df_tri_nat3[['DATA', 'DESCRICAO_NATUREZA3','VALOR_EMPENHADO']] # Selecionando as colunas
                df_tri_nat3 = df_tri_nat3.rename(columns={'VALOR_EMPENHADO':'VALOR_EMPENHADO_UG_SELECIONADA'}) # Renomeando a coluna
                df_tri_nat3 = df_tri_nat3.reset_index(drop=True) # Resetando o índice
                df_tri_nat3 = df_tri_nat3.groupby(['DATA', 'DESCRICAO_NATUREZA3']).sum().reset_index() # Agrupamento por natureza de despesa
                df_tri_nat3 = (selecionar_trimestre_anterior(mes_atual_do_ano_atual, df=df_tri_nat3))[1] # Filtrando o trimestre anterior
                df_tri_nat3 = df_tri_nat3.groupby([df_tri_nat3['DATA'].dt.year, 'DESCRICAO_NATUREZA3']).agg({'VALOR_EMPENHADO_UG_SELECIONADA': 'sum'}).reset_index() # Agrupamento por ano e natureza de despesa
                df_tri_nat3 = df_tri_nat3.pivot(index='DESCRICAO_NATUREZA3', columns='DATA', values='VALOR_EMPENHADO_UG_SELECIONADA').fillna(0) # Pivotando o dataframe
                df_tri_nat3.loc['TOTAL'] = df_tri_nat3.sum() # Adicionando uma linha de total para os dataframes

                # Resolveu um problema porém gerou outro
                for col in df_tri_nat3.columns: # Convertendo o novo df de percentagem para o formato de data
                    df_tri_nat3.columns = pd.to_datetime(df_tri_nat3.columns, format='%Y')
                    df_tri_nat3.columns = df_tri_nat3.columns.strftime('%Y')
                
                # Criação de tabela de variação entre anos: 2019 -> 2020; 2021 -> 2022; 2022 -> 2023; 2023 -> 2024. Baseado em df_tri_nat3
                df_tri_nat3_percent_variacao = pd.DataFrame()
                for year in range(ano_min, ano_max):
                    if f'{year}' in df_tri_nat3.columns and f'{year + 1}' in df_tri_nat3.columns:
                        df_tri_nat3_percent_variacao[f'{year} -> {year + 1}'] = ((df_tri_nat3[f'{year + 1}'] / df_tri_nat3[f'{year}']) - 1) * 100
                    else:
                        df_tri_nat3_percent_variacao[f'{year} -> {year + 1}'] = None
                
                # Concertando o problema que gerou!!!
                for col in df_tri_nat3.columns: # Convertendo coluna para o formato int32
                    df_tri_nat3.columns = df_tri_nat3.columns.astype('int32')

                df_tri_nat3_percent = pd.DataFrame()
                for year in range(ano_min, ano_max + 1):
                    df_tri_nat3_percent[f'{year}'] = (df_tri_nat3[year] / df_tri_nat3[year].sum()) * 2 * 100 # Não sei porque multiplica por 2, só sei que funciona

                # Participação global
                for col in df_tri_nat3_percent.columns: # Convertendo o novo df de percentagem para o formato de data
                    df_tri_nat3_percent.columns = pd.to_datetime(df_tri_nat3_percent.columns, format='%Y')
                    df_tri_nat3_percent.columns = df_tri_nat3_percent.columns.strftime('%Y')

                df_tri_nat3_percent['% TOTAL'] = df_tri_nat3_percent.mean(axis=1)

                # Adicionando uma linha de total para os dataframes
            
                df_tri_nat3_percent.loc['TOTAL'] = df_tri_nat3_percent.sum() / 2 # Devido a multiplicacao anterior, tem que dividr por 2,entao se arrumar lá emcima, lembrar de retirar a divisão por 2 :)
                #sort values mantendo total por ultimo

                df_tri_nat3_percent = df_tri_nat3_percent.sort_values(by='% TOTAL', ascending=False)

            with st.container(): # TEXTO 3
                digitacao(f"Podemos observar que há tendência à destinação predominante de recursos para a categoria  \
                            \"{df_tri_nat3_percent.index.values[1].lower()}\" a qual representa em média {df_tri_nat3_percent['% TOTAL'].values[1]:.2f}% das destinações totais, \
                            seguida por \"{df_tri_nat3_percent.index.values[2].lower()}\", \
                            a qual representa média de {df_tri_nat3_percent['% TOTAL'].values[2]:.2f}% das despesas do órgão. Acerca de \"{df_tri_nat3_percent.index.values[3].lower()}\" \
                            o empenho representou {df_tri_nat3_percent['% TOTAL'].values[3]:.2f}%")

                digitacao(f"Já para os anos de {ano_anterior} e {ano_max}, a tendência de despesa do órgão tem a seguinte configuração, \
                            considerando o recorte do {trimestre_anterior.lower()} trimestre para o ano de {ano_max}, tem-se a destinação de \
                            {df_tri_nat3_percent.iloc[1, -2]:.2f}% dos gastos do órgão para a categoria {df_tri_nat3_percent.index.values[1].lower()}, \
                            seguida de {df_tri_nat3_percent.iloc[2, -2]:.2f}% para as despesas com {df_tri_nat3_percent.index.values[2].lower()}, \
                            e {df_tri_nat3_percent.iloc[3, -2]:.2f}% para {df_tri_nat3_percent.index.values[3].lower()}. \
                            Quando referenciado ao período imediatamente anterior, é observado um total despendido durante o trimestre do ano corrente em \
                            {df_tri_nat3_percent_variacao[f'{year -1} -> {year}'].values[-1]:.2f}%. \
                        A análise estendida das variações percentuais para os demais anos está disponível no quadro a seguir:")

            with st.container(): # TABELA 3 - PARTICIPAÇÃO DA UG SELECIONADA NA DESPESA ESTADUAL POR NATUREZA DE DESPESA // PRECISA FORMATAR

                df_tri_nat3_percent_variacao_tabela = df_tri_nat3_percent_variacao.copy()
                df_tri_nat3_percent_variacao_tabela = df_tri_nat3_percent_variacao_tabela.map(formatar_valor2)
                mostrar_tabela_pdf(df_tri_nat3_percent_variacao_tabela, nome_tabela=f"Participação da {descricao_ug.title()} na Despesa Estadual por Natureza de Despesa - Valor Empenhado")
 
            with st.container(): # TEXTO 4
                variacao_percentual = df_tri_nat3_percent_variacao[f'{year - 1} -> {year}'].values[-1]
                montante_diferenca = df_tri_nat3.iloc[-1, -1] - df_tri_nat3.iloc[-1, -2]
                montante_formatado = formatar_valor(abs(montante_diferenca))  # Valor absoluto para exibição

                # Define o texto dinâmico em uma única linha
                texto_variacao = f"{'aumento' if variacao_percentual > 0 else 'redução' if variacao_percentual < 0 else 'nenhuma variação'} em {abs(variacao_percentual):.2f}%" if variacao_percentual != 0 else "nenhuma variação"
                texto_montante = f" {montante_formatado} {'a mais' if montante_diferenca > 0 else 'a menos' if montante_diferenca < 0 else 'do mesmo valor'}"

                # Renderiza o texto
                with st.container():  # TEXTO 4
                    digitacao(f"Ao tratar do empenho das despesas do órgão no mesmo recorte temporal, \
                                é possível observar os grupos de despesas que influenciaram {texto_variacao} \
                                para o ano de {ano_max}. Esta variação é reflexo de um montante de \
                                {texto_montante} em relação ao período anterior.")


            with st.container(): # TEXTO 5
                digitacao(f"Como observado anteriormente, as despesas do órgão estão divididas entre as categorias: \
                            \"{df_tri_nat3_percent.index.values[1].lower()}\", \"{df_tri_nat3_percent.index.values[2].lower()}\" e \"{df_tri_nat3_percent.index.values[3].lower()}\" \
                            e quando se trata dos valores empenhados, estes se dividem numa relação de {df_tri_nat3_percent.iloc[1, -2]:.2f}%, {df_tri_nat3_percent.iloc[2, -2]:.2f}% e {df_tri_nat3_percent.iloc[3, -2]:.2f}%  \
                            respectivamente, para o ano de {ano_max}.")

            with st.container(): # SESSÃO 3: SUBHEADER
                titulo_dinamico(f'### Detalhamento de Despesas Natureza 06: {descricao_ug.title()} ')

            with st.container(): # METRICAS DE NATUREZA 6 -> Tudo bagunçado :c
                
                # Trimestre Anterior!
                def selecionar_trimestre_anterior(df, mes_atual_do_ano_atual):
                    if 1 <= mes_atual_do_ano_atual <= 3:
                        trimestre_anterior = 'Quarto'
                        df_tri_ug_selecionada = df[(df['DATA'].dt.month > 9) & (df['DATA'].dt.month <= 12)]
                    elif 4 <= mes_atual_do_ano_atual <= 6:
                        trimestre_anterior = 'Primeiro'
                        df_tri_ug_selecionada = df[df['DATA'].dt.month <= 3]
                    elif 7 <= mes_atual_do_ano_atual <= 9:
                        trimestre_anterior = 'Segundo'
                        df_tri_ug_selecionada = df[(df['DATA'].dt.month > 3) & (df['DATA'].dt.month <= 6)]
                    else:
                        trimestre_anterior = 'Terceiro'
                        df_tri_ug_selecionada = df[(df['DATA'].dt.month > 6) & (df['DATA'].dt.month <= 9)]
                    
                    return trimestre_anterior, df_tri_ug_selecionada
                
                trimestre_anterior, df_tri_ug_selecionada,  = selecionar_trimestre_anterior(df_filtrado, mes_atual_do_ano_atual)

                valor_total_empenhado_por_outras_despesas_em_natureza3 = df_tri_ug_selecionada[df_tri_ug_selecionada['DESCRICAO_NATUREZA3'] == 'OUTRAS DESPESAS CORRENTES'][['DESCRICAO_NATUREZA6','VALOR_EMPENHADO']].groupby('DESCRICAO_NATUREZA6').sum().sort_values(by='VALOR_EMPENHADO', ascending=False)
                valor_total_empenhado_por_outras_despesas_em_natureza3['PORCENTAGEM'] = (valor_total_empenhado_por_outras_despesas_em_natureza3['VALOR_EMPENHADO'] / valor_total_empenhado_por_outras_despesas_em_natureza3['VALOR_EMPENHADO'].sum()) * 100
                # st.write(valor_total_empenhado_por_outras_despesas_em_natureza3)
                ranking_natureza6_1_lugar = valor_total_empenhado_por_outras_despesas_em_natureza3.index[0]
                ranking_natureza6_2_lugar = valor_total_empenhado_por_outras_despesas_em_natureza3.index[1]
                percent_ranking_natureza6_1_lugar = valor_total_empenhado_por_outras_despesas_em_natureza3['PORCENTAGEM'].iloc[0]
                percent_ranking_natureza6_2_lugar = valor_total_empenhado_por_outras_despesas_em_natureza3['PORCENTAGEM'].iloc[1]

                df_tri_ug_selecionada_ano_atual = df_tri_ug_selecionada[df_tri_ug_selecionada['DATA'].dt.year == ano_max]
                df_tri_ug_selecionada_ano_anterior = df_tri_ug_selecionada[df_tri_ug_selecionada['DATA'].dt.year == ano_anterior]

                # Filtrar e agregar os dados conforme necessário
                valor_total_empenhado_por_outras_despesas_em_natureza3_ano_atual = df_tri_ug_selecionada_ano_atual[df_tri_ug_selecionada_ano_atual['DESCRICAO_NATUREZA3'] == 'OUTRAS DESPESAS CORRENTES'][['DESCRICAO_NATUREZA6','VALOR_EMPENHADO']].groupby('DESCRICAO_NATUREZA6').sum().sort_values(by='VALOR_EMPENHADO', ascending=False)
                valor_total_empenhado_por_outras_despesas_em_natureza3_ano_anterior = df_tri_ug_selecionada_ano_anterior[df_tri_ug_selecionada_ano_anterior['DESCRICAO_NATUREZA3'] == 'OUTRAS DESPESAS CORRENTES'][['DESCRICAO_NATUREZA6','VALOR_EMPENHADO']].groupby('DESCRICAO_NATUREZA6').sum().sort_values(by='VALOR_EMPENHADO', ascending=False)

                # Calcular a porcentagem
                valor_total_empenhado_por_outras_despesas_em_natureza3_ano_atual['PORCENTAGEM'] = (valor_total_empenhado_por_outras_despesas_em_natureza3_ano_atual['VALOR_EMPENHADO'] / valor_total_empenhado_por_outras_despesas_em_natureza3_ano_atual['VALOR_EMPENHADO'].sum()) * 100
                # Obter os rankings e porcentagens
                # st.write(valor_total_empenhado_por_outras_despesas_em_natureza3_ano_atual)
                ranking_natureza6_1_lugar_ano_atual = valor_total_empenhado_por_outras_despesas_em_natureza3_ano_atual.index[0]
                ranking_natureza6_2_lugar_ano_atual = valor_total_empenhado_por_outras_despesas_em_natureza3_ano_atual.index[1]
                percent_ranking_natureza6_1_lugar_ano_atual = valor_total_empenhado_por_outras_despesas_em_natureza3_ano_atual['PORCENTAGEM'].iloc[0]
                percent_ranking_natureza6_2_lugar_ano_atual = valor_total_empenhado_por_outras_despesas_em_natureza3_ano_atual['PORCENTAGEM'].iloc[1]

                digitacao(f"A categoria de “custeio” representa uma quantidade considerável dos gastos do órgão. \
                                Nesta, a destinação mais representativa referente para toda série histórica trimestral são para \"{ranking_natureza6_1_lugar.lower()}\", \
                                que representam {percent_ranking_natureza6_1_lugar:.2f}% dos direcionamentos da categoria, \
                                juntamente com \"{ranking_natureza6_2_lugar.lower()}\" que representam {percent_ranking_natureza6_2_lugar:.2f}% dos gastos. \
                            Já referente ao {trimestre_anterior.lower()} trimestre de {ano_max}, a categoria de “custeio” \
                            apresentou uma destinação de {percent_ranking_natureza6_1_lugar_ano_atual:.2f}% para \"{ranking_natureza6_1_lugar_ano_atual.lower()}\" \
                            e {percent_ranking_natureza6_2_lugar_ano_atual:.2f}% para \"{ranking_natureza6_2_lugar_ano_atual.lower()}\".")

                                    # Concatenar valor_total_empenhado_por_outras_despesas_em_natureza3_ano_atual & valor_total_empenhado_por_outras_despesas_em_natureza3_ano_anterior
                valor_total_empenhado_comparacao = pd.concat(
                    [valor_total_empenhado_por_outras_despesas_em_natureza3_ano_anterior.rename(columns={'VALOR_EMPENHADO': f'VALOR_EMPENHADO_{ano_anterior}'}),
                        valor_total_empenhado_por_outras_despesas_em_natureza3_ano_atual.rename(columns={'VALOR_EMPENHADO': f'VALOR_EMPENHADO_{ano_max}'})],
                    axis=1
                ).fillna(0)

                valor_total_empenhado_comparacao['DIFERENCA'] = valor_total_empenhado_comparacao[f'VALOR_EMPENHADO_{ano_max}'] - valor_total_empenhado_comparacao[f'VALOR_EMPENHADO_{ano_anterior}']
                valor_total_empenhado_comparacao = valor_total_empenhado_comparacao.sort_values(by='DIFERENCA', ascending=False)
                ranking_natureza6_1_lugar_comparacao = valor_total_empenhado_comparacao.index[0]
                ranking_natureza6_2_lugar_comparacao = valor_total_empenhado_comparacao.index[1]
                ranking_natureza6_3_lugar_comparacao = valor_total_empenhado_comparacao.index[2]
                valor_ranking_natureza6_1_lugar_comparacao = valor_total_empenhado_comparacao['DIFERENCA'].iloc[0]
                valor_ranking_natureza6_2_lugar_comparacao = valor_total_empenhado_comparacao['DIFERENCA'].iloc[1]
                valor_ranking_natureza6_3_lugar_comparacao = valor_total_empenhado_comparacao['DIFERENCA'].iloc[2]
                
                # FAZER ESSE TEXTO
                digitacao(f"Sobre as maiores variações no período em relação ao mesmo trimestre do ano anterior, \
                    é possível observar que os maiores destaques dentre as categorias de despesas \
                    são: \"{ranking_natureza6_1_lugar_comparacao.lower()}\", com crescimento de {formatar_valor(valor_ranking_natureza6_1_lugar_comparacao)} ({por_extenso_reais(valor_ranking_natureza6_1_lugar_comparacao)}); \"{ranking_natureza6_2_lugar_comparacao.lower()}\", \
                    que representam um acréscimo de {formatar_valor(valor_ranking_natureza6_2_lugar_comparacao)} ({por_extenso_reais(valor_ranking_natureza6_2_lugar_comparacao)}); \
                    e \"{ranking_natureza6_3_lugar_comparacao.lower()}\", com aumento de {formatar_valor(valor_ranking_natureza6_3_lugar_comparacao)} ({por_extenso_reais(valor_ranking_natureza6_3_lugar_comparacao)}). \
                    ")

                valor_total_empenhado_comparacao.drop(columns=['PORCENTAGEM'], inplace=True)      
                valor_total_empenhado_por_fonte = df_tri_ug_selecionada_ano_atual[df_tri_ug_selecionada_ano_atual['DESCRICAO_NATUREZA3'] == 'OUTRAS DESPESAS CORRENTES'][['FONTE_MAE','DESCRICAO_FONTE_MAE','VALOR_EMPENHADO']].groupby(['FONTE_MAE', 'DESCRICAO_FONTE_MAE']).sum().sort_values(by='VALOR_EMPENHADO', ascending=False)
                valor_total_empenhado_por_fonte['PORCENTAGEM'] = (valor_total_empenhado_por_fonte['VALOR_EMPENHADO'] / valor_total_empenhado_por_fonte['VALOR_EMPENHADO'].sum()) * 100
                valor_total_empenhado_por_fonte = valor_total_empenhado_por_fonte.sort_values(by='VALOR_EMPENHADO', ascending=False)
                
                try:
                    ranking_fonte_1_lugar_comparacao = valor_total_empenhado_por_fonte.index[0][1]
                    ranking_fonte_2_lugar_comparacao = valor_total_empenhado_por_fonte.index[1][1]
                    valor_ranking_fonte_1_lugar_comparacao = valor_total_empenhado_por_fonte['PORCENTAGEM'].iloc[0]
                    valor_ranking_fonte_2_lugar_comparacao = valor_total_empenhado_por_fonte['PORCENTAGEM'].iloc[1]
                except IndexError:
                    ranking_fonte_2_lugar_comparacao = 0
                    valor_ranking_fonte_1_lugar_comparacao = 0
                    valor_ranking_fonte_2_lugar_comparacao = 0
                try:
                    # Função para formatar o valor com base no limite de milhões
                    valor_empenhado_1 = valor_total_empenhado_por_fonte['VALOR_EMPENHADO'].iloc[0]
                    valor_empenhado_2 = valor_total_empenhado_por_fonte['VALOR_EMPENHADO'].iloc[1]

                    digitacao(f"Logo abaixo, é possível observar o quadro com o detalhamento das despesas por fonte de recurso. \
                    Assim, é notável que a maior parte das despesas da {descricao_ug.title()} provêm de \"{ranking_fonte_1_lugar_comparacao.title()}\" \
                    no {trimestre_anterior.lower()} trimestre de {ano_max}, representando um total de {valor_ranking_fonte_1_lugar_comparacao:.2f}%, \
                    que corresponde a um total empenhado de {formatar_valor(valor_empenhado_1)} ({por_extenso_reais(valor_empenhado_1)}). Enquanto isso, a \"{ranking_fonte_2_lugar_comparacao.title()}\" \
                    representa {valor_ranking_fonte_2_lugar_comparacao:.2f}% do total empenhado no período, que corresponde a {formatar_valor(valor_empenhado_2)} ({por_extenso_reais(valor_empenhado_2)}). \
                    ")

                except IndexError:
                    valor_empenhado_1 = valor_total_empenhado_por_fonte['VALOR_EMPENHADO'].iloc[0]

                    digitacao(f"Logo abaixo, é possível observar o quadro com o detalhamento das despesas por fonte de recurso. \
                    Assim, é notável que a maior parte das despesas da {descricao_ug.title()} provêm de \"{ranking_fonte_1_lugar_comparacao.title()}\" \
                    no {trimestre_anterior.lower()} trimestre de {ano_max}, representando um total de {valor_ranking_fonte_1_lugar_comparacao:.2f}%, \
                    que corresponde a um total empenhado de {formatar_valor(valor_empenhado_1)} ({por_extenso_reais(valor_empenhado_1)}). \
                    ")

                valor_total_empenhado_por_fonte_com_natureza6 = df_tri_ug_selecionada_ano_atual[df_tri_ug_selecionada_ano_atual['DESCRICAO_NATUREZA3'] == 'OUTRAS DESPESAS CORRENTES'][['FONTE_MAE','DESCRICAO_NATUREZA6','VALOR_EMPENHADO']].groupby(['FONTE_MAE','DESCRICAO_NATUREZA6']).sum().sort_values(by='VALOR_EMPENHADO', ascending=False)
                valor_total_empenhado_por_fonte_com_natureza6['PORCENTAGEM'] = (valor_total_empenhado_por_fonte_com_natureza6['VALOR_EMPENHADO'] / valor_total_empenhado_por_fonte_com_natureza6['VALOR_EMPENHADO'].sum()) * 100
                valor_total_empenhado_por_fonte_com_natureza6['PORCENTAGEM'] = valor_total_empenhado_por_fonte_com_natureza6['PORCENTAGEM'].apply(formatar_valor2)
                valor_total_empenhado_por_fonte_com_natureza6['COLUNA_ADICIONAL'] = valor_total_empenhado_por_fonte_com_natureza6.index
                valor_total_empenhado_por_fonte_com_natureza6['Fonte Mãe'] = valor_total_empenhado_por_fonte_com_natureza6['COLUNA_ADICIONAL'].apply(lambda x: x[0])
                valor_total_empenhado_por_fonte_com_natureza6['Natureza 6'] = valor_total_empenhado_por_fonte_com_natureza6['COLUNA_ADICIONAL'].apply(lambda x: x[1])
                valor_total_empenhado_por_fonte_com_natureza6 = valor_total_empenhado_por_fonte_com_natureza6.rename(columns={'VALOR_EMPENHADO': 'Valor Empenhado', 'PORCENTAGEM': 'Percentual'})
                valor_total_empenhado_por_fonte_com_natureza6 = valor_total_empenhado_por_fonte_com_natureza6[['Fonte Mãe', 'Natureza 6', 'Valor Empenhado', 'Percentual', ]]
                valor_total_empenhado_por_fonte_com_natureza6['Valor Empenhado'] = valor_total_empenhado_por_fonte_com_natureza6['Valor Empenhado'].apply(formatar_valor)
                mostrar_tabela_pdf(valor_total_empenhado_por_fonte_com_natureza6, nome_tabela=f"Participação da {descricao_ug.title()} na Despesa Estadual por Fonte de Recurso")
