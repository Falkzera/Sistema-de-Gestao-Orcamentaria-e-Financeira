import streamlit as st

from utils.ui.display import padrao_importacao_pagina
from utils.ui.dataframe import mostrar_tabela
from src.salvar_alteracoes import formulario_edicao_comentario_cpof
from utils.ui.display import titulos_pagina
from src.base import func_load_base_cpof
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
padrao_importacao_pagina()

titulos_pagina("Canal de Manifestação Técnica", font_size="1.9em", text_color="#3064AD", icon='<i class="fas fa-edit"></i>')


st.session_state.base_cpof = func_load_base_cpof(forcar_recarregar=True)

membros_cpof = ['SECRETÁRIA EXECUTIVA', 'SEPLAG', 'SEFAZ', 'GABINETE CIVIL', 'SEGOV']

usuario_logado = st.session_state.username.upper() 
if usuario_logado in membros_cpof:
    membro_atual = usuario_logado
    st.markdown(f"🔒 **Membro atual:** {membro_atual}")
    colunas_mostrar = ['Nº do Processo', 'Órgão (UO)', 'Valor', 'Fonte de Recursos', 'Tipo de Despesa', 'Objetivo', membro_atual, 'Observação']
else:
    membro_atual = st.selectbox(
        "Selecione o membro",
        membros_cpof,
        key='membro',
        help="Escolha o membro para ver os processos pendentes."
    )
    colunas_mostrar = ['Nº do Processo', 'Órgão (UO)', 'Valor', 'Fonte de Recursos', 'Tipo de Despesa', 'Objetivo'] + membros_cpof + ['Observação']

base_mostrar = st.session_state.base_cpof[st.session_state.base_cpof['Deliberação'] == 'Disponível aos Membros CPOF']  # Core de toda lógica!
base_mostrar = base_mostrar[colunas_mostrar]

if "filtro_status" not in st.session_state:
    st.session_state.filtro_status = None

aguardando_resposta_df = base_mostrar[base_mostrar[membro_atual].isna()]
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
        if st.button(f"Processos Aguardando Resposta ({indicadores_situacao['Processos Aguardando Resposta']})", key="btn_aguardando", use_container_width=True):
            st.session_state.filtro_status = "Processos Aguardando Resposta"

    with col2:
        if st.button(f"Processos Respondidos ({indicadores_situacao['Processos Respondidos']})", key="btn_respondidos", use_container_width=True):
            st.session_state.filtro_status = "Processos Respondidos"

# with st.container(): # APÓS A SELEÇÃO DOS BOTÕES ACIMA

resposta_em_bloco = False
editar_processo = False

