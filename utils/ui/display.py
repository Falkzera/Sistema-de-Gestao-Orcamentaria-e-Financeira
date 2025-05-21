import streamlit as st
from utils.auth.auth import verificar_permissao

def criar_botao_navegacao(nome_pagina, caminho_pagina, icone, tipo="secondary"):
    """
    Cria um botão de navegação na barra lateral que redireciona para a página especificada.

    Args:
        nome_pagina (str): Nome a ser exibido no botão
        caminho_pagina (str): Caminho para o arquivo da página (ex: "pages/cadastro.py")
        icone (str): Ícone a ser exibido no botão
        tipo (str): Tipo do botão (primary, secondary)

    Returns:
        bool: True se o botão foi clicado, False caso contrário
    """
    # Verifica se a página atual está selecionada para destacar o botão
    pagina_atual = st.session_state.get("selected_page", "")

    # Define o tipo do botão com base na página atual
    tipo_botao = "primary" if pagina_atual == nome_pagina else tipo

    # Cria o botão com o ícone e nome da página
    if st.sidebar.button(f"{icone} {nome_pagina}", use_container_width=True, type=tipo_botao):
        st.session_state.selected_page = nome_pagina
        st.switch_page(caminho_pagina)
        return True
    return False

def exibir_menu_navegacao():
    """
    Exibe o menu de navegação na barra lateral com base nas permissões do usuário.
    """
    # Mapeamento de páginas com nomes padronizados (iguais ao secrets.toml)
    paginas = {
        "home": {"nome_exibicao": "Home", "caminho": "Home.py", "icone": "🏠"},
        "cadastrar_processo": {"nome_exibicao": "Cadastrar Processo", "caminho": "pages/cadastro.py", "icone": "📂"},
        "canal_resposta_cpof": {"nome_exibicao": "Canal de Resposta CPOF", "caminho": "pages/canal_resposta_cpof.py", "icone": "📨"},
        "dashboards": {"nome_exibicao": "Dashboards", "caminho": "pages/dashboards.py", "icone": "📊"},
        "relatorio": {"nome_exibicao": "Relatório", "caminho": "pages/relatorio.py", "icone": "📝"},
        "visualizar_processos": {"nome_exibicao": "Visualizar Processos", "caminho": "pages/visualizar.py", "icone": "🔍"},
        "historico": {"nome_exibicao": "Histórico", "caminho": "pages/historico.py", "icone": "📜"},
    }

    st.sidebar.markdown("---")

    if "logged_in" not in st.session_state or not st.session_state.logged_in:
        criar_botao_navegacao("Login", "pages/login.py", "🔐", "primary")
        return

    page_access = st.session_state.get("page_access", [])

    for chave_pagina, info in paginas.items():
        # Permite acesso se a página está na lista de permissões do usuário
        if chave_pagina in page_access:
            criar_botao_navegacao(info["nome_exibicao"], info["caminho"], info["icone"], "primary")
        # Home é sempre acessível para usuários logados
        elif chave_pagina == "home":
            criar_botao_navegacao(info["nome_exibicao"], info["caminho"], info["icone"], "primary")

    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.page_access = []
        st.session_state.selected_page = "Login"
        st.switch_page("pages/login.py")

def ocultar_barra_lateral_streamlit():
    """
    Função para ocultar a barra lateral do Streamlit, utilizando CSS.
    """

    st.markdown("""
        <style>
        [data-testid="stSidebarNav"] {display: none;}
        </style>
    """, unsafe_allow_html=True)


def configurar_sidebar_marca():
    """
    Exibe o logo de ALAGOAS e um separador visual na barra lateral.
    """
    st.sidebar.image("image/ALAGOAS.png")
    st.sidebar.caption('---')

def configurar_cabecalho_principal():
    """
    Exibe o título principal e o logo da SEPLAG na área principal.
    """
    col1, col2 = st.columns([2, 1.2])
    col1.title("Sistema de Gestão Orçamentária")
    col2.image("image/SEPLAG.png")
    st.write('---')

def exibir_info_usuario_sidebar():
    """
    Exibe o nome do usuário em uma caixa estilizada na barra lateral, se disponível.
    """
    if "username" in st.session_state:
        st.sidebar.markdown(f"""
        <style>
        .caixa-info-usuario {{
            background: #EAEDF1;
            color: #3064AD;
            border-radius: 10px;
            padding: 18px 12px 14px 12px;
            margin-bottom: 10px;
            font-size: 1.05em;
            font-weight: 500;
            box-shadow: 0 2px 8px rgba(48,100,173,0.08);
            text-align: center;
        }}
        .caixa-info-usuario a {{
            color: #3064AD;
            text-decoration: underline;
            font-weight: bold;
        }}
        .caixa-info-usuario a:hover {{
            color: #18325e;
            text-decoration: underline;
        }}
        </style>
        <div class="caixa-info-usuario">
            {st.session_state.username.upper()}
        </div>
        """, unsafe_allow_html=True)
        st.sidebar.markdown("<br>", unsafe_allow_html=True)

def customizar_sidebar():
    """
    Função principal para customizar a barra lateral do Streamlit.
    """
    ocultar_barra_lateral_streamlit()
    configurar_sidebar_marca()
    configurar_cabecalho_principal()
    exibir_info_usuario_sidebar()


def desenvolvido():
    """
    Exibe uma seção estilizada de créditos do desenvolvedor na barra lateral do Streamlit.

    Esta função adiciona uma linha horizontal, um espaçamento e um bloco customizado de HTML/CSS
    na barra lateral, creditando o desenvolvedor com um link estilizado para o perfil do LinkedIn.

    Nota:
        Requer o Streamlit importado como `st`.
        O HTML é renderizado com `unsafe_allow_html=True`.

    Retorna:
        None
    """
    st.sidebar.write("---")
    st.sidebar.markdown("""
    <style>
    .creditos-dev {
        background: #EAEDF1;
        color: #3064AD;
        border-radius: 10px;
        padding: 18px 12px 14px 12px;
        margin-bottom: 10px;
        font-size: 1.05em;
        font-weight: 500;
        box-shadow: 0 2px 8px rgba(48,100,173,0.08);
    }
    .creditos-dev a {
        color: #3064AD;
        text-decoration: underline;
        font-weight: bold;
    }
    .creditos-dev a:hover {
        color: #18325e;
        text-decoration: underline;
    }
    </style>
    <div class="creditos-dev">
        Desenvolvido por: <a href="https://www.linkedin.com/in/falkzera/" target="_blank">Lucas Falcão</a>
    </div>
    """, unsafe_allow_html=True)


def padrao_importacao_pagina():
    """
    Função para definir o padrão de importação do Streamlit.
    """
    customizar_sidebar()
    verificar_permissao()
    exibir_menu_navegacao()
    desenvolvido()