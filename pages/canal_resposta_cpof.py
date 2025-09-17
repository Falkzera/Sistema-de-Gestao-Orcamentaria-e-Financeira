import streamlit as st
import numpy as np

from src.base import func_load_base_cpof
from utils.ui.display import padrao_importacao_pagina, rodape_desenvolvedor, titulos_pagina, img_pag_icon
from utils.ui.dataframe import mostrar_tabela
from src.salvar_alteracoes import salvar_modificacoes_selectbox_mae, inicializar_e_gerenciar_modificacoes

st.set_page_config(page_title="SIGOF", page_icon=img_pag_icon(), layout="wide")
padrao_importacao_pagina()

titulos_pagina("Canal de Manifestação Técnica", font_size="1.9em", text_color="#3064AD", icon='<i class="fas fa-edit"></i>')

st.session_state.base_cpof = func_load_base_cpof(forcar_recarregar=True)

membros_cpof = ['SECRETÁRIA EXECUTIVA', 'SEPLAG', 'SEFAZ', 'GABINETE CIVIL', 'SEGOV']

usuario_logado = st.session_state.username.upper() 
if usuario_logado in membros_cpof:
    membro_atual = usuario_logado
    st.markdown(f"🔒 **Membro atual:** {membro_atual}")

else:
    membro_atual = st.selectbox("Selecione o membro", membros_cpof, key='membro', help="Escolha o membro para ver os processos pendentes.")

# Detalhamento: a variável "base_mostrar", é core central para identificar os processos que irão ser exibidos na tela dos membros do CPOF, por enquanto está sendo definida por "Disponível aos Membros CPOF", mas pode ser alterada para outros critérios, como "Em Análise" ou "Em Revisão".

base_mostrar = st.session_state.base_cpof[st.session_state.base_cpof['Deliberação'] == 'Disponível aos Membros CPOF']  # <<<<<<<<<<<

if "filtro_status" not in st.session_state:
    st.session_state.filtro_status = None

base_mostrar.loc[:, membro_atual] = base_mostrar[membro_atual].replace([False, '', ' ', None], np.nan)

aguardando_resposta_df = base_mostrar[base_mostrar[membro_atual].isna()]

respondidos_df = base_mostrar[base_mostrar[membro_atual].notna()]

aguardando_resposta = aguardando_resposta_df.shape[0]
respondidos = respondidos_df.shape[0]

indicadores_situacao = {
    "Processos Aguardando Resposta": aguardando_resposta,
    "Processos Respondidos": respondidos,
}

with st.container(): # Aqui o usuário irá alternar entre os processos respondidos e os que aguardam resposta
        
    col1, col2 = st.columns(2)
    with col1:
        if st.button(f"Processos Aguardando Resposta ({indicadores_situacao['Processos Aguardando Resposta']})", key="btn_aguardando", use_container_width=True, type="primary", help="Clique para ver os processos que aguardam sua manifestação técnica."):
            st.session_state.filtro_status = "Processos Aguardando Resposta"

    with col2:
        if st.button(f"Processos Respondidos ({indicadores_situacao['Processos Respondidos']})", key="btn_respondidos", use_container_width=True, type="primary", help="Clique para ver os processos que já foram respondidos."):
            st.session_state.filtro_status = "Processos Respondidos"

# with st.container(): # APÓS A SELEÇÃO DOS BOTÕES ACIMA

if st.session_state.filtro_status in ["Processos Aguardando Resposta", "Processos Respondidos"]:

    st.write('---')

    df = aguardando_resposta_df if st.session_state.filtro_status == "Processos Aguardando Resposta" else respondidos_df

    base_mostrar, selected_row = mostrar_tabela(df, editable_columns=[membro_atual], mostrar_na_tela=True, enable_click=True, nome_tabela=f"{st.session_state.filtro_status} ({len(df)}) - {membro_atual}")

    tem_modificacoes = inicializar_e_gerenciar_modificacoes(selected_row, escolha_coluna=membro_atual)

    if tem_modificacoes:
        
        if st.button("Clique para Salvar", type="primary", help="Clique aqui para salvar as modificações feitas na tabela atual."):
            salvar_modificacoes_selectbox_mae("Histórico CPOF", "Base CPOF", df, escolha_coluna=membro_atual)
            st.session_state["forcar_recarregar"] = True
            del st.session_state["forcar_recarregar"]
            st.rerun()


rodape_desenvolvedor()