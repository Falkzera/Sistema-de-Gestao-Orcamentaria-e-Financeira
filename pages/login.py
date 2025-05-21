import streamlit as st
from utils.ui.display import customizar_sidebar
from utils.auth.auth import login

st.set_page_config(page_title="Sistema de Login", page_icon="🔐", layout="wide")

customizar_sidebar()

st.title("🔐 Sistema de Login")

username = st.text_input("Usuário")
password = st.text_input("Senha", type="password")

if st.button("Entrar", help="Clique para fazer login", icon="🚪", use_container_width=True, type='primary'):
    page_access = login(username, password)

    if page_access:
        st.session_state.logged_in = True
        st.session_state.username = username
        st.session_state.page_access = page_access

        st.switch_page("Home.py") 

    else:
        st.error("Usuário ou senha incorretos.")
