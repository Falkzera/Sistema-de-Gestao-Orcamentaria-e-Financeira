import streamlit as st
import streamlit as st
from src.auth_sei import SEILogin
from utils.auth.auth import login
from utils.ui.display import customizar_sidebar, titulos_pagina, desenvolvido, img_pag_icon

st.set_page_config(page_title="SIGOF", page_icon=img_pag_icon(), layout="centered")

customizar_sidebar()
st.sidebar.image("assets/image/sigof.png")
desenvolvido()

st.markdown(
'<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" integrity="sha512-9usAa10IRO0HhonpyAIVpjrylPvoDwiPUiKdWk5t3PyolY1cOd4DSE0Ga+ri4AuTroPR5aQvXU9xC6qOPnzFeg==" crossorigin="anonymous" referrerpolicy="no-referrer" />',
unsafe_allow_html=True
)

if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

BASE_URL = st.secrets["BASE_URL"]

def fazer_login(usuario, senha):
    """
    Função que realiza o login do usuário
    """
    print(f"🔐 Iniciando processo de login para usuário: {usuario}")
    
    try:
        # Chamar a função de login do auth.py
        sucesso, mensagem = login(usuario, senha)
        print(f"📋 Resultado do login: sucesso={sucesso}, mensagem={mensagem}")
        
        if sucesso:
            print(f"✅ Login bem-sucedido para {usuario}")
            print(f"📋 Dados da sessão:")
            print(f"   - Username: {st.session_state.get('username', 'N/A')}")
            print(f"   - CPF: {st.session_state.get('user_cpf', 'N/A')}")
            print(f"   - Páginas: {st.session_state.get('user_paginas', 'N/A')}")
            print(f"   - Bases: {st.session_state.get('user_bases', 'N/A')}")
            return True
        else:
            print(f"❌ Falha no login: {mensagem}")
            st.error(mensagem)
            return False
            
    except Exception as e:
        print(f"❌ Erro durante o processo de login: {str(e)}")
        st.error(f"Erro interno: {str(e)}")
        return False

# Se não estiver logado mostra tela de login
if not st.session_state.logged_in:
    
    with st.form("login_form", border=True):
        
        titulos_pagina("Sistema de Login", font_size="1.9em", text_color="#3064AD", icon='<i class="fas fa-lock"></i>' )
        
        usuario = st.text_input(
            "CPF",
            help="Informe seu CPF cadastrado no sistema"
        )
    
        senha = st.text_input(
            "Senha",
            type="password",
            help="Informe sua senha do sistema SEI"
        )
    
        submitted = st.form_submit_button(
            "ACESSAR",
            use_container_width=True,
            type="primary"
        )

        if submitted:
            if usuario and senha:
                fazer_login(usuario, senha)
                if st.session_state.logged_in:
                    st.switch_page("Home.py")
            else:
                st.error("⚠️ Por favor, preencha todos os campos!")
    st.stop()

if st.session_state.logged_in:
    st.switch_page("Home.py")

