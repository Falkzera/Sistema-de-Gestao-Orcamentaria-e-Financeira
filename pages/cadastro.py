import streamlit as st

from utils.ui.display import padrao_importacao_pagina
from utils.auth.auth import carregar_base_por_usuario
from utils.cadastrar_processos.cadastro import cadastrar_processos_credito_geo, cadastrar_processos_cpof, mostrar_cadastro_por_permissao

padrao_importacao_pagina()

st.header("Cadastro de Processos de Execução Orçamentária 📁")
st.write("######")

with st.container(): # Carregamento da base PRECISA VER UMA FORMA DE EVITAR O RECARREGAMENTO DA BASE CONSTANTEMENTE!
    df, nome_base, nome_base_historica = carregar_base_por_usuario() # Tempo de execução está obivamente atrlado a essa função aqui, depurar ela mais tarde


# mostrar_cadastro_por_permissao(nome_base, df)

if nome_base == "Base Crédito SOP/GEO":
    cadastrar_processos_credito_geo(nome_base, df)
elif nome_base == "Base CPOF":
    cadastrar_processos_cpof(nome_base, df)
else:
    st.warning("Você não tem permissão para cadastrar processos.")