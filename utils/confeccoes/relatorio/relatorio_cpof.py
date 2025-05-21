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
    mes_por_extenso,
    por_extenso,
    por_extenso_reais,
    gerar_relatorio_origem_recurso_com_graficos
)
from utils.limite.limite_credito import calcular_limite_credito_atual
from datetime import datetime


with st.container(): # CÁLCULO DO LIMITE (retirado de utils/calculo_limite/limite.py)
    limite = calcular_limite_credito_atual()
    VALOR_UTILIZADO_LIMITE = limite["valor_utilizado"]
    VALOR_DO_LIMITE = limite["valor_limite"]
    ORÇAMENTO_APROVADO_2025 = limite["orcamento_aprovado"]

with st.container():  # LIMPAR A SESSÃO PARA OS GRÁFICOS E TABELS

    # 🔁 Limpa conteúdo acumulado (se não estiver gerando PDF)
    if "conteudo_pdf" in st.session_state and not st.session_state.get("gerando_pdf", False):
        del st.session_state["conteudo_pdf"]

    # 🔁 Reseta contador de quadros e gráficos (sem depender de 'if')
    if not st.session_state.get("gerando_pdf", False):
        st.session_state["contador_quadro"] = 1
        st.session_state["contador_grafico"] = 1

with st.container():  # ALOCAÇÃO DO DATAFRAME
     from src.base import func_load_base_credito_sop_geo
     df = func_load_base_credito_sop_geo()

# 1️⃣ Filtro reutilizável de ano e mês
def filtro_ano_mes(df: pd.DataFrame, exibir_na_tela=True, key_prefix="filtro"):
    hoje = datetime.today()
    mes_padrao = hoje.month - 1 if hoje.month > 1 else 12
    ano_padrao = hoje.year if hoje.month > 1 else hoje.year - 1

    df['Data de Recebimento'] = pd.to_datetime(df['Data de Recebimento'], format='%d/%m/%Y')
    df['Ano'] = df['Data de Recebimento'].dt.year
    df['Mês'] = df['Data de Recebimento'].dt.month

    anos_disponiveis = sorted(df['Ano'].unique())
    meses_disponiveis = sorted(df['Mês'].unique())

    if exibir_na_tela:
        col1, col2 = st.columns(2)
        ano = col1.selectbox(
            "Selecione o Ano",
            anos_disponiveis,
            index=anos_disponiveis.index(ano_padrao),
            key=f"{key_prefix}_ano"
        )
        mes = col2.selectbox(
            "Selecione o Mês",
            meses_disponiveis,
            index=meses_disponiveis.index(mes_padrao),
            key=f"{key_prefix}_mes",
            format_func=mes_por_extenso
        )
    else:
        ano = st.session_state.get(f"{key_prefix}_ano", ano_padrao)
        mes = st.session_state.get(f"{key_prefix}_mes", mes_padrao)

    df_filtrado = df[(df['Ano'] == ano) & (df['Mês'] == mes)].copy()
    df_mes_anterior = df[
        (df['Ano'] == (ano if mes > 1 else ano - 1)) &
        (df['Mês'] == (mes - 1 if mes > 1 else 12))
    ].copy()

    return ano, mes, df_filtrado, df_mes_anterior

ano, mes, df_filtrado, df_filtrado_mes_anterior = filtro_ano_mes(df, exibir_na_tela=False, key_prefix="home")

with st.container():  # CONSTRUÇÃO DE MÉTRICAS INICIAIS

    QUANTIDADE_DE_PROCESSOS = df_filtrado.shape[0]
    mes_anterior = df_filtrado_mes_anterior['Mês'].unique()[0] if not df_filtrado_mes_anterior.empty else None

