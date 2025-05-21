import streamlit as st
from streamlit_tags import st_tags

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
