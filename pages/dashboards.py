import streamlit as st

from utils.ui.display import padrao_importacao_pagina
from utils.confeccoes.dashboards.mdic_comercio_exterior_dashboard import render_mdic_comercio_exterior_dashboard
from utils.confeccoes.dashboards.rgf_dashboard import render_rgf_dashboard

st.set_page_config(page_title="Dashboards", page_icon="📊", layout="wide")

padrao_importacao_pagina()

from utils.ui.display import titulos_pagina, desenvolvido

titulos_pagina("Dashboards", font_size="1.9em", text_color="#3064AD", icon='<i class="fas fa-project-diagram"></i>' )

col1, col2 = st.columns([1, 1])

with col1:
    if st.button("Dashboard - Comércio Exterior", use_container_width=True, type="primary"):
        st.session_state["pagina_atual"] = "Dashboard - Comércio Exterior"
        
        st.rerun()

with col2:
    if st.button("Dashboard - RGF", use_container_width=True, type="primary"):
        st.session_state["pagina_atual"] = "Dashboard - RGF"
        
        st.rerun()

if st.session_state.get("pagina_atual") == "Dashboard - Comércio Exterior":
    st.session_state["pagina_atual"] = "Dashboard - Comércio Exterior"
    render_mdic_comercio_exterior_dashboard()
elif st.session_state.get("pagina_atual") == "Dashboard - RGF":
    render_rgf_dashboard()