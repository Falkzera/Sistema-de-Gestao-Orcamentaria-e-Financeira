import streamlit as st
import pandas as pd

from datetime import datetime

from streamlit_gsheets import GSheetsConnection

from src.salvar_historico import salvar_modificacoes_em_lote, salvar_modificacao

def salvar_base(df, nome_base):
    """
    Salva as alterações de um DataFrame em uma worksheet do Google Sheets, atualizando ou inserindo linhas conforme o 'Nº do Processo'.
    Parâmetros:
        df (pd.DataFrame): DataFrame contendo os dados a serem salvos ou atualizados.
        nome_base (str): Nome da worksheet no Google Sheets onde os dados serão salvos.
    Comportamento:
        - Conecta à worksheet especificada usando a conexão 'gsheets'.
        - Para cada linha em 'df', atualiza a linha correspondente em 'base' (worksheet) se o 'Nº do Processo' já existir; caso contrário, adiciona a nova linha.
        - Caso as colunas 'Nº do Processo' não existam em ambos os DataFrames, concatena os dados.
        - Atualiza a worksheet com os dados modificados.
        - Exibe mensagem de sucesso e força recarregamento do estado da sessão.
    Erros:
        - Exibe mensagem de erro se 'nome_base' não for uma string.
    """

    conn = st.connection("gsheets", type=GSheetsConnection)
    if not isinstance(nome_base, str):
        st.error("Nome da base inválido ao salvar. Informe o nome do worksheet como string.")
        return

    base = conn.read(worksheet=nome_base, ttl=0)
    base = pd.DataFrame(base)  

    # Atualiza ou substitui a linha com o mesmo 'Nº do Processo'
    if 'Nº do Processo' in base.columns and 'Nº do Processo' in df.columns:
        for _, row in df.iterrows():
            processo_id = row['Nº do Processo']
            idx = base[base['Nº do Processo'] == processo_id].index
            if not idx.empty:
                base.loc[idx[0]] = row  # Atualiza a linha existente
            else:
                base = pd.concat([base, pd.DataFrame([row])], ignore_index=True)  # Adiciona nova linha se não existir
    else:
        base = pd.concat([base, df], ignore_index=True)

    conn.update(worksheet=nome_base, data=base)
    
    st.success(f"Salvo com Sucesso! ✅")
    st.session_state["forcar_recarregar"] = True
    del st.session_state["forcar_recarregar"]

