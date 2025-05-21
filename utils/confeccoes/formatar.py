import re
import base64
import uuid
import tempfile
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from num2words import num2words
from utils.ui.dataframe import mostrar_tabela


def formatar_valor(valor, casas_decimais=2):
    negativo = valor < 0  
    valor = abs(valor)  
    
    if valor >= 1_000_000_000 and valor < 1_000_000_000_000:
        valor_formatado = valor 
    elif valor >= 1_000_000 and valor < 1_000_000_000:
        valor_formatado = valor 
    elif valor >= 1_000 and valor < 1_000_000:
        valor_formatado = valor 
    else:
        valor_formatado = valor

    numero_formatado = f"{valor_formatado:.{casas_decimais}f}"
    parte_inteira, parte_decimal = numero_formatado.split(".")
    parte_inteira_formatada = ".".join([parte_inteira[max(i - 3, 0):i] for i in range(len(parte_inteira) % 3, len(parte_inteira) + 1, 3) if i])

    resultado = f"R$ {'-' if negativo else ''}{parte_inteira_formatada},{parte_decimal}".strip()

    return resultado


def formatar_valor_arredondado(valor, casas_decimais=2):
    negativo = valor < 0  
    valor = abs(valor)  
    
    if valor >= 1_000_000_000 and valor < 1_000_000_000_000:
        valor_formatado = valor / 1_000_000_000
        sufixo = "Bi"
    elif valor >= 1_000_000 and valor < 1_000_000_000:
        valor_formatado = valor / 1_000_000
        sufixo = "Mi"
    elif valor >= 1_000 and valor < 1_000_000:
        valor_formatado = valor / 1_000
        sufixo = "mil"
    else:
        valor_formatado = valor
        sufixo = ""

    numero_formatado = f"{valor_formatado:.{casas_decimais}f}"
    parte_inteira, parte_decimal = numero_formatado.split(".")
    parte_inteira_formatada = ".".join([parte_inteira[max(i - 3, 0):i] for i in range(len(parte_inteira) % 3, len(parte_inteira) + 1, 3) if i])

    resultado = f"R$ {'-' if negativo else ''}{parte_inteira_formatada},{parte_decimal} {sufixo}".strip()

    return resultado

def formatar_valor2(valor):
    return f"{valor:.2f}".replace(".", ",") + "%"


def formatar_valor_sem_cifrao(valor, casas_decimais=2):
    negativo = valor < 0  
    valor = abs(valor)  
    
    if valor >= 1_000_000_000 and valor < 1_000_000_000_000:
        valor_formatado = valor 
    elif valor >= 1_000_000 and valor < 1_000_000_000:
        valor_formatado = valor 
    elif valor >= 1_000 and valor < 1_000_000:
        valor_formatado = valor 
    else:
        valor_formatado = valor

    numero_formatado = f"{valor_formatado:.{casas_decimais}f}"
    parte_inteira, parte_decimal = numero_formatado.split(".")
    parte_inteira_formatada = ".".join([parte_inteira[max(i - 3, 0):i] for i in range(len(parte_inteira) % 3, len(parte_inteira) + 1, 3) if i])

    resultado = f"{'-' if negativo else ''}{parte_inteira_formatada},{parte_decimal}".strip()

    return resultado



def digitacao(texto, acumular_pdf=True, mostrar_na_tela=False):
    """
    Adiciona texto ao PDF (sempre) e opcionalmente exibe no Streamlit.

    Args:
        texto (str): O conteúdo textual a ser usado.
        acumular_pdf (bool): Se True, adiciona ao conteúdo do PDF.
        mostrar_na_tela (bool): Se True, renderiza na interface do app. Padrão é False.
    """
    if mostrar_na_tela:
        st.markdown(
            f"<div style='text-align: justify; font-size: 22px;'>{texto}</div>",
            unsafe_allow_html=True
        )

    if acumular_pdf:
        if "conteudo_pdf" not in st.session_state:
            st.session_state["conteudo_pdf"] = []
        st.session_state["conteudo_pdf"].append(
            f"<p style='line-height: 1.1; margin-bottom: 6px;'>{texto}</p>"
        )

