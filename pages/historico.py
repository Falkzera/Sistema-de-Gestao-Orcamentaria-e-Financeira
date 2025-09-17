import streamlit as st

from src.base import func_load_base_cpof, func_load_base_credito_sop_geo, func_load_base_ted, func_load_base_sop_geral
from utils.ui.display import padrao_importacao_pagina, titulos_pagina, rodape_desenvolvedor, img_pag_icon
from src.salvar_historico import exibir_historico

st.set_page_config(page_title="SIGOF", page_icon=img_pag_icon(), layout="wide")

padrao_importacao_pagina()

titulos_pagina("Histórico Processual", font_size="1.9em", text_color="#3064AD", icon='<i class="fas fa-history"></i>' )

base_opcoes = ["Histórico CPOF", "Histórico Crédito SOP/GEO", "Histórico TED", "Histórico SOP/GERAL"]

historico_map = {
    "Base CPOF": "Histórico CPOF",
    "Base Crédito SOP/GEO": "Histórico Crédito SOP/GEO",
    "Base TED": "Histórico TED",
    "Base SOP/GERAL": "Histórico SOP/GERAL"
}

usuario = st.session_state.get("username", None)
bases_disponiveis = []
if usuario and "base_access" in st.secrets and usuario in st.secrets["base_access"]:
    for base in base_opcoes:
        if base in st.secrets["base_access"][usuario]:
            bases_disponiveis.append(base)

if not bases_disponiveis:
    st.warning("Você não tem acesso a nenhum histórico de processos.")
    st.stop()

if len(bases_disponiveis) == 1:
    base_escolhida = bases_disponiveis[0]
else:
    base_escolhida = st.selectbox("Escolha o tipo de histórico:", bases_disponiveis)

nome_base = historico_map.get(base_escolhida, base_escolhida)

if nome_base == "Histórico CPOF":
    df = func_load_base_cpof()
elif nome_base == "Histórico Crédito SOP/GEO":
    df = func_load_base_credito_sop_geo()
elif nome_base == "Histórico TED":
    df = func_load_base_ted()   
elif nome_base == "Histórico SOP/GERAL":
    df = func_load_base_sop_geral()
else:
    st.error("Base de histórico não reconhecida.")
    st.stop()

if "processos_filtrados" in st.session_state and not st.session_state.processos_filtrados.empty:
    processos_disponiveis = st.session_state.processos_filtrados["Processo ID"].tolist()
else:
    processos_disponiveis = df["Nº do Processo"].tolist() if "Nº do Processo" in df.columns else df["Processo ID"].tolist()

processos_unicos = list(dict.fromkeys(processos_disponiveis))
processo_edit = st.selectbox(
    "Selecione um processo para editar", 
    [""] + processos_unicos
)

if processo_edit:
    if "Nº do Processo" in df.columns:
        row_index = df[df["Nº do Processo"] == processo_edit].index[0]
    else:
        row_index = df[df["Processo ID"] == processo_edit].index[0]
    processo = df.loc[row_index]

with st.container(border=True): 
    if not processo_edit:
        st.info("⚠️ Selecione um processo para visualizar o histórico de modificações.")

    if processo_edit:
        exibir_historico(processo_edit, nome_base)


rodape_desenvolvedor()