def inicializar_e_gerenciar_modificacoes(selected_row, escolha_coluna=None):
    """
    Inicializa e gerencia modificações de deliberação ou situação para processos.

    Args:
        selected_row: Dicionário contendo os dados da linha selecionada na tabela

    Returns:
        bool: True se existem modificações pendentes, False caso contrário
    """
    # Inicializa a lista de modificações no session state
    if "modificacoes" not in st.session_state:
        st.session_state.modificacoes = []

    # Inicializa selected_row_fixo se necessário
    if "selected_row_fixo" not in st.session_state:
        st.session_state.selected_row_fixo = None

    # Inicializa o status inicial de cada processo em um dicionário
    if "status_inicial" not in st.session_state:
        st.session_state.status_inicial = {}

    coluna_status = None

    """
    Primeiro se define se existe select_row, ou seja, se a linha foi clicada na tabela.
    Após isso, verifica se a "escolha_coluna" foi definida, ou seja, se no chamemento da função, a mesma é definida, caso não seja, por padrão a mesma é None.
    Isto serve para definir qual coluna de status será utilizada, se é a "Deliberação" ou "Situação", ou essa nova coluna escolhida pelo usuário. 
    """
    if selected_row and escolha_coluna is None:
        print("Chegou aqui -> Selected_row é True e escolha_coluna é None")
        if "Deliberação" in selected_row:
            coluna_status = "Deliberação"
            print("Coluna Deliberação encontrada na tabela.")
        elif "Situação" in selected_row:
            coluna_status = "Situação"
            print("Coluna Situação encontrada na tabela.")
        elif "Situação TED" in selected_row:
            coluna_status = "Situação TED"
            print("Coluna Situação TED encontrada na tabela.")
        elif "Situação SOP" in selected_row:
            coluna_status = "Situação SOP"
            print("Coluna Situação SOP encontrada na tabela.")
        else:
            st.warning("Não existe coluna 'Deliberação' nem 'Situação' na tabela. A ação não pode ser completada.")
            return False
        
    elif selected_row and escolha_coluna is not None:
        if escolha_coluna in selected_row:
            coluna_status = escolha_coluna
        else:
            st.warning("Não existe coluna 'Deliberação' nem 'Situação' na tabela. A ação não pode ser completada.")
            return False

    if coluna_status is not None:

        processo_id = selected_row.get("Nº do Processo")
        status_atual = selected_row.get(coluna_status)

        print(f"Coluna atual selecionada: {coluna_status}")

        if processo_id not in st.session_state.status_inicial:
            st.session_state.status_inicial[processo_id] = status_atual

        status_inicial = st.session_state.status_inicial[processo_id]

        if st.session_state.selected_row_fixo is None or st.session_state.selected_row_fixo.get("Processo") != processo_id:
            st.session_state.selected_row_fixo = {
                "Processo": processo_id,
                coluna_status: status_atual
            }

        if status_atual != status_inicial:
            if not any(
                mod["Processo"] == processo_id and
                mod[f"{coluna_status} Anterior"] == status_inicial and
                mod[f"{coluna_status} Atual"] == status_atual
                for mod in st.session_state.modificacoes
            ):
                st.session_state.modificacoes.append({
                    "Processo": processo_id,
                    f"{coluna_status} Anterior": status_inicial,
                    f"{coluna_status} Atual": status_atual
                })
        else:
            st.session_state.modificacoes = [
                mod for mod in st.session_state.modificacoes
                if not (mod["Processo"] == processo_id)
            ]

    if st.session_state.modificacoes:
        processos_pendentes = []
        for mod in st.session_state.modificacoes:
            if mod["Processo"] not in processos_pendentes:
                processos_pendentes.append(mod["Processo"])
        processos_str = "; ".join(str(proc) for proc in processos_pendentes)
        st.caption(f"⬇️ Processo(s) pendente(s): {processos_str}")
        
        return True

    return False

def salvar_modificacoes_selectbox_mae(nome_base_historica, nome_base_principal, df_base, escolha_coluna=None):
    """
    Salva todas as modificações pendentes de deliberação ou situação.
    nome_base_historica: string do worksheet do histórico (ex: 'Histórico CPOF')
    nome_base_principal: string do worksheet da base principal (ex: 'Base CPOF')
    df_base: DataFrame da base principal (será atualizado e salvo)
    """
    
    if not st.session_state.modificacoes:
        st.warning("Nenhuma modificação pendente para salvar.")
        return

    # Detecta qual coluna está sendo usada nas modificações
    exemplo_mod = st.session_state.modificacoes[0]
    print(f"Exemplo_mod: {exemplo_mod}")

    if escolha_coluna is None:
        if "Deliberação Anterior" in exemplo_mod and "Deliberação Atual" in exemplo_mod:
            coluna_status = "Deliberação"
        elif "Situação Anterior" in exemplo_mod and "Situação Atual" in exemplo_mod:
            coluna_status = "Situação"
        elif "Situação TED Anterior" in exemplo_mod and "Situação TED Atual" in exemplo_mod:
            coluna_status = "Situação TED"
        elif "Situação SOP Anterior" in exemplo_mod and "Situação SOP Atual" in exemplo_mod:
            coluna_status = "Situação SOP"
        else:
            st.warning("Não foi possível identificar a coluna de status para salvar as modificações.")
        # return
    elif escolha_coluna is not None:
        if f"{escolha_coluna} Anterior" in exemplo_mod and f"{escolha_coluna} Atual" in exemplo_mod:
            coluna_status = escolha_coluna
        else:
            st.warning("Não foi possível identificar a coluna de status para salvar as modificações.")
            # return

    processos_modificados = []
    for modificacao in st.session_state.modificacoes:
        processo_id = modificacao["Processo"]
        status_antes = modificacao[f"{coluna_status} Anterior"]
        status_depois = modificacao[f"{coluna_status} Atual"]
        modificacao_texto = f"{coluna_status} alterada de '{status_antes}' para '{status_depois}'"
        processos_modificados.append((processo_id, modificacao_texto))

        # Atualiza o dataframe base (df_base) em memória
        idx_base = df_base[df_base['Nº do Processo'] == processo_id].index
        if not idx_base.empty:
            df_base.at[idx_base[0], coluna_status] = status_depois
            df_base.at[idx_base[0], 'Última Edição'] = f"{st.session_state.username.title()} - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
    
    # Atualiza a base no session_state para refletir as alterações na interface
    if nome_base_principal == "Base CPOF":
        st.session_state.base_cpof = df_base
    elif nome_base_principal == "Base Crédito SOP/GEO":
        st.session_state.base_creditos_sop_geo = df_base
    elif nome_base_principal == "Base TED":
        st.session_state.base_ted = df_base
    elif nome_base_principal == "Base SOP/GERAL":
        st.session_state.base_sop_geral = df_base
    # ...adicione outros nomes de base se necessário...

    usuario = st.session_state.username.title()
    salvar_modificacoes_em_lote(processos_modificados, usuario, nome_base_historica)
    salvar_base(df_base, nome_base_principal)

    st.session_state.modificacoes = []
    st.session_state.selected_row_fixo = None
    st.session_state.status_inicial = {}
    st.rerun()