def titulo_dinamico(titulo_markdown, acumular_pdf=True, mostrar_na_tela=False):
    """
    Adiciona título ao PDF (sempre) e opcionalmente exibe no Streamlit.

    Args:
        titulo_markdown (str): Título em formato markdown (ex: "### Meu Título")
        acumular_pdf (bool): Se True, acumula no conteúdo do PDF
        mostrar_na_tela (bool): Se True, renderiza no app (padrão: False)
    """
    if mostrar_na_tela:
        st.markdown(titulo_markdown)

    match = re.match(r"(#+)\s+(.*)", titulo_markdown.strip())
    if not match:
        return 

    hashes, texto = match.groups()
    nivel = min(len(hashes), 6)

    if acumular_pdf:
        if "conteudo_pdf" not in st.session_state:
            st.session_state["conteudo_pdf"] = []
        st.session_state["conteudo_pdf"].append(f"<h{nivel}>{texto}</h{nivel}>")

def cabecalho_dinamico(cabecalho_html, acumular_pdf=True, mostrar_na_tela=False):
    """
    Adiciona conteúdo HTML ao PDF (sempre) e opcionalmente exibe no Streamlit.

    Args:
        cabecalho_html (str): Conteúdo HTML já formatado para o cabeçalho.
        acumular_pdf (bool): Se True, acumula no conteúdo do PDF.
        mostrar_na_tela (bool): Se True, renderiza no app (padrão: False).
    """
    if mostrar_na_tela:
        st.markdown(cabecalho_html, unsafe_allow_html=True)

    if acumular_pdf:
        if "conteudo_pdf" not in st.session_state:
            st.session_state["conteudo_pdf"] = []
        st.session_state["conteudo_pdf"].append(cabecalho_html)

def inserir_imagem_centrada_relatorio(caminho_imagem, largura=None, altura=None, acumular_pdf=True, mostrar_na_tela=False):
    """
    Gera HTML da imagem centralizada (ajustada para a direita), insere no conteúdo do PDF (acumula),
    e opcionalmente exibe no Streamlit.

    Args:
        caminho_imagem (str): Caminho ou URL da imagem.
        largura (int, opcional): Largura da imagem em pixels.
        altura (int, opcional): Altura da imagem em pixels.
        acumular_pdf (bool): Se True, adiciona ao conteúdo do PDF.
        mostrar_na_tela (bool): Se True, exibe no Streamlit.
    """
    style_size = ""
    if largura:
        style_size += f"width:{largura}px;"
    if altura:
        style_size += f"height:{altura}px;"

    html_img = f"""
    <div style="display: flex; justify-content: center; align-items: center; width: 100%;">
        <div style="width: fit-content; margin-left: 40px;">
        <img src="{caminho_imagem}" style="{style_size} display: block; margin: auto;" />
        </div>
    </div>
    """

    if mostrar_na_tela:
        st.markdown(html_img, unsafe_allow_html=True)

    if acumular_pdf:
        if "conteudo_pdf" not in st.session_state:
            st.session_state["conteudo_pdf"] = []
        st.session_state["conteudo_pdf"].append(html_img)

def gerar_relatorio_origem_recursos(df_filtrado, origem_recurso, n=3):

    df_origem_recurso = df_filtrado[df_filtrado['Origem de Recursos'] == origem_recurso]
    maiores_montantes = df_origem_recurso.groupby('Órgão (UO)')['Valor'].sum().nlargest(n)

    for idx, (orgao, valor) in enumerate(maiores_montantes.items()):
        df_maior_montante = df_origem_recurso[df_origem_recurso['Órgão (UO)'] == orgao]
        solicitacoes = df_maior_montante['Nº do Processo'].tolist()
        fontes = df_maior_montante['Fonte de Recursos'].unique()
        grupos_despesas = df_maior_montante['Grupo de Despesas'].unique()

        solicitacoes_texto = ', '.join(solicitacoes)
        fontes_texto = ', '.join(fontes)
        grupos_despesas_texto = ', '.join(map(str, grupos_despesas))

        if idx == 0:
            introducao = "O maior montante em relação à quantia foi"
        elif idx == 1:
            introducao = "Em seguida, o segundo maior montante foi"
        else:
            introducao = "Por fim, o terceiro maior montante foi"

        digitacao(
            f'''{introducao} da {orgao}, com um valor total de {formatar_valor(valor)} ({por_extenso_reais(valor)}), 
            divididos em {len(solicitacoes)} ({por_extenso(len(solicitacoes))}) solicitações, sendo elas:
            {solicitacoes_texto}, presentes na fonte {fontes_texto} e grupos de despesas {grupos_despesas_texto}.'''
        )

