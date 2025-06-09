import streamlit as st

from utils.ui.display import padrao_importacao_pagina, rodape_desenvolvedor
from utils.ui.display import titulos_pagina
from utils.auth.auth import carregar_base_por_usuario
from utils.cadastrar_processos.cadastro import cadastrar_processos_credito_geo, cadastrar_processos_cpof, cadastrar_processos_ted, cadastrar_processos_sop_geral

st.set_page_config(page_title="Cadastrar Processos", page_icon="📂", layout="wide")

padrao_importacao_pagina()

titulos_pagina("Cadastro de Processos", font_size="1.9em", text_color="#3064AD", icon='<i class="fas fa-folder"></i>' )

st.write("######")

with st.container():
    df, nome_base, nome_base_historica = carregar_base_por_usuario(apenas_base=True)

if nome_base == "Base Crédito SOP/GEO":
    cadastrar_processos_credito_geo(nome_base, df)
elif nome_base == "Base CPOF":
    cadastrar_processos_cpof(nome_base, df)
elif nome_base == "Base TED":
    cadastrar_processos_ted(nome_base, df)
elif nome_base == "Base SOP/GERAL":
    cadastrar_processos_sop_geral(nome_base, df)
else:
    st.warning("Você não tem permissão para cadastrar processos.")

rodape_desenvolvedor()