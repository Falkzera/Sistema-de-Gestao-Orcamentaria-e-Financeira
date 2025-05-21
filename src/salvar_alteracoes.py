import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

def salvar_base(df, nome_base):
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
    st.write(f"Base salva: {nome_base}")


def inicializar_e_gerenciar_modificacoes(selected_row):
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

    # Detecta qual coluna usar: Deliberação ou Situação
    coluna_status = None
    if selected_row:
        if "Deliberação" in selected_row:
            coluna_status = "Deliberação"
        elif "Situação" in selected_row:
            coluna_status = "Situação"
        else:
            st.warning("Não existe coluna 'Deliberação' nem 'Situação' na tabela. A ação não pode ser completada.")
            return False

        processo_id = selected_row.get("Nº do Processo")
        status_atual = selected_row.get(coluna_status)

        # Se selected_row_fixo ainda não foi definido, define-o
        if st.session_state.selected_row_fixo is None:
            st.session_state.selected_row_fixo = {
                "Processo": processo_id,
                coluna_status: status_atual
            }

        # Verifica se o processo selecionado é diferente do processo fixo
        if st.session_state.selected_row_fixo["Processo"] != processo_id:
            st.session_state.selected_row_fixo = {
                "Processo": processo_id,
                coluna_status: status_atual
            }

        # Verifica se o status foi modificado
        if st.session_state.selected_row_fixo.get(coluna_status) != status_atual:
            status_antes = st.session_state.selected_row_fixo.get(coluna_status)

            # Adiciona a modificação à lista se ainda não existir
            if not any(
                mod["Processo"] == processo_id and
                mod[f"{coluna_status} Anterior"] == status_antes and
                mod[f"{coluna_status} Atual"] == status_atual
                for mod in st.session_state.modificacoes
            ):
                st.session_state.modificacoes.append({
                    "Processo": processo_id,
                    f"{coluna_status} Anterior": status_antes,
                    f"{coluna_status} Atual": status_atual
                })

            # Atualiza o status no selected_row_fixo
            st.session_state.selected_row_fixo[coluna_status] = status_atual

    # Exibe informações sobre processos pendentes
    if st.session_state.modificacoes:
        processos_pendentes = []
        for mod in st.session_state.modificacoes:
            if mod["Processo"] not in processos_pendentes:
                processos_pendentes.append(mod["Processo"])
        processos_str = "; ".join(str(proc) for proc in processos_pendentes)
        st.caption(f"Processo(s) pendente(s): {processos_str}")
        return True

    return False

def salvar_modificacoes_selectbox_mae(nome_base_historica, nome_base_principal, df_base):
    """
    Salva todas as modificações pendentes de deliberação ou situação.
    nome_base_historica: string do worksheet do histórico (ex: 'Histórico CPOF')
    nome_base_principal: string do worksheet da base principal (ex: 'Base CPOF')
    df_base: DataFrame da base principal (será atualizado e salvo)
    """
    from src.salvar_historico import salvar_modificacoes_em_lote

    if not st.session_state.modificacoes:
        st.warning("Nenhuma modificação pendente para salvar.")
        return

    # Detecta qual coluna está sendo usada nas modificações
    exemplo_mod = st.session_state.modificacoes[0]
    if "Deliberação Anterior" in exemplo_mod and "Deliberação Atual" in exemplo_mod:
        coluna_status = "Deliberação"
    elif "Situação Anterior" in exemplo_mod and "Situação Atual" in exemplo_mod:
        coluna_status = "Situação"
    else:
        st.warning("Não foi possível identificar a coluna de status para salvar as modificações.")
        return

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

    # Salva as modificações em lote no histórico correto
    usuario = st.session_state.username.title()
    salvar_modificacoes_em_lote(processos_modificados, usuario, nome_base_historica)
    # Salva o DataFrame atualizado na base principal correta
    salvar_base(df_base, nome_base_principal)

    # Limpa a lista de modificações
    st.session_state.modificacoes = []
    st.session_state.selected_row_fixo = None
    st.rerun()

def formulario_edicao_comentario_cpof(numero_processo, membro_cpof, resposta_cpof):
    base = st.session_state.base
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
            from src.salvar_historico import salvar_modificacao
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