def por_extenso(valor):
    """
    Converte um número em palavras por extenso em português.

    Args:
    valor (int, float): Número a ser convertido para palavras.

    Returns:
    str: O número por extenso em português.
    """
    return num2words(valor, lang='pt')

def por_extenso_reais(valor):
    """
    Converte um valor monetário em reais (float ou int) para texto por extenso.
    Suporta valores até trilhões com centavos.
    """
    inteiro = int(valor)
    centavos = round((valor - inteiro) * 100)

    partes = []

    unidades = [
        (1_000_000_000_000, "trilhão", "trilhões"),
        (1_000_000_000, "bilhão", "bilhões"),
        (1_000_000, "milhão", "milhões"),
        (1_000, "mil", "mil"),
        (1, "", "")
    ]

    restante = inteiro

    for base, singular, plural in unidades:
        if restante >= base:
            valor_parte = restante // base
            restante = restante % base

            extenso = num2words(valor_parte, lang='pt')

            if base == 1:
                partes.append(extenso)
            elif valor_parte == 1:
                partes.append(f"{extenso} {singular}")
            else:
                partes.append(f"{extenso} {plural}")

    reais_extenso = " ".join(partes) + (" real" if inteiro == 1 else " reais")

    if centavos > 0:
        centavos_extenso = num2words(centavos, lang='pt')
        centavos_texto = "centavo" if centavos == 1 else "centavos"
        return f"{reais_extenso} e {centavos_extenso} {centavos_texto}"
    else:
        return reais_extenso

def mes_por_extenso(mes_num):
    """
    Converte o número do mês para o nome do mês por extenso.
    
    Args:
    mes_num (int): Número do mês (1 a 12).
    
    Returns:
    str: Nome do mês por extenso.
    """
    meses = [
        "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
        "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
    ]
    
    if 1 <= mes_num <= 12:
        return meses[mes_num - 1] 
    else:
        return "Mês inválido" 

