import streamlit as st

from utils.auth.auth import login
from utils.ui.display import customizar_sidebar, titulos_pagina, desenvolvido

st.set_page_config(page_title="Sistema de Login", page_icon="🔐", layout="centered")

customizar_sidebar()
desenvolvido()

st.markdown(
'<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" integrity="sha512-9usAa10IRO0HhonpyAIVpjrylPvoDwiPUiKdWk5t3PyolY1cOd4DSE0Ga+ri4AuTroPR5aQvXU9xC6qOPnzFeg==" crossorigin="anonymous" referrerpolicy="no-referrer" />',
unsafe_allow_html=True
)

with st.container(border=True):
    
    titulos_pagina("Sistema de Login", font_size="1.9em", text_color="#3064AD", icon='<i class="fas fa-lock"></i>' )

    username = st.text_input("Usuário")
    password = st.text_input("Senha", type="password")

    if st.button("CONTINUAR", help="Clique para fazer login", use_container_width=True, type='primary'):
        page_access = login(username, password)

        if page_access:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.page_access = page_access

            st.switch_page("Home.py") 

        else:
            st.error("Usuário ou senha incorretos.")