def montar_relatorio_cpof(ano, mes, df_filtrado, df_filtrado_mes_anterior):

    titulo_dinamico(f"# Relatório de {mes_por_extenso(mes)} / {ano}")

    with st.container():  # 1 - INTRODUÇÃO
            
        titulo_dinamico(f"## 1 - Introdução")

        digitacao(
            '''O orçamento é um produto do Sistema de Planejamento, que determina as ações que serão 
            desenvolvidas em um determinado exercício. Ele abrange a manutenção das atividades do Estado, 
            o planejamento e a execução dos projetos estabelecidos nos planos e programas de Governo.'''
        )

        digitacao(
            '''Durante a implementação dos programas de trabalho, podem ocorrer situações ou fatos novos
            que não foram previstos na fase de elaboração da peça orçamentária e que exigem a atuação do
            Poder Público. Desta forma, os créditos adicionais constituem-se em procedimentos previstos
            na Constituição Federal e na Lei 4.320/64 para corrigir ou amenizar situações que surgem
            durante a execução orçamentária, por razões de fatos de ordem econômica ou imprevisíveis.'''
        )

        digitacao(
            f'''Este relatório tem por objetivo compreender as alterações orçamentárias realizadas pelos
            órgãos do Poder Executivo, com base na Lei 4.320/64, Lei N° 9.454/2025 e Decreto Nº 100.553/2025. 
            Os dados abaixo são referentes aos processos de solicitações de créditos adicionais abertos por cada
            órgão do estado no período de {mes_por_extenso(mes)} de {ano}. Nesse relatório também foram incluídas
            informações sobre as Emendas Parlamentares Impositivas, além da atualização do Limite de Crédito.'''
        )

        qtd_processos = df_filtrado.shape[0]
        qtd_processos_sem_cobertura = df_filtrado[df_filtrado['Origem de Recursos'].str.startswith('Sem Cobertura')].shape[0]

        qtd_processos_com_cobertura = df_filtrado[~df_filtrado['Origem de Recursos'].str.startswith('Sem Cobertura')].shape[0]

        digitacao(
            f'''No mês de {mes_por_extenso(mes)} foram solicitados {qtd_processos} ({por_extenso(qtd_processos)}) processos de créditos
            adicionais, destes sendo, {qtd_processos_com_cobertura} ({por_extenso(qtd_processos_com_cobertura)}) com cobertura e {qtd_processos_sem_cobertura} ({por_extenso(qtd_processos_sem_cobertura)}) sem cobertura
            orçamentária. Contidas nestes processos, as solicitações de crédito se dividem conforme o gráfico
            abaixo:'''
        )

        gerar_grafico_pizza(
            labels=["Com Cobertura", "Sem Cobertura"],
            values=[qtd_processos_com_cobertura, qtd_processos_sem_cobertura],
            cores=["#095AA2", "#E0E0E0"],
            titulo_pdf="Distribuição por Tipo de Solicitação de Crédito"
        )

        qtd_processos_valores = df_filtrado['Valor'].sum()
        qtd_processos_valores_mes_anterior = df_filtrado_mes_anterior['Valor'].sum()
        diferenca = qtd_processos_valores - qtd_processos_valores_mes_anterior
        maior_que_atual = qtd_processos_valores - qtd_processos_valores_mes_anterior

        digitacao(
            f'''Estes créditos adicionais, compõem o valor total solicitado de {formatar_valor(qtd_processos_valores)} ({por_extenso_reais(qtd_processos_valores)}). 
            Uma diferença de {formatar_valor(abs(diferenca))} ({por_extenso_reais(abs(diferenca))})
            {'a mais' if maior_que_atual > 0 else 'a menos'}, em relação ao mês anterior de {mes_por_extenso(mes_anterior)}, a qual
            teve um total de solicitações de {formatar_valor(qtd_processos_valores_mes_anterior)} ({por_extenso_reais(qtd_processos_valores_mes_anterior)}).'''
        )

    with st.container():  # 2 - CRÉDITOS ADICIONAIS
            
        titulo_dinamico(f"## 2 - Créditos Adicionais")
        digitacao(
            f'''A abertura de um crédito adicional é formalizada por um Decreto do Executivo, porém,
            depende de prévia autorização legislativa (Lei Federal nº 4.320/64, art. 42).
            Esta seção é dedicada a análise descritiva e estatística dos processos de créditos adicionais
            que passaram por esta gerência de execução orçamentária durante o mês de {mes_por_extenso(mes)} de {ano}.
            Para este fim, serão utilizados os dados referentes aos processos de solicitação de alteração
            orçamentária advindos do SEI e do SIAFE, sendo estes dados tabulados de forma estruturada e
            tratada para as análises.'''
        )
        titulo_dinamico(f"### 2.1 - Créditos Especiais")

        digitacao(
            '''De acordo com o do Art. 41, inciso II, e Art. 42 da Lei Nº4.320, de 1964, são aqueles destinados
            às despesas que não foram previstas na Lei Orçamentária Anual - LOA, e para a qual não existe
            dotação orçamentária específica. De modo, que sua abertura se faz por meio de decreto do executivo,
            mas sua autorização se dá através de Lei específica, diferente dos créditos suplementares que são
            previstos na LOA e abertos por decretos executivos.
            Assim, não há uma dotação que se pretende reforçar, mas sim a criação de despesa. É o caso,
            por exemplo, da criação de uma ação por um Órgão cuja dotação não estava prevista no texto da LOA.'''
        )

        if df_filtrado[df_filtrado['Tipo de Crédito'] == 'Especial'].shape[0] == 0:
            digitacao(
                f'''No mês de {mes_por_extenso(mes)}, não houve solicitação de nenhum crédito especial.'''
            )
        else:
            digitacao(
                '''Os créditos especiais são aqueles destinados a despesas que não foram previstas na Lei Orçamentária
                Anual - LOA, e para a qual não existe dotação orçamentária específica. De modo, que sua abertura se faz
                por meio de decreto do executivo, mas sua autorização se dá através de Lei específica, diferente dos
                créditos suplementares que são previstos na LOA e abertos por decretos executivos. Assim, não há uma
                dotação que se pretende reforçar, mas sim a criação de despesa. É o caso, por exemplo, da criação de
                uma ação por um Órgão cuja dotação não estava prevista no texto da LOA.'''
            )

            orgaos_creditos_especiais = df_filtrado[df_filtrado['Tipo de Crédito'] == 'Especial'].groupby('Órgão (UO)').size()

            for orgao, qtd in orgaos_creditos_especiais.items():
                valor_total = df_filtrado[(df_filtrado['Tipo de Crédito'] == 'Especial') & (df_filtrado['Órgão (UO)'] == orgao)]['Valor'].sum()
                objetivos = df_filtrado[(df_filtrado['Tipo de Crédito'] == 'Especial') & (df_filtrado['Órgão (UO)'] == orgao)]['Objetivo'].unique()
                objetivos_texto = ', '.join(objetivos)
                
                numeros_processos = df_filtrado[(df_filtrado['Tipo de Crédito'] == 'Especial') & (df_filtrado['Órgão (UO)'] == orgao)]['Nº do Processo'].unique()
                numeros_processos_texto = ', '.join(map(str, numeros_processos)) 
                
            digitacao(
                f'''No mês de {mes_por_extenso(mes)}, o órgão {orgao} solicitou {qtd} ({por_extenso(qtd)}) processos de créditos especiais, 
                totalizando {formatar_valor(valor_total)} ({por_extenso_reais(valor_total)}). 
                Os números dos processos solicitados são: {numeros_processos_texto}. 
                Os objetivos associados a esses processos foram: "{objetivos_texto}".'''
            )

    with st.container():  # 2.2 - CRÉDITOS SUPLEMENTARES
            
        titulo_dinamico(f"### 2.2 - Créditos Suplementares")

        digitacao(
            '''No caso de créditos suplementares, a Constituição Federal, no § 8° do art. 165, permite que
            esta autorização possa constar da própria lei orçamentária. Com apoio nesta permissão
            constitucional, as leis orçamentárias do Estado trazem expressamente a autorização para abertura de
            créditos suplementares sob certas condições e limites, e os decretos estaduais, que estabelecem as
            normas para a programação e execução orçamentária e financeira em cada exercício, determinam os
            procedimentos complementares.'''
        )

        # qtd_processos_sem_cobertura = df_filtrado[df_filtrado['Origem de Recursos'].str.startswith('Sem Cobertura')].shape[0]
        qtd_processos_credito_suplementar = df_filtrado[df_filtrado['Tipo de Crédito'] == 'Suplementar'].shape[0]
        qtd_processos_credito_suplementar_valores = df_filtrado[df_filtrado['Tipo de Crédito'] == 'Suplementar']['Valor'].sum()
        digitacao(
            f'''Durante o mês de {mes_por_extenso(mes)} do exercício orçamentário de {ano}, foram solicitados um total de
            {qtd_processos_credito_suplementar} ({por_extenso(qtd_processos_credito_suplementar)}), totalizando uma quantia de {formatar_valor(qtd_processos_credito_suplementar_valores)} ({por_extenso_reais(qtd_processos_credito_suplementar_valores)}), de
            créditos suplementares, presentes no quadro abaixo.'''
        )

        # Ordenação por Valor (decrescente) e Órgão (crescente)
        df_filtrado_tabela = df_filtrado[df_filtrado['Tipo de Crédito'] == 'Suplementar'][['Órgão (UO)', 'Nº do Processo', 'Fonte de Recursos', 'Grupo de Despesas', 'Valor']] \
            .sort_values(by=['Órgão (UO)', 'Valor'], ascending=[False, False]).copy()

        # Formata os valores após ordenação
        df_filtrado_tabela['Valor'] = df_filtrado_tabela['Valor'].apply(formatar_valor)

        mostrar_tabela_pdf(
            df_filtrado_tabela,
            nome_tabela='Processos de Créditos Suplementares'
        )

    with st.container():  # 2.1.1.1 - ORIGEM DE RECURSOS E SEUS DIVERSOS TIPOS DE CPREDITO -> FUNÇÃO: gerar_relatorio_origem_recurso_com_graficos

        titulo_dinamico(f"#### 2.1.1 - Origem de recursos")

        titulo_dinamico(f"##### 2.1.1.1 - Sem cobertura")
        gerar_relatorio_origem_recurso_com_graficos(df_filtrado, 'Sem Cobertura', n=3, tipo_grafico='barra')

        titulo_dinamico(f"##### 2.1.1.2 - Superávit Financeiro")
        gerar_relatorio_origem_recurso_com_graficos(df_filtrado, 'Superávit Financeiro', n=3, tipo_grafico='barra')

        titulo_dinamico(f"##### 2.1.1.3 - Redução/Anulação")
        gerar_relatorio_origem_recurso_com_graficos(df_filtrado, 'Redução/Anulação', n=3, tipo_grafico='barra')

        titulo_dinamico(f"##### 2.1.1.4 - Excesso de Arrecadação e Superávit Financeiro")
        gerar_relatorio_origem_recurso_com_graficos(df_filtrado, 'Excesso de Arrecadação e Superávit Financeiro', n=3)

    with st.container():  # 3 - GRUPO DE DESPESAS

        titulo_dinamico(f"## 3 - Grupo de Despesas")

        nomes_despesas = {
            '1': '1 - Pessoal e Encargos Sociais',
            '2': '2 - Juros e Encargos da Dívida',
            '3': '3 - Outras Despesas Correntes',
            '4': '4 - Investimentos',
            '5': '5 - Inversões Financeiras',
            '6': '6 - Outras Despesas de Capital',
            '3 e 4': '3 e 4 - Outras Despesas e Investimentos'}

        grupo_despesa = df_filtrado.groupby('Grupo de Despesas')['Valor'].sum().reset_index()
        total_valor = grupo_despesa['Valor'].sum()
        grupo_despesa['Percentual'] = (grupo_despesa['Valor'] / total_valor) * 100
        grupo_despesa = grupo_despesa.sort_values(by='Valor', ascending=False).reset_index(drop=True)
        grupo_despesa['Grupo de Despesas'] = grupo_despesa['Grupo de Despesas'].map(nomes_despesas)
        texto_dinamico = f"Em análise às solicitações realizadas no mês de {mes_por_extenso(mes)}, constatou-se que "

        for idx, row in grupo_despesa.iterrows():
            grupo = row['Grupo de Despesas']
            percentual = row['Percentual']
            if idx == 0:
                texto_dinamico += f"a maior parte dos créditos foi destinada ao grupo de despesa {grupo}, que concentrou {formatar_valor2(percentual)} do total"
            elif idx == len(grupo_despesa) - 1:
                texto_dinamico += f", e o grupo {grupo} contribuiu com {formatar_valor2(percentual)} dos valores."
            else:
                texto_dinamico += f", seguido pelo grupo {grupo}, com {formatar_valor2(percentual)}"

        digitacao(texto_dinamico)

        cores_customizadas = ["#095AA2", "#E0E0E0", "#FFC300", "#FF5733", "#C70039"]

        gerar_grafico_pizza(
            labels=grupo_despesa['Grupo de Despesas'],
            values=grupo_despesa['Valor'],
            titulo_pdf=f"Gráfico: Distribuição por Grupo de Despesas ({mes_por_extenso(mes)})",
            cores=cores_customizadas
        )

    with st.container():  # 4 - CRÉDITOS PUBLICADOS
            
        titulo_dinamico(f"## 4 - Créditos Públicados")

        df['Data de Publicação'] = pd.to_datetime(df['Data de Publicação'], format='%d/%m/%Y', errors='coerce')
        df_publicados = df[
            (df['Situação'] == 'Publicado') &
            (df['Data de Publicação'].dt.year == ano) &
            (df['Data de Publicação'].dt.month == mes)
        ]

        df_publicados.reset_index(drop=True, inplace=True)
        qtd_publicados = df_publicados.shape[0]
        qtd_publicados_valores = df_publicados['Valor'].sum()
        df_tabela_publicados = df_publicados[['Órgão (UO)', 'Nº do Processo', 'Fonte de Recursos' , 'Valor', ]]
        df_tabela_publicados['Valor'] = df_tabela_publicados['Valor'].apply(formatar_valor)


        digitacao(
            f'''Foram publicados {qtd_publicados} ({por_extenso(qtd_publicados)}) créditos, 
            somando um valor de {formatar_valor(qtd_publicados_valores)} ({por_extenso_reais(qtd_publicados_valores)}, no mês de
            {mes_por_extenso(mes)} de {ano}.'''
                )

        mostrar_tabela_pdf(df_tabela_publicados, nome_tabela='Processos Publicados')

    with st.container():  # 5 - LIMITE DE CRÉDITO
            
        titulo_dinamico(f"## 5 - Limite de Crédito")

        digitacao(
            '''Após todo o exposto, vale ressaltar que dispomos de um limite de 10% (dez por cento) do
            total da despesa fixada na LOA, para abertura de créditos suplementares, conforme o Lei Estadual nº
            9.454 de 3 de janeiro de 2025:'''
        )

        digitacao(
        '''"Fica o Poder Executivo autorizado a abrir ao Orçamento Fiscal e da Seguridade Social, durante o
            exercício, créditos suplementares, até o limite de 10% (dez por cento) do total da despesa fixada
            no art. 4º desta Lei, em cumprimento ao disposto nos incisos V e VI do art. 178 da Constituição
            Estadual e nos arts. 7º e 43 da Lei Federal nº 4.320, de 1964, sendo vedada, no entanto, a
            utilização desta autorização para abrir créditos suplementares ao Poder Judiciário, Ministério
            Público, Defensoria Pública e Tribunal de Contas e anulações total ou parcial dos recursos
            destinados às emendas individuais impositivas."'''
                )

        digitacao(
        f'''Deste modo, sendo o total da despesa fixada na LOA, {formatar_valor(ORÇAMENTO_APROVADO_2025)} 
        ({por_extenso_reais(ORÇAMENTO_APROVADO_2025)}), tem-se que o montante disponível a abertura de créditos suplementares consiste no valor de
            {formatar_valor(VALOR_DO_LIMITE)} ({por_extenso_reais(VALOR_DO_LIMITE)}).'''
        )

        df_calculo_limite_mes_corrente = df[
            (df['Situação'] == 'Publicado') &
            (df['Data de Publicação'].dt.year == ano) &
            (df['Data de Publicação'].dt.month <= mes)
        ]

        valor_utilizado_limite = df_calculo_limite_mes_corrente['Valor'].sum()
        valor_limite_sobre_usado = (valor_utilizado_limite / VALOR_DO_LIMITE) * 100

        gerar_grafico_pizza(
            labels=["Executado", "Disponível"],
            values=[valor_limite_sobre_usado, 100 - valor_limite_sobre_usado],
            titulo_pdf="Limite Utilizado",
            cores=["#095AA2", "#E0E0E0"]
        )

        # fazer um dataframe com 4 colunas: ORÇAMENTO APROVADO 2025, VALOR DO LIMITE, VALOR UTILIZADO
        df_limite = pd.DataFrame({
            'Orçamento Aprovado 2025': [formatar_valor(ORÇAMENTO_APROVADO_2025)],
            'Valor do Limite (10%)': [formatar_valor(VALOR_DO_LIMITE)],
            'Valor Utilizado': [formatar_valor(valor_utilizado_limite)],
            'Disponível': [formatar_valor(VALOR_DO_LIMITE - valor_utilizado_limite)]
        })
        mostrar_tabela_pdf(df_limite, nome_tabela='Limite de Crédito')