import streamlit as st

from utils.ui.display import padrao_importacao_pagina, titulos_pagina, rodape_desenvolvedor

st.set_page_config(page_title="Dashboards", page_icon="📊", layout="wide")

padrao_importacao_pagina()

st.write("######")
with st.container(border=True):
    
    titulos_pagina("Sobre", font_size="1.9em", text_color="#3064AD", icon='<i class="fas fa-info-circle"></i>' )

    st.markdown(
        """
        <div style='text-align: center;'>
            <p>O Sistema de Gestão Orçamentária e Financeira (SIGOF) foi desenvolvido para auxiliar a administração pública, com o objetivo de centralizar a gestão orçamentária do Estado de Alagoas.</p>
            <p>Para mais informações, entre em contato com a equipe de desenvolvimento.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

rodape_desenvolvedor()