def inserir_grafico_pdf(fig, titulo):
    
    nome_arquivo = f"{uuid.uuid4()}.png"

    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
        fig.write_image(tmpfile.name, format="png", scale=3)
        caminho_imagem = tmpfile.name

    if "contador_grafico" not in st.session_state:
        st.session_state["contador_grafico"] = 1

    num = st.session_state["contador_grafico"]
    st.session_state["contador_grafico"] += 1

    titulo_html = f"""
    <div style="text-align: center; font-family: Times New Roman, serif; font-size: 12pt; font-weight: bold; margin-bottom: 5px;">
        Gráfico {num} - {titulo}
    </div>
    """

    fonte_html = """
        <div class='fonte'>
            <strong>Fonte:</strong> elaboração própria a partir de dados de processos do SEI e SIAFE - 2025.
        </div>
        <div style="height: 18px;"></div> <!-- Espaço abaixo da fonte -->
        """

    with open(caminho_imagem, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode()

    imagem_html = f"""
    <div style="text-align: center; margin: 20px 0;">
        <img src="data:image/png;base64,{encoded}" style="width:99%; max-width:600px;" />
    </div>
    """

    if "conteudo_pdf" not in st.session_state:
        st.session_state["conteudo_pdf"] = []

    bloco_html = f"""
    <div style="page-break-inside: avoid; margin-bottom: 20px;">
        {titulo_html}
        {imagem_html}
        {fonte_html}
    </div>
    """

    st.session_state["conteudo_pdf"].append(bloco_html)

def mostrar_tabela_pdf(df, nome_tabela=None, mostrar_na_tela=False):
    """
    Adiciona uma tabela formatada ao PDF, e opcionalmente exibe no app com AgGrid.

    Args:
        df (pd.DataFrame): Tabela a ser renderizada.
        nome_tabela (str): Título da tabela (será usado no PDF e opcionalmente na interface).
        mostrar_na_tela (bool): Se True, mostra no app com estilo; padrão é False.
    """

    if mostrar_na_tela:
        from utils.ui.dataframe import mostrar_tabela
        mostrar_tabela(df, nome_tabela=nome_tabela)

    titulo = f"<h4>{nome_tabela}</h4>" if nome_tabela else ""

    html_tabela = df.to_html(index=False, border=0, justify="center")

    if "conteudo_pdf" not in st.session_state:
        st.session_state["conteudo_pdf"] = []

    st.session_state["conteudo_pdf"].append(titulo + html_tabela)

def mostrar_tabela_pdf(df, nome_tabela=None):
    
    mostrar_tabela(df, nome_tabela=nome_tabela)

    estilo_tabela = """
    <style>
        table {
            border-collapse: collapse;
            width: 100%;
            margin-top: 10px;
            margin-bottom: 5px;
            font-family: 'Times New Roman', serif;
            font-size: 10pt;
            page-break-inside: auto;
        }
        th, td {
            border: 2px solid #000;
            padding: 2px 10px;
            text-align: center;
            vertical-align: middle;
        }
        th {
            background-color: #f2f2f2;
            font-weight: bold;
        }
        tr {
            page-break-inside: avoid;
            page-break-after: auto;
        }
        .quadro-titulo {
            text-align: center;
            font-size: 12pt;
            font-weight: bold;
            margin-top: 24px;
            margin-bottom: 8px;
        }
        .fonte {
            text-align: center;
            font-size: 10pt;
            font-weight: normal;
            margin-top: 6px;
        }
    </style>
    """
#customers tr:nth-child(even){background-color: #f2f2f2;}

#customers tr:hover {background-color: #ddd;}
    # Numeração de quadros (mantida na sessão)
    if "contador_quadro" not in st.session_state:
        st.session_state.contador_quadro = 1
    numero_quadro = st.session_state.contador_quadro
    st.session_state.contador_quadro += 1

    titulo_html = f"<div class='quadro-titulo'>Quadro {numero_quadro}: {nome_tabela}</div>" if nome_tabela else ""
    html_tabela = df.to_html(index=False, border=0, justify="center")
    fonte_html = """
        <div class='fonte'>
            <strong>Fonte:</strong> elaboração própria a partir de dados de processos do SEI e SIAFE - 2025.
        </div>
        <div style="height: 18px;"></div> <!-- Espaço abaixo da fonte -->
        """

    bloco_html = f"""
    {estilo_tabela}
    {titulo_html}
    {html_tabela}
    {fonte_html}
    """

    if "conteudo_pdf" not in st.session_state:
        st.session_state["conteudo_pdf"] = []

    st.session_state["conteudo_pdf"].append(bloco_html)

def gerar_grafico_pizza(labels, values, titulo_pdf="Gráfico: Pizza", cores=None, mostrar_na_tela=False):
    if cores is None:
        cores = [
            "#095AA2", "#0A6BB5", "#0B7CC8", "#0C8DDB", "#0D9EEE",
            "#E0E0E0", "#D0D0D0", "#C0C0C0", "#B0B0B0", "#A0A0A0"
        ]

    fig = go.Figure(
        data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.4,
            marker=dict(colors=cores),
            textinfo="percent",
            textfont=dict(
                family="Times New Roman, serif",
                size=20,
            ),
            insidetextorientation="radial"
        )]
    )

    fig.update_layout(
        title=None,
        font=dict(
            family="Times New Roman, serif",
            size=20,
            color="black"
        ),
        uniformtext_minsize=20,
        uniformtext_mode='hide',
        margin=dict(t=30, b=30, l=30, r=30),
        height=500,
        showlegend=True,
        legend=dict(
            orientation="h",
            y=-0.15,
            x=0.5,
            xanchor="center",
            font=dict(
                family="Times New Roman, serif",
                size=20
            )
        )
    )

    if mostrar_na_tela:
        st.plotly_chart(fig, use_container_width=True)
    inserir_grafico_pdf(fig, titulo=titulo_pdf)



