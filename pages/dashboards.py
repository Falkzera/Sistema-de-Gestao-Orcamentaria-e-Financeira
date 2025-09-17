import streamlit as st

from utils.ui.display import padrao_importacao_pagina, titulos_pagina, rodape_desenvolvedor, img_pag_icon
from utils.confeccoes.dashboards.rgf_dashboard import render_rgf_dashboard
from utils.confeccoes.dashboards.mdic_comercio_exterior_dashboard import render_mdic_comercio_exterior_dashboard
from utils.confeccoes.dashboards.paines_externos import observatorio_orcamento, preco_combustivel

st.set_page_config(page_title="SIGOF", page_icon=img_pag_icon(), layout="wide")

padrao_importacao_pagina()

titulos_pagina("Dashboards", font_size="1.9em", text_color="#3064AD", icon='<i class="fas fa-project-diagram"></i>' )

restringir_usuario_externo_dashboard = ["Observatório do Orçamento", "Dashboard - RGF"]

usuario = st.session_state.get("username", "")

# Definir dashboards disponíveis conforme usuário
if usuario and usuario.lower() == "externo":
    dashboards_disponiveis = ["Mapa do Comércio Exterior"]
else:
    dashboards_disponiveis = ["Observatório do Orçamento", "Mapa do Comércio Exterior", "Dashboard - RGF"]

st.caption("Selecione o dashboard que deseja acessar:")
col1, col2, col3 = st.columns([1, 1, 1])

if "pagina_atual" not in st.session_state or st.session_state["pagina_atual"] not in dashboards_disponiveis:
    st.session_state["pagina_atual"] = dashboards_disponiveis[0]

with col1:
    if "Observatório do Orçamento" in dashboards_disponiveis:
        if st.button("Observatório do Orçamento", use_container_width=True, type="primary"):
            st.session_state["pagina_atual"] = "Observatório do Orçamento"
            st.rerun()

with col2:
    if "Mapa do Comércio Exterior" in dashboards_disponiveis:
        if st.button("Mapa do Comércio Exterior", use_container_width=True, type="primary"):
            st.session_state["pagina_atual"] = "Mapa do Comércio Exterior"
            st.rerun()

with col3:
    if "Dashboard - RGF" in dashboards_disponiveis:
        if st.button("Dashboard - RGF", use_container_width=True, type="primary"):
            st.session_state["pagina_atual"] = "Dashboard - RGF"
            st.rerun()

if st.session_state.get("pagina_atual") == "Mapa do Comércio Exterior":
    st.session_state["pagina_atual"] = "Mapa do Comércio Exterior"
    render_mdic_comercio_exterior_dashboard()

elif st.session_state.get("pagina_atual") == "Dashboard - RGF":
    render_rgf_dashboard()

elif st.session_state.get("pagina_atual") == "Observatório do Orçamento":
    titulos_pagina("Observatório do Orçamento Público", font_size="1.5em", text_color="#3064AD", icon='<i class="fas fa-filter"></i>' )
    with st.container(border=True):
        st.markdown(
            "<div style='text-align: center;'>"
            "<a href='https://app.powerbi.com/view?r=eyJrIjoiZTkyNzU5NGMtOWUwOS00NTZiLWIzYTAtODVkYzY0YjliNDE1IiwidCI6ImNlMTdiNDVkLThmYjctNGYwMy05ZjRlLTYxMTBkMTAzZGI3NiJ9' target='_blank'>"
            "Acesse o dashboard no Power BI"
            "</a>"
            "</div>",
            unsafe_allow_html=True
        )

        observatorio_orcamento()


rodape_desenvolvedor()