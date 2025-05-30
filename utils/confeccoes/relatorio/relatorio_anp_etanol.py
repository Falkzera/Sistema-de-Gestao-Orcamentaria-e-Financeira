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

def montar_relatorio_anp_etanol(df):

    with st.container():  # CARREGAMENTO DATASET

        def load_data():

            df = read_parquet_file_from_drive('anp_etanol.parquet')    

            return df
        
        df = load_data()

    with st.container(): # MANIPULAÇÃO DO DATASET

        df.loc[:, 'MÊS'] = df['MÊS'].replace({'JAN': 1, 'FEV': 2, 'MAR': 3, 'ABR': 4,'MAI': 5, 'JUN': 6, 'JUL': 7, 'AGO': 8, 'SET': 9, 'OUT': 10, 'NOV': 11, 'DEZ': 12})
        df.loc[:, 'MÊS'] = df['MÊS'].infer_objects(copy=False)
        df.loc[:, 'DATA'] = pd.to_datetime(df['ANO'].astype(str) + '-' + df['MÊS'].astype(str) + '-01')
        df = df.drop(columns=['ANO', 'MÊS'])
        df = df[['DATA', 'GRANDE REGIÃO', 'UNIDADE DA FEDERAÇÃO', 'PRODUTO', 'PRODUÇÃO']]
        
        df.loc[:, 'PRODUÇÃO'] = df['PRODUÇÃO'].str.replace(',', '.').astype(float)

        df = df.groupby(['DATA', 'GRANDE REGIÃO', 'UNIDADE DA FEDERAÇÃO', 'PRODUTO'])[['PRODUÇÃO']].sum().reset_index()

    with st.container(): # TODOS OS DF NECESSÁRIOS: AL, NE, REGIÃO

        df_anidro = df[(df['PRODUTO'] == 'ANIDRO')].copy()
        df_hidratado = df[(df['PRODUTO'] == 'HIDRATADO')].copy()

        df_al = df[(df['UNIDADE DA FEDERAÇÃO'] == 'ALAGOAS')].copy()
        df_al_anidro = df_anidro[(df_anidro['UNIDADE DA FEDERAÇÃO'] == 'ALAGOAS')].copy()
        df_al_hidratado = df_hidratado[(df_hidratado['UNIDADE DA FEDERAÇÃO'] == 'ALAGOAS')].copy()

        df_ne = df[(df['GRANDE REGIÃO'] == 'REGIÃO NORDESTE')].copy()
        df_ne_anidro = df_anidro[(df_anidro['GRANDE REGIÃO'] == 'REGIÃO NORDESTE')].copy()
        df_ne_hidratado = df_hidratado[(df_hidratado['GRANDE REGIÃO'] == 'REGIÃO NORDESTE')].copy()

        df_regioes = df.groupby(['GRANDE REGIÃO', 'PRODUTO'])[['PRODUÇÃO']].sum().reset_index()
        ano_max = df['DATA'].max().year
        produto = df['PRODUTO'].unique()[0]

    with st.container(): # CABEÇALHO 
        titulo_dinamico(f"# Produção de Etanol em Alagoas")

        digitacao(f" \
        Segundo a Agência Nacional do Petróleo, Gás Natural e Biocombustíveis (ANP), o etanol \
        é um biocombustível produzido a partir da fermentação de açúcares, no qual tem diversas utilizações a depender de sua composição. \
        Possuindo dois tipos de etanol, o etanol anidro e o hidratado, se diferem principalmente na quantidade de água presente em sua formação. \
        O etanol anidro tem a composição mais pura, possuindo uma quantidade de água inferior a 1%, tendo \
        sua principal utilização na fabricação de gasolina, onde é misturado à gasolina, até um limite de 27,5%, \
        com o intuito de aumentar sua octanagem, \
        que é a capacidade do combustível resistir a compressão dentro do motor,\
        visando aumentar sua eficiência e reduzir a emissão de gases poluentes.  \
        O etanol anidro também é utilizado na indústria, servindo como matéria prima para a formulação de tintas e solventes. \
        Já o etanol hidratado, possui em sua composição um teor maior de água, chegando a um máximo de 7,5% e tem sua utilização principal\
        como combustível para motores a combustão sendo uma alternativa sustentável à combustíveis fósseis. ")
        
        titulo_dinamico(f"## Série histórica da produção de etanol: {df['DATA'].min().year} - {df['DATA'].max().year}")

    with st.container(): # Análise série histórica

        digitacao(f" \
            O gráfico a seguir apresenta a série histórica da produção de etanol em Alagoas, abrangendo o período de \
            {df['DATA'].min().year} a {df['DATA'].max().year}. A evolução ao longo do tempo revela tendências importantes \
            dessa produção. \
            Durante esse intervalo, a produção de etanol atingiu seu pico máximo \
            em {maior_pico_producao(df_al)} m³. \
            Além disso, a produção apresentou uma média de {media_producao(df_al)} m³ ao longo dos anos.  \
            Também nota-se o comportamento cíclico da produção, demonstrando vales e picos de maneira intensa, alternando conforme o aumento e a diminuição da produção.\
           ")
        
        with st.container(): # Gráfico!

            # Agrupamento dos dados
            # Filtrar para os últimos 3 anos disponíveis
            ultimos_anos = sorted(df_al_anidro['DATA'].dt.year.unique())[-5:]
            # Filtra apenas os meses a partir de junho (6)
            df_data_al_anidro = df_al_anidro[
                (df_al_anidro['DATA'].dt.year.isin(ultimos_anos)) & (df_al_anidro['DATA'].dt.month >= 6)
            ].groupby('DATA')['PRODUÇÃO'].sum().reset_index()
            df_data_al_hidratado = df_al_hidratado[
                (df_al_hidratado['DATA'].dt.year.isin(ultimos_anos)) & (df_al_hidratado['DATA'].dt.month >= 6)
            ].groupby('DATA')['PRODUÇÃO'].sum().reset_index()

            # Divide a coluna PRODUÇÃO por 1000 para ambos os dataframes
            df_data_al_anidro['PRODUÇÃO'] = df_data_al_anidro['PRODUÇÃO'] / 1000
            df_data_al_hidratado['PRODUÇÃO'] = df_data_al_hidratado['PRODUÇÃO'] / 1000

            gerar_grafico_linha(
                x=[df_data_al_anidro['DATA'], df_data_al_hidratado['DATA']],
                y=[df_data_al_anidro['PRODUÇÃO'], df_data_al_hidratado['PRODUÇÃO']],
                titulo_pdf=f'Produção de Etanol em Alagoas - {df_al["DATA"].max().year}',
                nomes_series=["Produção de Etanol Anidro", "Produção de Etanol Hidratado"],
                cores=['#0b4754', '#54180b'],  # Escolha a cor desejada
                # cores=['#095AA2', '#FF5733'],  # Escolha a cor desejada
                empilhar=True,  # 🧠 Só ativa o empilhamento aqui!
            )

        with st.container(): # RANKING
            digitacao(f" \
            Abaixo podemos observar o ranking de produção de etanol por estados do nordeste de toda a série histórica. \
            ")

            ranking_ne = ranking_producao(df_ne)
            top_3_estados = ranking_ne.head(3)
            alagoas_rank = ranking_ne[ranking_ne['UNIDADE DA FEDERAÇÃO'] == 'ALAGOAS']

            # Construir o texto para os top 3 estados
            top_3_texto = "Os três estados com maior produção de etanol no Nordeste são, respectivamente: "
            for idx, row in top_3_estados.iterrows():
                top_3_texto += f"{row['UNIDADE DA FEDERAÇÃO'].title()} com uma produção de {(row['PRODUÇÃO'])} m³"
                if idx < len(top_3_estados) - 2:
                    top_3_texto += ", "
                elif idx == len(top_3_estados) - 2:
                    top_3_texto += " e "
                else:
                    top_3_texto += ". "

            # Verificar se Alagoas está no top 3
            if not alagoas_rank.empty and alagoas_rank.index[0] < 3:
                top_3_texto += f"Destaca-se que Alagoas está entre os três primeiros colocados, ocupando a posição {alagoas_rank.index[0] + 1}° com uma produção de {(alagoas_rank.iloc[0]['PRODUÇÃO'])} m³."
            else:
                # Adicionar informações sobre Alagoas se não estiver no top 3
                if not alagoas_rank.empty:
                    top_3_texto += f"Embora Alagoas não esteja entre os três primeiros colocados, ocupa a posição {alagoas_rank.index[0] + 1}°, com uma produção de {(alagoas_rank.iloc[0]['PRODUÇÃO'])} m³, evidenciando sua relevância na produção de etanol na região."

            # Exibir o texto gerado
            digitacao(top_3_texto)

            # destrinchar o ranking de produção com nome do estado, produção e posição em um texto de linguagem natural formal
            df_ne['UNIDADE DA FEDERAÇÃO'] = df_ne['UNIDADE DA FEDERAÇÃO'].str.title()
    
            mostrar_tabela_pdf(ranking_producao(df_ne), nome_tabela=f"Ranking de Produção de etanol - Nordeste")
            cores_1 = ["#0b4754", "#54180b", "#9a6233", "#ffdd63", "#3d3c2f", "#70402a", "#a16d2c", "#d9b245", "#c77c3a"]
            
            gerar_grafico_pizza(labels=df_ne['UNIDADE DA FEDERAÇÃO'], values=df_ne['PRODUÇÃO'], titulo_pdf=f'Produção de Etanol no Nordeste (m³) {ano_max}', cores=cores_1)

        with st.container(): # RANKING
            digitacao(f" \
            Já referente ao ranking de produção de etanol por regiões, com relação a toda a série histórica. \
            ")

            ranking_regioes = ranking_producao(df_regioes)
            top_3_regioes = ranking_regioes.head(3)
            nordeste_rank = ranking_regioes[ranking_regioes['GRANDE REGIÃO'] == 'REGIÃO NORDESTE']

            # Construir o texto para os top 3 estados
            top_3_texto = "As três regiões com maior produção de etanol são, respectivamente: "
            for idx, row in top_3_regioes.iterrows():
                top_3_texto += f"{row['GRANDE REGIÃO'].title()} com uma produção de {(row['PRODUÇÃO'])} m³"
                if idx < len(top_3_regioes) - 2:
                    top_3_texto += ", "
                elif idx == len(top_3_regioes) - 2:
                    top_3_texto += " e "
                else:
                    top_3_texto += ". "

            # Verificar se Alagoas está no top 3
            if not nordeste_rank.empty and nordeste_rank.index[0] < 3:
                top_3_texto += f"Destaca-se que Alagoas está entre os três primeiros colocados, ocupando a posição {nordeste_rank.index[0] + 1}° com uma produção de {(nordeste_rank.iloc[0]['PRODUÇÃO'])} m³."
            else:
                # Adicionar informações sobre Alagoas se não estiver no top 3
                if not nordeste_rank.empty:
                    top_3_texto += f"Embora a região nordeste não esteja entre os três primeiros colocados, ocupa a posição {nordeste_rank.index[0] + 1}°, com uma produção de {(nordeste_rank.iloc[0]['PRODUÇÃO'])} m³, evidenciando sua relevância na produção de etanol na região."
            digitacao(top_3_texto)

            df_regioes['GRANDE REGIÃO'] = df_regioes['GRANDE REGIÃO'].str.title()
            mostrar_tabela_pdf(ranking_producao(df_regioes), nome_tabela=f"Ranking de Produção de etanol - Regiões")
            gerar_grafico_pizza(labels=df_regioes['GRANDE REGIÃO'], values=df_regioes['PRODUÇÃO'], titulo_pdf=f'Produção de Etanol por Regiões (m³) {ano_max}', cores=cores_1)
    