def gerar_grafico_linha(x, y, titulo_pdf="Gráfico: Linha", nomes_series=None, cores=None, texto_formatado=None, mostrar_na_tela=False, empilhar=False, fonte="Arial, sans-serif"):
    """
    Aceita tanto uma série única quanto múltiplas séries de linhas.
    - x: lista ou lista de listas (para múltiplas séries)
    - y: lista ou lista de listas
    - nomes_series: lista com o nome de cada série (para múltiplas séries)
    - texto_formatado: lista ou lista de listas (opcional)
    """

    fig = go.Figure()

    # Se for uma única série (x e y como listas), transforma tudo em listas de uma série só
    if not isinstance(x[0], (list, pd.Series)):
        x = [x]
        y = [y]
        texto_formatado = [texto_formatado] if texto_formatado else [None]
        nomes_series = nomes_series if nomes_series else ["Série 1"]
    else:
        # Se múltiplas séries, verifica consistência de nomes
        texto_formatado = texto_formatado if texto_formatado else [None] * len(x)
        if not nomes_series:
            nomes_series = [f"Série {i+1}" for i in range(len(x))]

    # Define cores padrão se não forem passadas
    cores_padrao = [
        "#095AA2", "#0A6BB5", "#0B7CC8", "#0C8DDB", "#0D9EEE",
        "#E0E0E0", "#D0D0D0", "#C0C0C0", "#B0B0B0", "#A0A0A0"
    ]
    if not cores:
        cores = cores_padrao[:len(x)]

    # Adiciona as séries ao gráfico
    for i in range(len(x)):
        trace_args = dict(
            x=x[i],
            y=y[i],
            mode='lines',
            name=nomes_series[i],
            line=dict(width=3, color=cores[i % len(cores)]),
            marker=dict(size=6),
            text=texto_formatado[i],
            textposition='bottom center',
        )

        if empilhar:
            trace_args["stackgroup"] = 'one'

        fig.add_trace(go.Scatter(**trace_args))

    # Layout padrão
    fig.update_layout(
        title=None,
        font=dict(family=fonte, size=16, color="black"),
        margin=dict(t=60, b=80, l=60, r=40),  # aumente l (left) e b (bottom) se quiser mais espaço
        height=500,
        xaxis=dict(
            title=None,
            tickfont=dict(family=fonte, size=20),
            showgrid=False,
            showticklabels=True,
            dtick="M6",  # mostra ticks a cada 3 meses
            tickformat="%m/%y",  # formata como mes/ano
            ticklabelmode="period",
            title_standoff=30,  # aumenta o afastamento do título do eixo x
        ),
        yaxis=dict(
            title=None,
            tickfont=dict(family=fonte, size=20),
            showgrid=True,
            showticklabels=True,
            automargin=True,
            title_standoff=30,  # aumenta o afastamento do título do eixo y
            tickformat=".0f",  # mostra apenas números inteiros, sem casas decimais
        ),
        legend=dict(
            font=dict(size=20),
            orientation='h',  # legenda na horizontal
            x=0.5,
            xanchor='center',
            y=-0.1
        )
    )

    if mostrar_na_tela:
        st.plotly_chart(fig, use_container_width=True)

    inserir_grafico_pdf(fig, titulo=titulo_pdf)



