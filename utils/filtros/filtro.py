import streamlit as st
import pandas as pd
from datetime import datetime

from utils.confeccoes.formatar import mes_por_extenso
from streamlit_tags import st_tags

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

def filtros_de_busca(df_filtrado):

    if 'palavras_chave' not in st.session_state:
        st.session_state.palavras_chave = [] 

    if 'deliberacao_selecionados' not in st.session_state:
        st.session_state.deliberacao_selecionados = ["TODOS"]

    # Detecta coluna de filtro principal
    coluna_filtro = None
    if "Deliberação" in df_filtrado.columns:
        coluna_filtro = "Deliberação"
    elif "Situação" in df_filtrado.columns:
        coluna_filtro = "Situação"
    else:
        st.warning("Não foi possível filtrar: coluna 'Deliberação' ou 'Situação' não encontrada.")
        return df_filtrado

    col1, col2, col3 = st.columns([2, 3, 1])

    with col1:
        try:
            opcoes_filtro = ["TODOS"] + sorted(list(df_filtrado[coluna_filtro].unique()))
            novas_opcoes = st.multiselect(
                f"Filtre por {coluna_filtro}",
                opcoes_filtro,
                default=st.session_state.deliberacao_selecionados,
                key=coluna_filtro,
                placeholder=f"Selecione a {coluna_filtro}",
            )
            if not novas_opcoes:
                novas_opcoes = ["TODOS"]
        except Exception as e:
            novas_opcoes = ["TODOS"]

    with col2:
        st.write("<style>div[data-baseweb='select'] { margin-top: 11px; }</style>", unsafe_allow_html=True)
        novas_palavras_chave = st_tags(
            label="",
            text='Filtre por palavra-chave',
            value=st.session_state.palavras_chave,
            maxtags=10,
            key='tags_busca',
        )

    with col3:
        st.markdown("<div style='margin-top: 35px;'>", unsafe_allow_html=True)
        modo_busca_ou = st.toggle("Modo 'E'", value=True)
        st.markdown("</div>", unsafe_allow_html=True)

    if novas_opcoes != st.session_state.deliberacao_selecionados or novas_palavras_chave != st.session_state.palavras_chave:
        st.session_state.deliberacao_selecionados = novas_opcoes
        st.session_state.palavras_chave = novas_palavras_chave

        if "processo_edit" in st.session_state:
            del st.session_state["processo_edit"]

        st.rerun()

    if "TODOS" not in st.session_state.deliberacao_selecionados:
        df_filtrado = df_filtrado[df_filtrado[coluna_filtro].isin(st.session_state.deliberacao_selecionados)]

    if st.session_state.palavras_chave:
        palavras_chave_lower = [p.lower() for p in st.session_state.palavras_chave]

        if modo_busca_ou:
            # Modo "OU"
            def contem_qualquer_palavra(row):
                return any(
                    any(p in str(cell).lower() for cell in row)
                    for p in palavras_chave_lower
                )
            df_filtrado = df_filtrado[df_filtrado.apply(contem_qualquer_palavra, axis=1)]
        else:
            # Modo "E"
            def contem_todas_palavras(row):
                return all(
                    any(p in str(cell).lower() for cell in row)
                    for p in palavras_chave_lower
                )
            df_filtrado = df_filtrado[df_filtrado.apply(contem_todas_palavras, axis=1)]

    st.write('---')

    return df_filtrado