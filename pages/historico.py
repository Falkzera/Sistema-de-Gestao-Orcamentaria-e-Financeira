import streamlit as st
import pandas as pd

from utils.ui.display import padrao_importacao_pagina
from utils.auth.auth import carregar_base_por_usuario
from src.salvar_historico import exibir_historico

padrao_importacao_pagina()

df, nome_base, nome_base_historica = carregar_base_por_usuario() # Tempo de execução está obivamente atrlado a essa função aqui, depurar ela mais tarde


# Verificar se há processos filtrados na sessão
if "processos_filtrados" in st.session_state and not st.session_state.processos_filtrados.empty:
    processos_disponiveis = st.session_state.processos_filtrados["Processo ID"].tolist()
else:
    processos_disponiveis = df["Processo ID"].tolist()

processos_unicos = list(dict.fromkeys(processos_disponiveis))  # Remove duplicatas mantendo a ordem
processo_edit = st.selectbox(
    "Selecione um processo para editar", 
    [""] + processos_unicos
)

if processo_edit:
    row_index = df[df["Processo ID"] == processo_edit].index[0]
    processo = df.loc[row_index]     

with st.container(border=True): 
    st.subheader("Histórico de Modificações")
    if not processo_edit:
        st.info("⚠️ Selecione um processo para visualizar o histórico de modificações.")

    if processo_edit:

        # if pd.notna(processo["Cadastrado Por"]):
            # st.markdown(f"```plaintext\nProcesso cadastrado por: {processo['Cadastrado Por']}\n```")
        exibir_historico(processo_edit, nome_base) # Exibe o histórico de modificações do processo editado