def gerar_grafico_barra(x, y, titulo_pdf="Gráfico: Barras", cores=None, texto_formatado=None, mostrar_na_tela=False):

    df = pd.DataFrame({'x': x, 'y': y})
    df = df.sort_values(by='y', ascending=False).reset_index(drop=True)

    if len(df) > 5:
        top5 = df.iloc[:5]
        outros = df.iloc[5:]
        total_outros = outros['y'].sum()
        outros_row = pd.DataFrame({'x': ['Outros'], 'y': [total_outros]})
        df = pd.concat([top5, outros_row], ignore_index=True)

    df_sem_outros = df[df['x'] != 'Outros'].sort_values(by='y', ascending=False)
    df_outros = df[df['x'] == 'Outros']
    df = pd.concat([df_sem_outros, df_outros], ignore_index=True)

    x = df['x']
    y = df['y']
    # texto_formatado = texto_formatado if texto_formatado else y

    if cores is None:
        cores_padrao = [
            "#095AA2", "#0A6BB5", "#0B7CC8", "#0C8DDB", "#0D9EEE",
            "#E0E0E0", "#D0D0D0", "#C0C0C0", "#B0B0B0", "#A0A0A0"
        ]
        cores = cores_padrao[:len(x)]
        if len(cores) < len(x):
            cores += ["#AAAAAA"] * (len(x) - len(cores))  # preenche se faltar cor

    fig = go.Figure(
        data=[go.Bar(
            x=x,
            y=y,
            marker=dict(color=cores),
            text=texto_formatado,
            textposition="outside",
            textangle=0
        )]
    )

    fig.update_traces(
        textfont=dict(
            family="Times New Roman, serif",
            size=14,
            color="black"
        )
    )

    fig.update_layout(
        title=None,
        font=dict(family="Times New Roman, serif", size=14, color="black"),
        uniformtext_minsize=14,
        uniformtext_mode='show',
        margin=dict(t=60, b=100, l=40, r=20),
        height=600,
        xaxis=dict(
            title=None,
            tickfont=dict(family="Times New Roman, serif", size=14),
            showgrid=False,
            showticklabels=True,
            tickangle=0,
            automargin=True
        ),
        yaxis=dict(
            title=None,
            tickfont=dict(family="Times New Roman, serif", size=14),
            showgrid=False,
            showticklabels=True,
        ),
    )

    if mostrar_na_tela:
        st.plotly_chart(fig, use_container_width=True)

    inserir_grafico_pdf(fig, titulo=titulo_pdf)


def gerar_relatorio_origem_recurso_com_graficos(df_filtrado, origem_recurso, n=3, tipo_grafico='nenhum'):

    df_origem_recurso = df_filtrado[df_filtrado['Origem de Recursos'] == origem_recurso]

    maiores_montantes = df_origem_recurso.groupby('Órgão (UO)')['Valor'].sum().nlargest(n)

    qtd_orgaos = df_origem_recurso['Órgão (UO)'].nunique()
    qntd_valor_total = df_origem_recurso['Valor'].sum()
    fontes_recurso = df_origem_recurso['Fonte de Recursos'].unique()
    
    fontes_recurso_texto = ', '.join(fontes_recurso)

    # Gerando o texto detalhado
    if qtd_orgaos == 0:
        digitacao(
            f'''Não foram encontrados órgãos solicitantes para a origem de recurso {origem_recurso}.'''
        )
        return
    digitacao(
        f'''Dos {qtd_orgaos} órgãos solicitantes, o montante total de créditos sem cobertura foi de {formatar_valor(qntd_valor_total)} ({por_extenso_reais(qntd_valor_total)}), 
        divididos entre as fontes de recursos: {fontes_recurso_texto}.'''
    )

    df_origem_recurso_tabela = df_origem_recurso[['Órgão (UO)', 'Nº do Processo', 'Fonte de Recursos', 'Grupo de Despesas', 'Valor']] \
        .sort_values(by=['Órgão (UO)','Valor' ], ascending=[False, False]).copy()

    df_origem_recurso_tabela['Valor'] = df_origem_recurso_tabela['Valor'].apply(formatar_valor)

    mostrar_tabela_pdf(
        df_origem_recurso_tabela,
        nome_tabela=f"Tabela de Dados - {origem_recurso}"
    )

 
    for idx, (orgao, valor) in enumerate(maiores_montantes.items()):

        df_maior_montante = df_origem_recurso[df_origem_recurso['Órgão (UO)'] == orgao]
        solicitacoes = df_maior_montante['Nº do Processo'].tolist()
        fontes = df_maior_montante['Fonte de Recursos'].unique()
        grupos_despesas = df_maior_montante['Grupo de Despesas'].unique()

        solicitacoes_texto = ', '.join(solicitacoes)
        fontes_texto = ', '.join(fontes)
        grupos_despesas_texto = ', '.join(map(str, grupos_despesas))

        if idx == 0:
            introducao = "O maior montante em relação à quantia foi"
        elif idx == 1:
            introducao = "Em seguida, o segundo maior montante foi"
        else:
            introducao = "Por fim, o terceiro maior montante foi"

        digitacao(
            f'''{introducao} da {orgao}, com um valor total de {formatar_valor(valor)} ({por_extenso_reais(valor)}), 
            divididos em {len(solicitacoes)} ({por_extenso(len(solicitacoes))}) solicitações, sendo elas:
            {solicitacoes_texto}, presentes na fonte {fontes_texto} e grupos de despesas {grupos_despesas_texto}.'''
        )

    orgaos_por_valor = df_origem_recurso.groupby('Órgão (UO)')['Valor'].sum().sort_values(ascending=False)

    azul_tons = [
    "#095AA2", "#0A6BB5", "#0B7CC8", "#0C8DDB", "#0D9EEE",
    "#E0E0E0", "#D0D0D0", "#C0C0C0", "#B0B0B0", "#A0A0A0"]

    if tipo_grafico == 'pizza':

        gerar_grafico_pizza(
            labels=orgaos_por_valor.index,
            values=orgaos_por_valor.values,
            titulo_pdf=f"Solicitação de Crédito por Órgão ({origem_recurso})",
            cores=azul_tons
        )

    elif tipo_grafico == 'barra':

        valores_formatados = [formatar_valor_arredondado(valor) for valor in orgaos_por_valor.values]

        gerar_grafico_barra(
            x=orgaos_por_valor.index,
            y=orgaos_por_valor.values,
            cores=azul_tons[:len(orgaos_por_valor)],
            texto_formatado=valores_formatados,
            titulo_pdf=f"Solicitação de Crédito por Órgão ({origem_recurso})"
        )

    elif tipo_grafico == 'nenhum':
        print("Nenhum gráfico foi gerado.")