if st.session_state.filtro_status in ["Processos Aguardando Resposta", "Processos Respondidos"]:

    opcao_selecionada = st.radio(
        "",
        options=["**Habilitar Edição**", "**Parecer em Bloco**"],
        captions=["*Insira o parecer técnico na tabela abaixo.*", "*Selecione um ou mais processos para informar o parecer em bloco.*"],
        index=0,
        key="opcao_radio",
        horizontal=True,
    )

    if opcao_selecionada == "**Parecer em Bloco**":
        resposta_em_bloco = True
        editar_processo = True
    elif opcao_selecionada == "**Habilitar Edição**":
        editar_processo = True

    df = aguardando_resposta_df if st.session_state.filtro_status == "Processos Aguardando Resposta" else respondidos_df

    if resposta_em_bloco:
        df['Selecionar'] = False  # Adiciona a coluna 'Selecionar' para permitir seleção em bloco

        df = df[['Selecionar'] + [col for col in df.columns if col != 'Selecionar']]
        editable_columns = ['Selecionar'] 

    elif editar_processo:
        editable_columns = [membro_atual]

    base_mostrar, selected_row = mostrar_tabela(df, editable_columns=editable_columns, mostrar_na_tela=True, enable_click=True, nome_tabela=f"{st.session_state.filtro_status} ({len(df)}) - {membro_atual}")

    if resposta_em_bloco:   
        processos_respondidos = base_mostrar[base_mostrar['Selecionar']]['Nº do Processo'].tolist()  # Captura os processos selecionados
        resposta_membro_atual = [None] * len(processos_respondidos)  # Respostas serão preenchidas em bloco
    else:
        processos_respondidos = base_mostrar[base_mostrar[membro_atual].notna()]['Nº do Processo'].tolist()  # Captura processos com respostas
        resposta_membro_atual = base_mostrar[base_mostrar[membro_atual].notna()][membro_atual].values.tolist()  # Captura respostas individuais

        # só aparecer se houver alteração
        with st.container(): # Bloco de Resposta, só deve aparecer caso haja resposta em resposta_membro_atual e processos_respondidos
        
            if processos_respondidos and resposta_membro_atual and editar_processo:
                # if st.session_state.filtro_status == "Processos Respondidos": # alterar formato que salva aqui
                #     # 
                if st.button("Salvar ✅", type="primary"):
                    # Verificando se há processos e respostas
                    if processos_respondidos and resposta_membro_atual:
                        # Coletar os processos e as respostas em uma lista de dicionários
                        processos_a_atualizar = []
                        for numero_processo, resposta in zip(processos_respondidos, resposta_membro_atual):
                            processos_a_atualizar.append((numero_processo, resposta))

                        # Agora, atualize todos os processos de uma vez
                        try:
                            # Criar um batch de atualizações
                            for numero_processo, resposta in processos_a_atualizar:
                                row_index = st.session_state.base_cpof[st.session_state.base_cpof["Nº do Processo"] == numero_processo].index[0]
                                st.session_state.base_cpof.at[row_index, membro_atual] = resposta
                                st.session_state.base_cpof.at[row_index, "Última Edição"] = f"{st.session_state.username.title()} - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
                                
                            conn = st.connection("gsheets", type=GSheetsConnection)
                            conn.update(worksheet="Base CPOF", data=st.session_state.base_cpof)
                            st.success(f"✅ Respostas enviadas com sucesso para {len(processos_a_atualizar)} processo(s)!")

                        except Exception as e:
                            st.error(f"❌ Erro ao salvar na planilha: {e}")
                    else:
                        st.warning("⚠️ Preencha a resposta e selecione ao menos um processo.")

laranja = '#e69e19'
verde = '#0d730d'
cor_situacao = verde if st.session_state.filtro_status == "Processos Respondidos" else laranja

with st.container(): # RESPOSTA EM BLOCO
        
    if resposta_em_bloco:
        processos_selecionados_bloco = base_mostrar.loc[base_mostrar['Selecionar'], 'Nº do Processo'].tolist()

        if processos_selecionados_bloco:
            st.markdown(f"""
            <div style="text-align: center; margin-top: 10px; margin-bottom: 10px; color: {cor_situacao};">
                <h5>Situação: <span style="color: {cor_situacao};">{st.session_state.filtro_status}</span></h5>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div style="border: 1px solid #3064ad; padding: 10px; border-radius: 6px; background-color: #f1f8ff; margin-bottom: 10px;">
                <b>📌 Processos selecionados ({len(processos_selecionados_bloco)}):</b><br>
            """ + ", ".join([f"<span style='color:#3064ad;font-weight:500'>{p}</span>" for p in processos_selecionados_bloco]) + "</div>", unsafe_allow_html=True)

        resposta_bloco = st.text_area("✍️ Insira seu parecer técnico:", height=80, placeholder="insira aqui seu parecer técnico", help="Insira seu parecer técnico.", key="resposta_bloco")

        if st.button("✅ Enviar Resposta em Bloco", use_container_width=True, type="primary", key="enviar_resposta_bloco"):
            if resposta_bloco.strip() and processos_selecionados_bloco:
                formulario_edicao_comentario_cpof(
                    numero_processo=processos_selecionados_bloco,
                    membro_cpof=membro_atual,
                    resposta_cpof=resposta_bloco
                )
            else:
                st.warning("⚠️ Preencha a resposta e selecione ao menos um processo.")

    elif editar_processo: # EDIÇÃO NORMAL + VISUALIZAÇÃO
        try:
            if selected_row and "Nº do Processo" in selected_row:
                processo_unico = selected_row["Nº do Processo"]
            else:
                st.stop()
        except NameError:
            st.info("⚠️ Selecione uma das opções acima.")
            st.stop()

        if not processo_unico:
            st.info("⚠️ Selecione um processo para continuar.")
            st.stop()

        try:
            dados = base_mostrar[base_mostrar['Nº do Processo'] == processo_unico].iloc[0]
        except IndexError:
            st.stop()
