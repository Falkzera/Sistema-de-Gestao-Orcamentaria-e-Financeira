import streamlit as st

from utils.ui.display import padrao_importacao_pagina
from utils.confeccoes.dashboards.mdic_comercio_exterior_dashboard import render_mdic_comercio_exterior_dashboard

st.set_page_config(page_title="Dashboards", page_icon="📊", layout="wide")

padrao_importacao_pagina()

from utils.ui.display import titulos_pagina, desenvolvido
titulos_pagina("Dashboards", font_size="1.9em", text_color="#3064AD", icon='<i class="fas fa-project-diagram"></i>' )

render_mdic_comercio_exterior_dashboard()