import streamlit as st
import plotly.graph_objects as go

from utils.ui.display import padrao_importacao_pagina, rodape_desenvolvedor
from utils.confeccoes.formatar import formatar_valor, formatar_valor2
from src.base import func_load_base_credito_sop_geo
from utils.limite.limite_credito import calcular_limite_credito_atual
from utils.limite.limite_nota_reestimativa import calcular_nota_reestimativa
from utils.ui.display import titulos_pagina, img_pag_icon

st.set_page_config(page_title="SIGOF", page_icon=img_pag_icon(), layout="wide")

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


    tabs1, tabs2 = st.tabs(["📊 Limite de Crédito", "📈 Notas de Reestimativa"])
    with tabs1:
            
        with st.container():

            col1, col2 = st.columns([0.9, 0.1])
            with col1:

                titulos_pagina(" Indicadores Orçamentários", font_size="1.9em", text_color="#3064AD", icon='<i class="fas fa-balance-scale"></i>' )

            with col2:
                mostrar_info = st.toggle("ℹ️", key="mostrar_tooltips_2")

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
                st.plotly_chart(fig, use_container_width=True, key="grafico_limite_credito",)


# Nota de reestimativa

limite = calcular_nota_reestimativa()
valor_utilizado_nota_restimativa_1 = limite["valor_utilizado_nota_reestimativa_1"]
valor_utilizado_nota_restimativa_2 = limite["valor_utilizado_nota_reestimativa_2"]
valor_utilizado_nota_restimativa_3 = limite["valor_utilizado_nota_reestimativa_3"]
valor_utilizado_nota_reestimativa_4 = limite["valor_utilizado_nota_reestimativa_4"]
nota_reestimativa_1 = limite["nota_reestimativa_1"]
nota_reestimativa_2 = limite["nota_reestimativa_2"]
nota_reestimativa_3 = limite["nota_reestimativa_3"]
nota_reestimativa_4 = limite["nota_reestimativa_4"]
saldo_disponivel_nota_reestimativa_1 = limite["saldo_disponivel_nota_reestimativa_1"]
saldo_disponivel_nota_reestimativa_2 = limite["saldo_disponivel_nota_reestimativa_2"]
saldo_disponivel_nota_reestimativa_3 = limite["saldo_disponivel_nota_reestimativa_3"]
saldo_disponivel_nota_reestimativa_4 = limite["saldo_disponivel_nota_reestimativa_4"]
percentual_executado_nota_reestimativa_1 = limite["percentual_executado_nota_reestimativa_1"]
percentual_executado_nota_reestimativa_2 = limite["percentual_executado_nota_reestimativa_2"]
percentual_executado_nota_reestimativa_3 = limite["percentual_executado_nota_reestimativa_3"]
percentual_executado_nota_reestimativa_4 = limite["percentual_executado_nota_reestimativa_4"]
fonte_500_reestimativa_1 = limite["fonte_500_reestimativa_1"]
fonte_501_reestimativa_1 = limite["fonte_501_reestimativa_1"]
fonte_761_reestimativa_1 = limite["fonte_761_reestimativa_1"]
saldo_disponivel_fonte_500 = limite["saldo_disponivel_fonte_500"]
saldo_disponivel_fonte_501 = limite["saldo_disponivel_fonte_501"]
saldo_disponivel_fonte_761 = limite["saldo_disponivel_fonte_761"]
percentual_executado_fonte_500 = limite["percentual_executado_fonte_500"]
percentual_executado_fonte_501 = limite["percentual_executado_fonte_501"]
percentual_executado_fonte_761 = limite["percentual_executado_fonte_761"]
valor_utilizado_fonte_500 = limite["valor_utilizado_fonte_500"]
valor_utilizado_fonte_501 = limite["valor_utilizado_fonte_501"]
valor_utilizado_fonte_761 = limite["valor_utilizado_fonte_761"]

with st.container():

    with st.container():

        df = func_load_base_credito_sop_geo()

        df['Valor'] = df['Valor'].astype(float) 


    with tabs2:
            
        with st.container():

            col1, col2 = st.columns([0.9, 0.1])
            with col1:

                titulos_pagina(" Valores utilizados da NR", font_size="1.9em", text_color="#3064AD", icon='<i class="fas fa-balance-scale"></i>' )

            with col2:
                mostrar_info = st.toggle("ℹ️", key="mostrar_tooltips")

            indicadores = {
                "1° NR": nota_reestimativa_1,
                "Valor Utilizado 1° NR": valor_utilizado_nota_restimativa_1,
                "Saldo Disponível 1° NR": saldo_disponivel_nota_reestimativa_1
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


        indicadores = {
            "Percentual Utilizado NR 1": percentual_executado_nota_reestimativa_1,
        }

        cores_financas = ["#095AA2", "#095AA2", "#095AA2"]

        with st.container():

            fonte_infos = [
                {
                    "nome": "Fonte 500",
                    "limite": fonte_500_reestimativa_1,
                    "utilizado": valor_utilizado_fonte_500,
                    "saldo": saldo_disponivel_fonte_500,
                    "Percentual (%)": percentual_executado_fonte_500
                },
                {
                    "nome": "Fonte 501",
                    "limite": fonte_501_reestimativa_1,
                    "utilizado": valor_utilizado_fonte_501,
                    "saldo": saldo_disponivel_fonte_501,
                    "Percentual (%)": percentual_executado_fonte_501    
                },
                {
                    "nome": "Fonte 761",
                    "limite": fonte_761_reestimativa_1,
                    "utilizado": valor_utilizado_fonte_761,
                    "saldo": saldo_disponivel_fonte_761,
                    "Percentual (%)": percentual_executado_fonte_761
                }
            ]

            for idx, fonte in enumerate(fonte_infos):
                st.markdown(
                    f"<div style='display:flex; gap:10px; margin-bottom:8px;'>"
                    f"<div style='background-color:#095aa2; padding:10px 12px; border-radius:10px; color:white; min-width:240px; text-align:center; font-size:13px;'>"
                    f"<b>{fonte['nome']} - Limite</b><br>{formatar_valor(fonte['limite'])}</div>"
                    f"<div style='background-color:#1976d2; padding:10px 12px; border-radius:10px; color:white; min-width:240px; text-align:center; font-size:13px;'>"
                    f"<b>{fonte['nome']} - Utilizado</b><br>{formatar_valor(fonte['utilizado'])}</div>"
                    f"<div style='background-color:#43a047; padding:10px 12px; border-radius:10px; color:white; min-width:240px; text-align:center; font-size:13px;'>"
                    f"<b>{fonte['nome']} - Disponível</b><br>{formatar_valor(fonte['saldo'])}</div>"
                    f"<div style='background-color:#fbc02d; padding:10px 12px; border-radius:10px; color:white; min-width:240px; text-align:center; font-size:13px;'>"
                    f"<b>{fonte['nome']} - Percentual (%)</b><br>{fonte['Percentual (%)']:.2f}%</div>"
                    f"</div>",
                    unsafe_allow_html=True
                )
            
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



# rotina_envio_email_ted()

rodape_desenvolvedor()