def formulario_edicao_comentario_cpof(numero_processo, membro_cpof, resposta_cpof):
    """
    Atualiza o comentário/resposta de um membro do CPOF para um ou mais processos na base de dados.
    Para cada processo informado, verifica se a resposta fornecida difere da resposta anterior.
    Se houver alteração, atualiza o campo correspondente ao membro do CPOF, registra a data e o usuário da última edição,
    salva a modificação no histórico e persiste as alterações na base de dados.
    Parâmetros:
        numero_processo (str ou list[str]): Número(s) do processo a ser(em) atualizado(s).
        membro_cpof (str): Nome da coluna correspondente ao membro do CPOF.
        resposta_cpof (str): Nova resposta/comentário a ser registrada.
    Efeitos colaterais:
        - Atualiza a base de dados em st.session_state.base_cpof.
        - Salva o histórico de modificações.
        - Exibe mensagens de erro ou informação via Streamlit.
    Exceções:
        - Exibe mensagem de erro via Streamlit se houver falha ao salvar a base de dados.
        - Exibe mensagem informativa se nenhuma modificação for necessária.
    """

    base = st.session_state.base_cpof
    resposta_cpof = resposta_cpof.strip()
    agora = datetime.now()

    if isinstance(numero_processo, str):
        numero_processo = [numero_processo]

    processos_modificados = []
    indices_modificados = []

    # Busca e atualiza apenas os índices necessários, evitando múltiplas buscas e operações desnecessárias
    for num_proc in numero_processo:
        idx = base.index[base["Nº do Processo"] == num_proc]
        if not idx.empty:
            idx = idx[0]
            resposta_anterior = base.at[idx, membro_cpof]
            if isinstance(resposta_anterior, str) and resposta_anterior.strip() == resposta_cpof:
                continue
            base.at[idx, membro_cpof] = resposta_cpof
            base.at[idx, "Última Edição"] = f"{st.session_state.username.title()} - {agora.strftime('%d/%m/%Y %H:%M:%S')}"
            
            salvar_modificacao(num_proc, f"[CPOF] Resposta de {membro_cpof}: {resposta_cpof}", st.session_state.username.title())
            processos_modificados.append(num_proc)
            indices_modificados.append(idx)

    if processos_modificados:
        try:
            salvar_base(base, nome_base="Base CPOF")

        except Exception as e:
            st.error(f"❌ Erro ao salvar na planilha: {e}")
    else:
        st.info("ℹ️ Nenhuma modificação foi necessária.")