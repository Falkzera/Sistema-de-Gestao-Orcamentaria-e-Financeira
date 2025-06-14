import streamlit as st
import plotly.graph_objects as go

from utils.ui.display import padrao_importacao_pagina, rodape_desenvolvedor
from utils.confeccoes.formatar import formatar_valor, formatar_valor2
from src.base import func_load_base_credito_sop_geo
from utils.limite.limite_credito import calcular_limite_credito_atual
from utils.ui.display import titulos_pagina

st.set_page_config(page_title="Página Inicial", page_icon="🏠", layout="wide")

padrao_importacao_pagina()

if "username" not in st.session_state or not st.session_state.username:
    print("Usuário não está logado.")

if "base_access" not in st.secrets or st.session_state.username not in st.secrets["base_access"]:
    print("Usuário não tem acesso a nenhuma base de dados.")

limite = calcular_limite_credito_atual()
VALOR_UTILIZADO_LIMITE = limite["valor_utilizado"]
VALOR_DO_LIMITE = limite["valor_limite"]
ORÇAMENTO_APROVADO_2025 = limite["orcamento_aprovado"]

with st.container():

    with st.container():

        df = func_load_base_credito_sop_geo()

        df['Valor'] = df['Valor'].astype(float) 

    with st.container():

        col1, col2 = st.columns([0.9, 0.1])
        with col1:

            titulos_pagina(" Indicadores Orçamentários", font_size="1.9em", text_color="#3064AD", icon='<i class="fas fa-balance-scale"></i>' )

        with col2:
            mostrar_info = st.toggle("ℹ️", key="mostrar_tooltips")

        indicadores = {
            "Orçamento Aprovado - 2025": ORÇAMENTO_APROVADO_2025,
            "Limite de Execução (10%)": VALOR_DO_LIMITE,
            "Limite Executado": VALOR_UTILIZADO_LIMITE
        }

        tooltips = [
            "O orçamento aprovado é a estimativa legalmente autorizada das receitas e despesas públicas para um determinado exercício financeiro, aprovada pelo Poder Legislativo com base na proposta enviada pelo Executivo. Ele serve como instrumento de planejamento e controle da administração pública, estabelecendo limites para os gastos governamentais em diversas áreas, como saúde, educação, infraestrutura, entre outras. Sua aprovação ocorre por meio da Lei Orçamentária Anual (LOA), em conformidade com as diretrizes da Lei de Diretrizes Orçamentárias (LDO) e do Plano Plurianual (PPA), compondo o ciclo orçamentário brasileiro (GIACOMONI, 2021).",
            "O valor do limite corresponde a um percentual máximo do orçamento aprovado que pode ser utilizado ou comprometido com despesas em determinada etapa da execução orçamentária, funcionando como um mecanismo de controle fiscal e responsabilidade na gestão dos recursos públicos. No estado de Alagoas, esse limite é tradicionalmente fixado em 10% do Orçamento Aprovado, conforme práticas adotadas para garantir o equilíbrio das contas públicas e prevenir a execução de gastos além da capacidade financeira do ente federativo. Esse valor serve como um parâmetro inicial para autorização de despesas, podendo ser revisto conforme a evolução da arrecadação e das prioridades governamentais (GIACOMONI, 2021).",
            "O valor do limite utilizado representa a parcela efetivamente executada ou comprometida dentro do limite previamente autorizado do orçamento — no caso de Alagoas, 10% do Orçamento Aprovado. Ele indica o quanto já foi consumido do total permitido, sendo um importante indicador de acompanhamento da execução orçamentária e da capacidade remanescente para novas despesas. Monitorar esse valor permite ao gestor público tomar decisões fundamentadas, evitando extrapolar os limites legais e promovendo uma gestão fiscal responsável e transparente (GIACOMONI, 2021)."
        ]

        cores_financas = ["#095AA2"] * len(indicadores)

        cols_kpi = st.columns(len(indicadores))
        for idx, (titulo, valor) in enumerate(indicadores.items()):
            with cols_kpi[idx]:
                st.markdown(f"""
                <div style='background-color:{cores_financas[idx]};
                            padding:25px;
                            border-radius:10px;
                            text-align:center;
                            color:white;
                            border:2px solid #b5cee3;
                            animation: fadeIn 0.5s ease-in-out;'>
                    <b style='font-size:18px;'>{titulo}</b><br>
                    <span style='font-size:26px;font-weight:bold;'>{formatar_valor(valor)}</span>
                </div>
                <style>
                @keyframes fadeIn {{
                    from {{ opacity: 0; }}
                    to {{ opacity: 1; }}
                }}
                </style>
                """, unsafe_allow_html=True)

                if mostrar_info:
                    st.markdown(f"""
                    <div style='background-color:#f0f0f0;
                                padding: 10px;
                                border-radius:10px;
                                text-align:;
                                color:black;
                                border:1px solid #ccc;
                                margin-top:10px;
                                max-height:100px;
                                overflow-y:auto;
                                animation: fadeIn 0.5s ease-in-out;'>
                        {tooltips[idx]}
                    </div>
                    <style>
                    @keyframes fadeIn {{
                        from {{ opacity: 0; }}
                        to {{ opacity: 1; }}
                    }}
                    </style>
                    """, unsafe_allow_html=True)


    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    with st.container():

        valor_orcamento_anual_e_executado = (VALOR_UTILIZADO_LIMITE / ORÇAMENTO_APROVADO_2025) * 100
        valor_limite_sobre_usado = (VALOR_UTILIZADO_LIMITE / VALOR_DO_LIMITE) * 100

        indicadores = {
            "Percentual Executado do Total": valor_orcamento_anual_e_executado,
            "Percentual Executado do Limite": valor_limite_sobre_usado,
            "Valor Disponível": VALOR_DO_LIMITE - VALOR_UTILIZADO_LIMITE
        }

        cores_financas = ["#095AA2", "#095AA2", "#095AA2"]

        col1, col2 = st.columns([1, 2])  

        with col1:
            st.markdown("<div style='display: flex; flex-wrap: wrap; gap: 20px;'>", unsafe_allow_html=True)

            for idx, (titulo, valor) in enumerate(indicadores.items()):
                if idx < 2:
                    valor_formatado = f"{formatar_valor2(valor)}"
                else: 
                    valor_formatado = formatar_valor(valor)

                st.markdown(f"""
                <div style='background-color:{cores_financas[idx]};
                    padding:15px;
                    border-radius:10px;
                    text-align:center;
                    color:white;
                    border:2px solid #b5cee3;
                    box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
                    max-width:300px; margin:auto;
                    animation: fadeInSlow 1.5s ease-in-out;'>
                <b style='font-size:18px;'>{titulo}</b><br>
                <span style='font-size:26px;font-weight:bold;'>{valor_formatado}</span>
                </div>
                <style>
                @keyframes fadeInSlow {{
                    from {{ opacity: 0; }}
                    to {{ opacity: 1; }}
                }}
                </style>
                """, unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

        with col2:
            fig = go.Figure(
                data=[go.Pie(
                    labels=["Executado", "Disponível"],
                    values=[valor_limite_sobre_usado, 100 - valor_limite_sobre_usado],
                    hole=0.4,
                    marker=dict(colors=["#095AA2", "#E0E0E0"]),
                    textinfo="percent+label",
                    insidetextorientation="radial",
                    textfont=dict(size=16) 
                )]
            )

            fig.update_layout(
                margin=dict(t=0, b=0),
                height=340,
                showlegend=False,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                transition={'duration': 1000, 'easing': 'cubic-in-out'},
                
                )
            
            fig.data[0].values = [valor_limite_sobre_usado, 100 - valor_limite_sobre_usado]
            st.plotly_chart(fig, use_container_width=True)

st.write('---')

username = st.session_state.username
base_access = st.secrets.get("base_access", {})

if "Base Crédito SOP/GEO" in base_access.get(username, []):
    st.caption('Acompanhamento da Situação Processual')

    situacao_counts = df['Situação'].value_counts()
    situacao_counts = situacao_counts.reset_index()
    situacao_counts.columns = ['Situação', 'Quantidade']

    total_processos = situacao_counts['Quantidade'].sum()
    qtd_processos_sem_cobertura = df[df['Origem de Recursos'].str.startswith('Sem Cobertura')].shape[0]
    qtd_processos_com_cobertura = df[~df['Origem de Recursos'].str.startswith('Sem Cobertura')].shape[0]

    def escolhendo_indicador(situacao_counts, situacao):
        return situacao_counts.set_index('Situação').get('Quantidade', {}).get(situacao, 0)

    indicadores_situacao = {
        "Total de Processos": total_processos,
        "Processos com Cobertura": qtd_processos_com_cobertura,
        "Processos sem Cobertura": qtd_processos_sem_cobertura,
        "Publicado": escolhendo_indicador(situacao_counts, 'Publicado'),  
        }
    
    azuis = ["#095aa2"]

    cores_financas = [azuis[i % len(azuis)] for i in range(len(indicadores_situacao))]

    cols_kpi = st.columns(len(indicadores_situacao))
    for idx, (titulo, valor) in enumerate(indicadores_situacao.items()):
        with cols_kpi[idx]:
            st.markdown(f"""
            <div style='background-color:{cores_financas[idx]};
                        padding:20px;
                        border-radius:20px;
                        text-align:center;
                        color:white;
                        border:0px solid #b5cee3;
                        animation: fadeIn 0.5s ease-in-out;'>
                <b style='font-size:18px;'>{titulo}</b><br>
                <span style='font-size:30px;font-weight:bold;'>{(valor)}</span>
            </div>
            <style>
            @keyframes fadeIn {{
                from {{ opacity: 0; }}
                to {{ opacity: 1; }}
            }}
            </style>
            """, unsafe_allow_html=True)

from utils.confeccoes.email.email import rotina_envio_email_ted # <<<<<<<< QUALQUER USUÁRIO DEVE ATIVAR ISSO????? ACHO QUE NÃO, NÉ? --> Visualizar o que a Gabi gostaria de ver aqui e imnplementar essa atualziacao em conjunto
# Pois provavelmente também terá e-mail autoamtico dela.
# --> Realizar e-mail automatico, do mesmo escopo de Backup com o resumo do dia anterior -> Processos que Houberam Modificações e processos cadastrados.
# Em cima um resumo de: Quantos processos foram cadastrados, e quantos foram modificados. 
# E embaixo um essas informações mais detalhadas.



rotina_envio_email_ted()

rodape_desenvolvedor()