import streamlit as st

from utils.ui.display import padrao_importacao_pagina
from utils.ui.dataframe import mostrar_tabela
from utils.ui.display import titulos_pagina
from src.base import func_load_base_cpof
from src.salvar_alteracoes import salvar_modificacoes_selectbox_mae, inicializar_e_gerenciar_modificacoes, formulario_edicao_comentario_cpof
import numpy as np

padrao_importacao_pagina()

titulos_pagina("Canal de Manifestação Técnica", font_size="1.9em", text_color="#3064AD", icon='<i class="fas fa-edit"></i>')

st.session_state.base_cpof = func_load_base_cpof(forcar_recarregar=True)

membros_cpof = ['SECRETÁRIA EXECUTIVA', 'SEPLAG', 'SEFAZ', 'GABINETE CIVIL', 'SEGOV']

usuario_logado = st.session_state.username.upper() 
if usuario_logado in membros_cpof:
    membro_atual = usuario_logado
    st.markdown(f"🔒 **Membro atual:** {membro_atual}")
    # Coluna_mostrar não funciona atualmente, pois as colunas ocultas, são "apagadas" quando realiza o salvamento, então todos os processos tem suas colunas apagadas ao mergir para a base salva.
    # colunas_mostrar = ['Nº do Processo', 'Órgão (UO)', 'Valor', 'Fonte de Recursos', 'Tipo de Despesa', 'Objetivo', membro_atual, 'Observação']
else:
    membro_atual = st.selectbox(
        "Selecione o membro",
        membros_cpof,
        key='membro',
        help="Escolha o membro para ver os processos pendentes."
    )
    # colunas_mostrar = ['Nº do Processo', 'Órgão (UO)', 'Valor', 'Fonte de Recursos', 'Tipo de Despesa', 'Objetivo'] + membros_cpof + ['Observação']

base_mostrar = st.session_state.base_cpof[st.session_state.base_cpof['Deliberação'] == 'Disponível aos Membros CPOF']  # Core de toda lógica!
# base_mostrar = base_mostrar[colunas_mostrar]

if "filtro_status" not in st.session_state:
    st.session_state.filtro_status = None

# Transformar respostas vazias, False ou strings vazias em NaN
base_mostrar[membro_atual] = base_mostrar[membro_atual].replace([False, '', ' ', None], np.nan)

aguardando_resposta_df = base_mostrar[
    base_mostrar[membro_atual].isna()
]

respondidos_df = base_mostrar[base_mostrar[membro_atual].notna()]

aguardando_resposta = aguardando_resposta_df.shape[0]
respondidos = respondidos_df.shape[0]

indicadores_situacao = {
    "Processos Aguardando Resposta": aguardando_resposta,
    "Processos Respondidos": respondidos,
}

with st.container(): # Botões principais RESPONDIDOS vs AGUARDANDO RESPOSTA - Responsta
        
    col1, col2 = st.columns(2)
    with col1:
        if st.button(f"Processos Aguardando Resposta ({indicadores_situacao['Processos Aguardando Resposta']})", key="btn_aguardando", use_container_width=True, type="primary"):
            st.session_state.filtro_status = "Processos Aguardando Resposta"

    with col2:
        if st.button(f"Processos Respondidos ({indicadores_situacao['Processos Respondidos']})", key="btn_respondidos", use_container_width=True, type="primary"):
            st.session_state.filtro_status = "Processos Respondidos"

# with st.container(): # APÓS A SELEÇÃO DOS BOTÕES ACIMA

resposta_em_bloco = False
editar_processo = False

if st.session_state.filtro_status in ["Processos Aguardando Resposta", "Processos Respondidos"]:

    opcao_selecionada = st.radio(
        "Label_visibility false",
        options=["**Habilitar Edição**", "**Parecer em Bloco**"],
        captions=["*Insira o parecer técnico na tabela abaixo.*", "*Selecione um ou mais processos para informar o parecer em bloco.*"],
        index=0,
        key="opcao_radio",
        horizontal=True,
        label_visibility="collapsed",
    )

    if opcao_selecionada == "**Parecer em Bloco**":
        resposta_em_bloco = True
        editar_processo = True
    elif opcao_selecionada == "**Habilitar Edição**":
        editar_processo = True

    df = aguardando_resposta_df if st.session_state.filtro_status == "Processos Aguardando Resposta" else respondidos_df

    if st.session_state.filtro_status == "Processos Aguardando Resposta" and resposta_em_bloco:
        df.loc[:, membro_atual] = False  # Adiciona a coluna 'Selecionar' para permitir seleção em bloco

        df = df[[membro_atual] + [col for col in df.columns if col != membro_atual]]
        editable_columns = [membro_atual] 

    elif editar_processo:
        editable_columns = [membro_atual]

    base_mostrar, selected_row = mostrar_tabela(df, editable_columns=editable_columns, mostrar_na_tela=True, enable_click=True, nome_tabela=f"{st.session_state.filtro_status} ({len(df)}) - {membro_atual}")

    tem_modificacoes = inicializar_e_gerenciar_modificacoes(selected_row, escolha_coluna=membro_atual)

    if tem_modificacoes:
        
        if st.button("Salvar ✅", type="primary"):
            salvar_modificacoes_selectbox_mae("Histórico CPOF", "Base CPOF", df, escolha_coluna=membro_atual)
            st.session_state["forcar_recarregar"] = True
            del st.session_state["forcar_recarregar"]
            st.rerun()