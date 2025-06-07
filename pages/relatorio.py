import streamlit as st

st.set_page_config(page_title="Relatório", page_icon="📄", layout="wide")

from utils.ui.display import padrao_importacao_pagina, titulos_pagina, rodape_desenvolvedor
from utils.confeccoes.formatar import mes_por_extenso

padrao_importacao_pagina() # Está colocado em cima, para que seja carregado mais rápido

from src.base import func_load_base_credito_sop_geo

# >>>>>>>>>>>>>> ATUALIZAÇÃO DAS BASES <<<<<<<<<<<<<<<<
from src.coleta_de_dados.ibge_abate_animais import funcao_ibge_abate_animais
from src.coleta_de_dados.ibge_leite_industrializado import funcao_ibge_leite_industrializado
from src.coleta_de_dados.mdic_comercio_exterior import funcao_mdic_comercio_exterior
from src.coleta_de_dados.anp_preco_combustivel import funcao_anp_preco_combustivel
from src.coleta_de_dados.anp_producao_combustivel import funcao_anp_producao_combustivel
from src.coleta_de_dados.sefaz_dotacao_completo import funcao_sefaz_dotacao
from src.coleta_de_dados.sefaz_despesa_completo import funcao_sefaz_despesa_completo
from src.coleta_de_dados.sefaz_despesa_ano_corrente import funcao_sefaz_despesa_ano_corrente
from src.coleta_de_dados.sefaz_dotacao_ano_corrente import funcao_sefaz_dotacao_ano_corrente
from src.coleta_de_dados.rgf import funcao_rgf

# Botão de Gerar Relatório
from utils.confeccoes.gerar_baixar_confeccao import botao_gerar_e_baixar_arquivo

# >>>>>>>>>>>>>> CONFECÇÕES DO RELATÓRIO <<<<<<<<<<<<<<<<
from utils.confeccoes.relatorio.relatorio_cpof import montar_relatorio_cpof, filtro_ano_mes
from utils.confeccoes.relatorio.relatorio_ibge_abate_animais import montar_relatorio_ibge_abate_animais
from utils.confeccoes.relatorio.relatorio_ibge_leite_industrializado import montar_relatorio_ibge_leite_industrializado
from utils.confeccoes.relatorio.relatorio_mdic_comercio_exterior import montar_relatorio_mdic_comercio_exterior
from utils.confeccoes.relatorio.relatorio_anp_preco_combustivel import montar_relatorio_anp_preco_combustivel
from utils.confeccoes.relatorio.relatorio_anp_etanol import montar_relatorio_anp_etanol
from utils.confeccoes.relatorio.relatorio_anp_gn import montar_relatorio_anp_gn
from utils.confeccoes.relatorio.relatorio_anp_petroleo import montar_relatorio_anp_petroleo
from utils.confeccoes.relatorio.relatorio_anp_lgn import montar_relatorio_anp_lgn
from utils.confeccoes.relatorio.relatorio_sefaz_despesa import montar_relatorio_sefaz_despesa

titulos_pagina("Relatórios", font_size="1.9em", text_color="#3064AD", icon='<i class="fas fa-file-invoice"></i>' )

with st.container(): # Código para o usuário SUDO e talvez ADMIN
        
    st.session_state.setdefault("buffer_download", {})

    if (
        "username" in st.session_state
        and "page_access" in st.secrets
        and st.session_state.username in st.secrets["page_access"]
        and len(st.secrets["page_access"][st.session_state.username]) >= 7
    ):

        with st.container():  # Atualização das Bases -> Será permitido apenas para o admin
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                if st.button("Atualizar Dados do Boletim", use_container_width=True, type="primary"):
                    with st.spinner("Atualizando dados gerais..."):
                        funcao_ibge_abate_animais()
                        funcao_ibge_leite_industrializado()
                        funcao_mdic_comercio_exterior()
                        funcao_anp_preco_combustivel()
                        funcao_anp_producao_combustivel()
                        st.success("Dados atualizados com sucesso!")
            with col2:
                if st.button("Atualizar Dados do Relatório de Despesas", use_container_width=True, type="primary"):
                    with st.spinner("Atualizando dados do relatório de desepsa..."):
                        funcao_sefaz_despesa_completo()
                        st.success("Dados atualizados com sucesso!")
            with col3:
                if st.button("Atualizar Dados Sefaz", use_container_width=True, type="primary"):
                    with st.spinner("Atualizando dados do relatório de desepsa..."):
                        funcao_sefaz_despesa_ano_corrente()
                        # funcao_sefaz_dotacao_ano_corrente()
                        st.success("Dados atualizados com sucesso!")
            
            with col4:
                if st.button("Atualizar Dados RGF", use_container_width=True, type="primary"):
                    with st.spinner("Atualizando dados do RGF..."):
                        funcao_rgf()
                        st.success("Dados atualizados com sucesso!")
    else:
        pass

