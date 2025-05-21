import streamlit as st
import pandas as pd

from utils.ui.display import padrao_importacao_pagina
from utils.auth.auth import carregar_base_por_usuario
from utils.ui.dataframe import mostrar_tabela
from src.salvar_alteracoes import salvar_modificacoes_selectbox_mae, inicializar_e_gerenciar_modificacoes
from utils.filtros.filtro import filtros_de_busca
import streamlit_nested_layout # NÃO PODE SER EXCLUÍDO, CASO CONTRÁRIO OCORRE ERRO DE IMPORTAÇÃO

padrao_importacao_pagina()

with st.container(): # Carregamento da base PRECISA VER UMA FORMA DE EVITAR O RECARREGAMENTO DA BASE CONSTANTEMENTE!
    df, nome_base, nome_base_historica = carregar_base_por_usuario() # Tempo de execução está obivamente atrlado a essa função aqui, depurar ela mais tarde
    df = filtros_de_busca(df)


with st.container(): # Exibição da Tabela
    df, selected_row = mostrar_tabela(
        df,
        editable_colunas_especiais=True,
        mostrar_na_tela=True,
        enable_click=True,
        nome_tabela=f"{nome_base}",
    )

    tem_modificacoes = inicializar_e_gerenciar_modificacoes(selected_row)

    if tem_modificacoes:
        if st.button("Salvar todas as alterações", type="primary"):
            salvar_modificacoes_selectbox_mae(nome_base_historica, nome_base, df)
            st.session_state["forcar_recarregar"] = True
            del st.session_state["forcar_recarregar"]
            st.rerun()

with st.container():
    from src.editar_processo_geral import editar_unico_processo
    editar_unico_processo(selected_row, nome_base, df)


with st.container():
    from utils.confeccoes.resumos import mostrar_resumos_por_permissao
    mostrar_resumos_por_permissao(df, nome_base)


