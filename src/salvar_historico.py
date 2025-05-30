import streamlit as st
import pandas as pd

from datetime import datetime

from streamlit_gsheets import GSheetsConnection

def salvar_modificacao(processo_id, modificacao, usuario, nome_base_historica):
    """
    Salva uma modificação realizada em um processo em uma base histórica no Google Sheets.

    Parâmetros:
        processo_id (str or int): Identificador único do processo modificado.
        modificacao (str): Descrição da modificação realizada.
        usuario (str): Nome ou identificador do usuário que realizou a modificação.
        nome_base_historica (str): Nome da worksheet (aba) no Google Sheets onde o histórico será salvo.

    Comportamento:
        - Lê os dados atuais da worksheet especificada.
        - Adiciona uma nova linha com as informações da modificação, incluindo data e hora atual.
        - Atualiza a worksheet com o novo histórico.
        - Em caso de erro, exibe uma mensagem de erro e interrompe a execução.

    Exceções:
        Exibe mensagem de erro na interface Streamlit e interrompe a execução caso ocorra qualquer exceção durante o processo.
    """

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
        df = conn.read(worksheet=nome_base_historica, ttl=0)
        df = pd.DataFrame(df)  
        df = pd.concat([df, pd.DataFrame([nova_modificacao])], ignore_index=True)
        conn.update(worksheet=nome_base_historica, data=df)
    except Exception as e:
        st.error(f"Erro ao salvar a modificação: {e}")
        st.stop()

def salvar_modificacoes_em_lote(modificacoes, usuario, base_historico): 
    """
    Salva um lote de modificações em uma planilha do Google Sheets, registrando o ID do processo, data e hora da modificação, descrição da modificação e o usuário responsável.
    Args:
        modificacoes (list of tuple): Lista de tuplas contendo (processo_id, modificacao) para cada modificação a ser salva.
        usuario (str): Nome ou identificador do usuário que realizou as modificações.
        base_historico (str): Nome da worksheet (aba) no Google Sheets onde o histórico será salvo.
    Raises:
        Exibe uma mensagem de erro na interface Streamlit e interrompe a execução caso ocorra alguma exceção durante o salvamento.
    """

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
    """
    Exibe o histórico de modificações de um processo selecionado em formato hierárquico.
    Parâmetros:
        processo_edit (str or int): Identificador do processo selecionado para visualização do histórico.
        base_historico (str): Nome da worksheet no Google Sheets contendo o histórico das modificações.
    Funcionalidade:
        - Caso nenhum processo seja selecionado, exibe uma mensagem informativa.
        - Lê os dados do histórico a partir de uma conexão com Google Sheets.
        - Filtra as modificações referentes ao processo selecionado.
        - Caso não haja modificações, exibe um aviso.
        - Agrupa as modificações por usuário e minuto de alteração.
        - Exibe o histórico em formato de árvore hierárquica, mostrando usuário, data/hora e as modificações realizadas.
    Dependências:
        - Requer Streamlit (`st`) para exibição das mensagens e markdown.
        - Requer pandas (`pd`) para manipulação dos dados.
        - Requer uma conexão do tipo `GSheetsConnection` configurada no Streamlit.
    """

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