# >>>>>>>>>>>>>> RELATÓRIOS PARA O USUÁRIO BAIXAR <<<<<<<<<<<<<<<<

restringir_usuario_externo_relatorio = ["Relatório CPOF", "Relatório de Despesas dos Órgãos"]

relatorio_opcoes = [
    "Relatório CPOF",
    "Boletim Conjuntural Alagoano",
    "Relatório de Despesas dos Órgãos",
]

df = None

# Restringe opções para usuário externo
usuario = st.session_state.get("username", "")
if usuario and usuario.lower() == "externo":
    opcoes_filtradas = [op for op in relatorio_opcoes if op not in restringir_usuario_externo_relatorio]
else:
    opcoes_filtradas = relatorio_opcoes

escolha_relatorio = st.selectbox("Selecione o relatório que deseja gerar:", opcoes_filtradas)

if escolha_relatorio == "Relatório CPOF":
    
    with st.container():

        df = func_load_base_credito_sop_geo()

        st.session_state["base_creditos_sop_geo"] = df

        ano, mes, df_filtrado, df_filtrado_mes_anterior = filtro_ano_mes(df, exibir_na_tela=True, key_prefix="home")

        with st.expander("", expanded=True):
            st.subheader("Relatório CPOF")
            st.write('O Relatório CPOF apresenta um panorama detalhado das movimentações orçamentárias no âmbito do Poder Executivo do Estado de Alagoas, com foco nas solicitações e publicações de créditos adicionais conforme os dispositivos legais vigentes (Lei 4.320/64, Lei Estadual nº 9.454/2025 e Decreto nº 100.553/2025).')
        botao_gerar_e_baixar_arquivo(
            nome_botao="Relatório CPOF",
            montar_conteudo_funcao=montar_relatorio_cpof,
            parametros_funcao={
                "ano": ano,
                "mes": mes,
                "df_filtrado": df_filtrado,
                "df_filtrado_mes_anterior": df_filtrado_mes_anterior
            },
            nome_arquivo=f"Relatorio_CPOF_{mes_por_extenso(mes)}_{ano}.pdf",
            tipo_arquivo="pdf",
        )

elif escolha_relatorio == "Boletim Conjuntural Alagoano":
    with st.container():

        def montar_relatorio_composto(**kwargs):
            montar_relatorio_ibge_abate_animais(df)
            montar_relatorio_ibge_leite_industrializado(df)
            montar_relatorio_mdic_comercio_exterior(df)
            montar_relatorio_anp_preco_combustivel(df)
            montar_relatorio_anp_petroleo(df)
            montar_relatorio_anp_etanol(df)
            montar_relatorio_anp_gn(df)
            montar_relatorio_anp_lgn(df)
            
        with st.expander("", expanded=True):
            st.subheader("Boletim Alagoano")
            st.write('O Boletim Alagoano apresenta uma análise abrangente sobre os principais indicadores econômicos e produtivos do estado de Alagoas, com foco na agropecuária, indústria energética e comércio exterior. Estruturado com dados históricos e recentes, o boletim oferece uma visão consolidada e atualizada da performance econômica estadual, destacando tendências, variações trimestrais e posicionamento regional. ')
        
        st.write('---')
        botao_gerar_e_baixar_arquivo(
            nome_botao="Boletim Alagoano",
            montar_conteudo_funcao=montar_relatorio_composto,
            nome_arquivo=f"Boletim_Alagoano.pdf",
            parametros_funcao={"df": df},
            tipo_arquivo="pdf",
        )

elif escolha_relatorio == "Relatório de Despesas dos Órgãos":
    with st.container():
        with st.expander("", expanded=True):
            st.subheader("Relatório de Despesas dos Órgãos")
            st.write('O Relatório de Despesas dos Órgãos apresenta uma análise detalhada das despesas realizadas pelos órgãos do governo, com foco nas movimentações orçamentárias e financeiras. O relatório é estruturado para fornecer uma visão clara e objetiva das despesas, permitindo uma melhor compreensão da execução orçamentária e financeira do governo.')

        botao_gerar_e_baixar_arquivo(
            nome_botao="Relatório de Despesas dos Órgãos",
            montar_conteudo_funcao=montar_relatorio_sefaz_despesa,
            nome_arquivo=f"Relatorio_Despesas_Orgaos.pdf",
            parametros_funcao={"df": df},
            tipo_arquivo="pdf",
        )


rodape_desenvolvedor()