import streamlit as st

from utils.ui.display import padrao_importacao_pagina
from utils.confeccoes.dashboards.mdic_comercio_exterior_dashboard import render_mdic_comercio_exterior_dashboard

padrao_importacao_pagina()



render_mdic_comercio_exterior_dashboard()