def formatar_valor_br(valor_str: str) -> str:
    """
    Formata para padrão brasileiro:
    - Insere ponto como separador de milhar
    - Usa vírgula como separador decimal
    Ex: '1234567.89' → '1.234.567,89'
    """
    try:
        # Remove tudo que não for número ou vírgula
        valor_normalizado = valor_str.replace('.', '').replace(',', '.')
        valor_float = float(valor_normalizado)
        return f"{valor_float:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    except:
        return valor_str  # Retorna original se erro



def maior_pico_producao(df):
    """
    Retorna uma string com o valor, ano e mês da maior produção de um DataFrame.

    Parâmetros:
        df (pd.DataFrame): DataFrame contendo as colunas 'DATA' (datetime) e 'producao'.
        nome_df (str): Nome do DataFrame para identificação.

    Retorna:
        str: String formatada com os resultados.
    """
    max_row = df.loc[df['PRODUÇÃO'].idxmax()]  # Encontra a linha de maior produção
    ano = max_row['DATA'].year
    mes = max_row['DATA'].month
    return f"{mes_por_extenso(mes)} de {ano}, chegando a um montante de {formatar_valor_sem_cifrao(max_row['PRODUÇÃO'])} ({por_extenso(max_row['PRODUÇÃO'])})"

def media_producao(df):
    """
    Retorna a média de produção de um DataFrame.

    Parâmetros:
        df (pd.DataFrame): DataFrame contendo as colunas 'DATA' (datetime) e 'producao'.
        nome_df (str): Nome do DataFrame para identificação.

    Retorna:
        str: String formatada com o resultado.
    """
    media = int(df['PRODUÇÃO'].mean())
    return f"{formatar_valor_sem_cifrao(media)} ({por_extenso(media)})"

def menor_pico_producao(df):
    """
    Retorna uma string com o valor, ano e mês da menor produção de um DataFrame.

    Parâmetros:
        df (pd.DataFrame): DataFrame contendo as colunas 'DATA' (datetime) e 'producao'.
        nome_df (str): Nome do DataFrame para identificação.

    Retorna:
        str: String formatada com os resultados.
    """
    min_row = df.loc[df['PRODUÇÃO'].idxmin()]
    ano = min_row['DATA'].year
    mes = min_row['DATA'].month

    return f"{mes_por_extenso(mes)} de {ano}, chegando a um montante de {formatar_valor_sem_cifrao(min_row['PRODUÇÃO'])} ({por_extenso(min_row['PRODUÇÃO'])})"

