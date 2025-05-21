import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection


def salvar_modificacao(processo_id, modificacao, usuario):
    conn = st.connection("gsheets", type=GSheetsConnection)
    agora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    nova_modificacao = {
        "Processo ID": processo_id,
        "Data e Hora": agora,
        "Modificação": modificacao,
        "Usuário": usuario
    }
    try:
        # Lê os dados atuais
        df = conn.read(worksheet="Histórico de Modificações", ttl=0)
        df = pd.DataFrame(df)  
        df = pd.concat([df, pd.DataFrame([nova_modificacao])], ignore_index=True)
        conn.update(worksheet="Histórico de Modificações", data=df)
    except Exception as e:
        st.error(f"Erro ao salvar a modificação: {e}")
        st.stop()


def salvar_modificacoes_em_lote(modificacoes, usuario, base_historico): # quando chamado a partir de um for
    conn = st.connection("gsheets", type=GSheetsConnection)
    agora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    novas_modificacoes = []
    for processo_id, modificacao in modificacoes:
        novas_modificacoes.append({
            "Processo ID": processo_id,
            "Data e Hora": agora,
            "Modificação": modificacao,
            "Usuário": usuario
        })
    try:
        df = conn.read(worksheet=base_historico, ttl=0)
        df = pd.DataFrame(df)
        df = pd.concat([df, pd.DataFrame(novas_modificacoes)], ignore_index=True)
        conn.update(worksheet=base_historico, data=df)
    except Exception as e:
        st.error(f"Erro ao salvar as modificações: {e}")
        st.stop()

def exibir_historico(processo_edit, base_historico):
    if not processo_edit:
        st.info("Selecione um processo para visualizar o histórico.")
        return

    conn = st.connection("gsheets", type=GSheetsConnection)
    df = pd.DataFrame(conn.read(worksheet=base_historico, ttl=0))

    # Filtrar pelo processo selecionado
    df = df[df["Processo ID"] == processo_edit]

    if df.empty:
        st.warning("⚠️ Nenhuma modificação registrada para este processo.")
        return

    # Criar uma coluna de agrupamento por minuto
    df["Grupo"] = df.apply(lambda row: f"{row['Usuário']} — {row['Data e Hora'][:16]}", axis=1)  # 'YYYY-MM-DD HH:MM'

    # Ordenar cronologicamente por esse agrupamento
    df = df.sort_values(by="Data e Hora", ascending=False)

    # Agrupar
    agrupado = {}
    for _, row in df.iterrows():
        grupo = row["Grupo"]
        if grupo not in agrupado:
            agrupado[grupo] = []
        agrupado[grupo].append(row["Modificação"])

    # Montar a estrutura hierárquica
    estrutura = f"📁 Histórico de Modificações — Processo: {processo_edit}\n"
    linhas = []
    grupos = list(agrupado.items())
    for i, (grupo, modificacoes) in enumerate(grupos):
        con_grupo = "└──" if i == len(grupos) - 1 else "├──"
        linhas.append(f"{con_grupo} 📂 {grupo}")
        for j, mod in enumerate(modificacoes):
            con_mod = "    └──" if j == len(modificacoes) - 1 else "    ├──"
            linhas.append(f"{con_mod} 📝 {mod}")

    estrutura += "\n".join(linhas)
    st.markdown("```plaintext\n" + estrutura + "\n```")
