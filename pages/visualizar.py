import streamlit as st

st.set_page_config(page_title="Visualizar Processos", page_icon="🔍", layout="wide")

from utils.ui.display import padrao_importacao_pagina, titulos_pagina
from utils.ui.dataframe import mostrar_tabela
from utils.auth.auth import carregar_base_por_usuario
from src.salvar_alteracoes import salvar_modificacoes_selectbox_mae, inicializar_e_gerenciar_modificacoes
from utils.filtros.filtro import filtros_de_busca
from src.editar_processo_geral import editar_unico_processo
from utils.confeccoes.resumos import mostrar_resumos_por_permissao

import streamlit_nested_layout # NÃO PODE SER EXCLUÍDO, CASO CONTRÁRIO OCORRE ERRO DE IMPORTAÇÃO


padrao_importacao_pagina()

titulos_pagina("Visualizador de Processos", font_size="1.9em", text_color="#3064AD", icon='<i class="fas fa-folder-open"></i>' )

with st.container(): # Carregamento da base PRECISA VER UMA FORMA DE EVITAR O RECARREGAMENTO DA BASE CONSTANTEMENTE!
    df, nome_base, nome_base_historica = carregar_base_por_usuario() # Tempo de execução está obivamente atrlado a essa função aqui, depurar ela mais tarde
    df = filtros_de_busca(df)

with st.container(): # Exibição da Tabela
    df, selected_row = mostrar_tabela(
        df,
        editable_colunas_especiais=True,
        mostrar_na_tela=True,
        enable_click=True,
        nome_tabela=f"{nome_base}",
    )

    tem_modificacoes = inicializar_e_gerenciar_modificacoes(selected_row)

    if tem_modificacoes:
        
        if st.button("Salvar ✅", type="primary"):
            salvar_modificacoes_selectbox_mae(nome_base_historica, nome_base, df)
            st.session_state["forcar_recarregar"] = True
            del st.session_state["forcar_recarregar"]
            st.rerun()

with st.container():
    if not tem_modificacoes:
        if selected_row is not None and "Nº do Processo" in selected_row:
            with st.expander(f"📋 **Editar Processo Selecionado📋** -> *{selected_row['Nº do Processo']}* ", expanded=False):
                editar_unico_processo(selected_row, nome_base, df, nome_base_historica)

with st.container():
    
    mostrar_resumos_por_permissao(df, nome_base)