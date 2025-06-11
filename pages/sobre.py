import streamlit as st

from utils.ui.display import padrao_importacao_pagina, titulos_pagina, rodape_desenvolvedor

st.set_page_config(page_title="Dashboards", page_icon="📊", layout="wide")

padrao_importacao_pagina()

st.write("######")
with st.container(border=False):
    st.write("---")
    
    titulos_pagina("Sobre", font_size="1.9em", text_color="#3064AD", icon='<i class="fas fa-info-circle"></i>' )

    st.markdown(
        """
        <div style='font-size:1.1em; color:#222; line-height:1.2; text-align:center;'>
            <p>
               <h2 style='color:#3064AD;'>Sistema de Gestão Orçamentário e Financeiro</h2>
            </p>
            <h4 style='color:#3064AD;'>Equipe de Desenvolvimento do Sistema de Gestão Orçamentário e Financeiro</h4>
            <b>DESENVOLVEDOR</b><br>
            Luca Matheus Falcão da Silva<br><br>
            <h5 style='color:#3064AD;'>Superintendência de Orçamento Público</h5>
            <b>SUPERINTENDENTE DE ORÇAMENTO PÚBLICO</b><br>
            Messias Junior Caffeu Ritir<br><br>
            <b>ASSESSORIA DE ORÇAMENTO PÚBLICO</b><br>
            Rebeca De Cássia Soares Da Silva Melo<br><br>
            <h5 style='color:#3064AD;'>Gerência de Estudos e Projeções</h5>
            <b>GERENTE DE ESTUDOS E PROJEÇÕES</b><br>
            Cayo Luca Gomes Santana<br>
            <b></b><br>
            <b>SUPERVISÃO DE MONITORAMENTO DAS AÇÕES ORÇAMENTÁRIAS</b><br>
            Adélia Cristina Silva De Lima<br>
            <b></b><br>
            <b>ESTAGIÁRIA</b><br>
            Priscila Luciane Leite Do Nascimento
            <b></b><br>
            <b></b><br>
            <h5 style='color:#3064AD;'>Gerência de Execução Orçamentária</h5>
            <b>GERENTE DE EXECUÇÃO ORÇAMENTÁRIA</b><br>
            Felliphy Rammon Queiroz Ferreira<br>
            <b></b><br>
            <b>SUPERVISÃO DE MODIFICAÇÕES ORÇAMENTÁRIAS</b><br>
            Fillipe Fernando Gomes De Oliveira<br>
            <b></b><br>
            <b>SUPERVISÃO DE EXECUÇÃO DAS EMENDAS PARLAMENTARES</b><br>
            Romero Lima Medeiros Cavalcanti<br>
            <b></b><br>
            <b>ASSESSORIA DE EMENDAS PARLAMENTARES</b><br>
            Isadora Mendes Costa<br><br>
            <h5 style='color:#3064AD;'>Gerência de Orçamento</h5>
            <b>GERENTE DE ORÇAMENTO</b><br>
            Marcos Henrique Agra Costa Malta<br>
            <b></b><br>
            <b>SUPERVISÃO DE PROGRAMAÇÃO ORÇAMENTÁRIA</b><br>
            Arthur Ferreira Da Silva Pitanga<br><br>

        </div>
        """,
        unsafe_allow_html=True
    )





rodape_desenvolvedor()