##########################################################

    with st.container(): # ANO

        df = recorte_temporal_ano_passado(df)
        df_anidro = recorte_temporal_ano_passado(df_anidro)
        df_hidratado = recorte_temporal_ano_passado(df_hidratado)

        df_al = recorte_temporal_ano_passado(df_al)
        df_al_anidro = recorte_temporal_ano_passado(df_al_anidro)
        df_al_hidratado = recorte_temporal_ano_passado(df_al_hidratado)

        df_ne = recorte_temporal_ano_passado(df_ne)
        df_ne_anidro = recorte_temporal_ano_passado(df_ne_anidro)
        df_ne_hidratado = recorte_temporal_ano_passado(df_ne_hidratado)
        
        df_regioes = df.groupby(['GRANDE REGIÃO', 'PRODUTO'])[['PRODUÇÃO']].sum().reset_index()

        titulo_dinamico(f"## Análise da produção de etanol: {df['DATA'].max().year}")

        digitacao(f"Realizando o recorte referente ao ano de {df_al['DATA'].max().year}, \
        podemos observar a evolução da produção ao neste período. E com essas informações concluímos que a produção de etanol\
        atingiu o seu máximo {maior_pico_producao(df_al)} m³. \
       ")
        
        with st.container(): # Gráfico!

            df_data_al = df_al.groupby('DATA')['PRODUÇÃO'].sum().reset_index()

            # 🔧 Aqui: formata a coluna 'DATA' como rótulo categórico "Jan/2025"
            df_data_al['DATA_FORMATADA'] = df_data_al['DATA'].dt.strftime('%b/%Y').str.title()

            gerar_grafico_barra(
                x=df_data_al['DATA_FORMATADA'],  # ⬅️ Usa a coluna formatada aqui
                y=df_data_al['PRODUÇÃO'],
                titulo_pdf=f'Produção de etanol em Alagoas - {df_al["DATA"].max().year}',
                cores=['#0b4754', '#54180b'] * len(df_data_al),
                texto_formatado=df_data_al['PRODUÇÃO'].apply(formatar_valor_arredondado_sem_cifrao),
            )

            digitacao(f" \
            Abaixo podemos observar o ranking de produção de etanol por estado e por região. \
            ")

            # Destrinchar o ranking de produção com nome do estado, produção e posição em um texto de linguagem natural formal
            # Buscar sempre mencionar os top 3 estados primeiros. Se Alagoas estiver em um deles, informar com detalhes.
            # Caso contrário, informar os top 3 e posteriormente informar o ranking de Alagoas.

            ranking_ne = ranking_producao(df_ne)
            top_3_estados = ranking_ne.head(3)
            alagoas_rank = ranking_ne[ranking_ne['UNIDADE DA FEDERAÇÃO'] == 'Alagoas']

            # Construir o texto para os top 3 estados
            top_3_texto = "Os três estados com maior produção de etanol no Nordeste são, respectivamente: "
            for idx, row in top_3_estados.iterrows():
                top_3_texto += f"{row['UNIDADE DA FEDERAÇÃO']} com uma produção de {(row['PRODUÇÃO'])} m³"
                if idx < len(top_3_estados) - 2:
                    top_3_texto += ", "
                elif idx == len(top_3_estados) - 2:
                    top_3_texto += " e "
                else:
                    top_3_texto += ". "

            # Verificar se Alagoas está no top 3
            if not alagoas_rank.empty and alagoas_rank.index[0] < 3:
                top_3_texto += f"Destaca-se que Alagoas está entre os três primeiros colocados, ocupando a posição {alagoas_rank.index[0] + 1}° com uma produção de {(alagoas_rank.iloc[0]['PRODUÇÃO'])} m³."
            else:
                # Adicionar informações sobre Alagoas se não estiver no top 3
                if not alagoas_rank.empty:
                    top_3_texto += f"Embora Alagoas não esteja entre os três primeiros colocados, ocupa a posição {alagoas_rank.index[0] + 1}°, com uma produção de {(alagoas_rank.iloc[0]['PRODUÇÃO'])} m³, evidenciando sua relevância na produção de etanol na região."

            # Exibir o texto gerado
            digitacao(top_3_texto)

            df_ne['UNIDADE DA FEDERAÇÃO'] = df_ne['UNIDADE DA FEDERAÇÃO'].str.title()
            mostrar_tabela_pdf(ranking_producao(df_ne), nome_tabela=f"Ranking de Produção de etanol - Nordeste")
            
            df_ne['UNIDADE DA FEDERAÇÃO'] = df_ne['UNIDADE DA FEDERAÇÃO'].replace({'Paraiba': 'Paraíba'})
            gerar_grafico_pizza(labels=df_ne['UNIDADE DA FEDERAÇÃO'], values=df_ne['PRODUÇÃO'], titulo_pdf=f'Produção de etanol por Estados do Nordeste',
                                cores=cores_1)

        with st.container(): # RANKING REGIÕES
            ranking_regioes = ranking_producao(df_regioes)
            top_3_regioes = ranking_regioes.head(3)
            nordeste_rank = ranking_regioes[ranking_regioes['GRANDE REGIÃO'] == 'REGIÃO NORDESTE']

            # Construir o texto para os top 3 estados
            top_3_texto = "Já referente ao ranking por regiões, temos que as três regiões com maior produção de etanol são, respectivamente: "
            for idx, row in top_3_regioes.iterrows():
                top_3_texto += f"{row['GRANDE REGIÃO'].title()} com uma produção de {(row['PRODUÇÃO'])} m³"
                if idx < len(top_3_regioes) - 2:
                    top_3_texto += ", "
                elif idx == len(top_3_regioes) - 2:
                    top_3_texto += " e "
                else:
                    top_3_texto += ". "

            # Verificar se Alagoas está no top 3
            if not nordeste_rank.empty and nordeste_rank.index[0] < 3:
                top_3_texto += f"Destaca-se que a região nordeste está entre os três primeiros colocados, ocupando a posição {nordeste_rank.index[0] + 1}° com uma produção de {(nordeste_rank.iloc[0]['PRODUÇÃO'])} m³."
            else:
                # Adicionar informações sobre Alagoas se não estiver no top 3
                if not nordeste_rank.empty:
                    top_3_texto += f"Embora a região nordeste não esteja entre os três primeiros colocados, ocupa a posição {nordeste_rank.index[0] + 1}°, com uma produção de {(nordeste_rank.iloc[0]['PRODUÇÃO'])} m³, evidenciando sua relevância na produção de etanol na região."
            digitacao(top_3_texto)

            df_regioes['GRANDE REGIÃO'] = df_regioes['GRANDE REGIÃO'].str.title()
            mostrar_tabela_pdf(ranking_producao(df_regioes), nome_tabela=f"Ranking de Produção de etanol - Regiões")

            gerar_grafico_pizza(labels=df_regioes['GRANDE REGIÃO'], values=df_regioes['PRODUÇÃO'], titulo_pdf=f'Produção de etanol por Região', 
                              cores=cores_1)