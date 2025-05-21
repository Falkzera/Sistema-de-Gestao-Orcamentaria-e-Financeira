import streamlit as st

from utils.ui.display import padrao_importacao_pagina
from utils.auth.auth import carregar_base_por_usuario
from utils.ui.dataframe import mostrar_tabela
from src.salvar_alteracoes import salvar_modificacoes_selectbox_mae, inicializar_e_gerenciar_modificacoes

padrao_importacao_pagina()

# Controle do recarregamento forçado via session_state
if "forcar_recarregar" not in st.session_state:
    st.session_state["forcar_recarregar"] = True  # Primeira vez: força recarregar

def carregar_base_cache(titulo_selectbox, chave_selectbox):
    # Usa o valor atual do session_state para forcar_recarregar
    df, nome_base, nome_base_historica = carregar_base_por_usuario(
        titulo_selectbox=titulo_selectbox,
        chave_selectbox=chave_selectbox,
        forcar_recarregar=st.session_state["forcar_recarregar"]
    )
    # Após recarregar, sempre seta para False para evitar recarregamento contínuo
    st.session_state["forcar_recarregar"] = False
    return df, nome_base, nome_base_historica

df, nome_base, nome_base_historica = carregar_base_cache(
    titulo_selectbox="Selecione a base para análise:",
    chave_selectbox="base_analise"
)

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


# NÃO ESTÁ ATUALIZANDO O DATAFRAE APÓS O SAVE! 
# ESTÁ SALVANDO DE BOAS!