def ranking_producao(df):
    """
    Gera um ranking de produção, agrupando por DATA e somando a produção.

    Parâmetros:
        df (pd.DataFrame): DataFrame contendo as colunas 'DATA' (datetime) e 'producao'.
        nome_df (str): Nome do DataFrame para identificação.

    Retorna:
        pd.DataFrame: DataFrame ordenado do maior para o menor valor de produção.
    """
    if 'UNIDADE DA FEDERAÇÃO' in df.columns:

        df_ranking = df.groupby("UNIDADE DA FEDERAÇÃO")["PRODUÇÃO"].sum().reset_index()
        df_ranking = df_ranking.sort_values(by="PRODUÇÃO", ascending=False).reset_index(drop=True)
        df_ranking['PRODUÇÃO'] = df_ranking['PRODUÇÃO'].apply(lambda x: formatar_valor_sem_cifrao(x))
    
    elif 'GRANDE REGIÃO' in df.columns:
        df_ranking = df.groupby("GRANDE REGIÃO")["PRODUÇÃO"].sum().reset_index()
        df_ranking = df_ranking.sort_values(by="PRODUÇÃO", ascending=False).reset_index(drop=True)
        df_ranking['PRODUÇÃO'] = df_ranking['PRODUÇÃO'].apply(lambda x: formatar_valor_sem_cifrao(x))
        
    return df_ranking

def recorte_temporal_ano_passado(df): # MUDEI PARA ANO PRESENTE
    ano_max = df['DATA'].max().year
    df_ano_passado = df[(df['DATA'].dt.year == ano_max)].copy()
    return df_ano_passado



def formatar_valor_usd(valor, casas_decimais=2):
    negativo = valor < 0  
    valor = abs(valor)  
    
    if valor >= 1_000_000_000 and valor < 1_000_000_000_000:
        valor_formatado = valor / 1_000_000_000
        sufixo = "bilhões"
    elif valor >= 1_000_000 and valor < 1_000_000_000:
        valor_formatado = valor / 1_000_000
        sufixo = "milhões"
    elif valor >= 1_000 and valor < 1_000_000:
        valor_formatado = valor / 1_000
        sufixo = "mil"
    else:
        valor_formatado = valor
        sufixo = ""

    numero_formatado = f"{valor_formatado:.{casas_decimais}f}"
    parte_inteira, parte_decimal = numero_formatado.split(".")
    
    parte_inteira_formatada = ".".join([parte_inteira[max(i - 3, 0):i] for i in range(len(parte_inteira) % 3, len(parte_inteira) + 1, 3) if i])

    resultado = f"US$ {'-' if negativo else ''}{parte_inteira_formatada},{parte_decimal} {sufixo}".strip()

    return resultado

def formatar_valor_arredondado_sem_cifrao(valor, casas_decimais=2):
    negativo = valor < 0  
    valor = abs(valor)  
    
    if valor >= 1_000_000_000 and valor < 1_000_000_000_000:
        valor_formatado = valor / 1_000_000_000
        sufixo = "Bi"
    elif valor >= 1_000_000 and valor < 1_000_000_000:
        valor_formatado = valor / 1_000_000
        sufixo = "Mi"
    elif valor >= 1_000 and valor < 1_000_000:
        valor_formatado = valor / 1_000
        sufixo = "mil"
    else:
        valor_formatado = valor
        sufixo = ""

    numero_formatado = f"{valor_formatado:.{casas_decimais}f}"
    parte_inteira, parte_decimal = numero_formatado.split(".")
    parte_inteira_formatada = ".".join([parte_inteira[max(i - 3, 0):i] for i in range(len(parte_inteira) % 3, len(parte_inteira) + 1, 3) if i])

    resultado = f"{'-' if negativo else ''}{parte_inteira_formatada},{parte_decimal} {sufixo}".strip()

    return resultado
