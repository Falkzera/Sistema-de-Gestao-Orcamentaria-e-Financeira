import streamlit as st

from src.base import (
    func_load_base_cpof,
    func_load_historico_cpof,
    func_load_base_credito_sop_geo,
    func_load_historico_credito_sop_geo
)

def controle_sessao():
    """
    Inicializa as variáveis de sessão necessárias para o controle de autenticação.
    """
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "username" not in st.session_state:
        st.session_state.username = ""
    if "page_access" not in st.session_state:
        st.session_state.page_access = []
    if "selected_page" not in st.session_state:
        st.session_state.selected_page = "🏠 Home"

def login(username, password):
    """
    Verifica as credenciais do usuário e retorna as permissões de acesso.

    Args:
        username (str): Nome de usuário
        password (str): Senha do usuário

    Returns:
        list: Lista de páginas que o usuário tem permissão para acessar, ou None se as credenciais forem inválidas
    """
    users = st.secrets["users"]
    page_access = st.secrets["page_access"]

    if username in users and users[username] == password:
        return page_access.get(username, [])
    return None

def verificar_permissao():
    """
    Verifica se o usuário está autenticado e possui permissão para acessar a página atual.

    Esta função realiza duas verificações:
    1. Se o usuário não está autenticado (não existe ou está falso o estado 'logged_in' na sessão),
        redireciona para a página de login.
    2. Se o usuário não possui permissão de acesso à página (estado 'page_access' ausente ou inválido na sessão),
        exibe uma mensagem de erro e interrompe a execução da página.

    Requer que o módulo Streamlit (`st`) esteja importado e que o estado da sessão esteja corretamente configurado.
    """

    if "logged_in" not in st.session_state or not st.session_state.logged_in:
        st.switch_page("pages/login.py")

    if "page_access" not in st.session_state or not st.session_state.page_access:
        st.error("🚫 Você não tem permissão para acessar esta página.")
        st.switch_page("pages/Home.py")
        st.stop()
# Construir um mapeamento de usuários e suas permissões


def carregar_base_por_usuario(
    titulo_selectbox="Selecione a base de dados:",
    chave_selectbox="base_selectbox",
    forcar_recarregar=False,
    apenas_historico=False,
):
    """
    Carrega a base de dados apropriada com base no usuário logado e nas permissões definidas em secrets.toml.
    Permite forçar recarregamento do Google Sheets.
    Retorna o DataFrame já armazenado em session_state pelo base.py.
    """


    # Mapeamento do nome da base para a função de carregamento e chave do session_state
    bases = {
        "Base CPOF": {"func": func_load_base_cpof, "session_key": "base_cpof"},
        "Histórico CPOF": {"func": func_load_historico_cpof, "session_key": "historico_cpof"},
        "Base Crédito SOP/GEO": {"func": func_load_base_credito_sop_geo, "session_key": "base_creditos_sop_geo"},
        "Histórico Crédito SOP/GEO": {"func": func_load_historico_credito_sop_geo, "session_key": "historico_credito_sop_geo"}
    }
    historico_map = {
        "Base CPOF": "Histórico CPOF",
        "Base Crédito SOP/GEO": "Histórico Crédito SOP/GEO",
        "Histórico CPOF": "Histórico CPOF",
        "Histórico Crédito SOP/GEO": "Histórico Crédito SOP/GEO"
    }

    if "username" not in st.session_state or not st.session_state.username:
        st.error("Usuário não está logado.")
        return None, "Nenhuma base carregada", None

    username = st.session_state.username
    base_access = st.secrets.get("base_access", {})
    bases_permitidas = base_access.get(username, [])

    if not bases_permitidas:
        st.error(f"Usuário {username} não tem permissão para acessar nenhuma base de dados.")
        return None, "Nenhuma base carregada", None

    if len(bases_permitidas) >= 4:
        nome_base_selecionada = st.selectbox(
            titulo_selectbox,
            bases_permitidas,
            key=chave_selectbox
        )
    else:
        nome_base_selecionada = bases_permitidas[0]

    # Busca a função e a chave do session_state correspondente
    base_info = bases.get(nome_base_selecionada)
    if base_info is None:
        st.error(f"Função de carregamento não encontrada para a base '{nome_base_selecionada}'.")
        return None, nome_base_selecionada, None

    # Chama a função de carregamento (ela já gerencia o session_state internamente)
    base_info["func"](forcar_recarregar=forcar_recarregar)

    # Retorna o DataFrame diretamente do session_state, conforme definido em base.py
    base_dados = st.session_state.get(base_info["session_key"], None).copy()

    if base_dados is None:
        st.error(f"Erro ao carregar a base '{nome_base_selecionada}'.")
        return None, nome_base_selecionada, None
    
    if apenas_historico: # ADICIONAR AQUI LÓGICA DE ESCOLHER QUAL BASE HISTÓRICO CARREGAR, IMPEDINDO QUE SEJA SELECIONADO ATRAVÉS DO SELECTBOX AS BASES QUE NÃO SEJAM HISTÓRICAS
        return base_dados, nome_base_selecionada, None

    nome_base_historica = historico_map.get(nome_base_selecionada, None)
    return base_dados, nome_base_selecionada, nome_base_historica