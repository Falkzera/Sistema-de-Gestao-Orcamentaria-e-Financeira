import streamlit as st
import pandas as pd
from utils.confeccoes.formatar import (
    digitacao,
    titulo_dinamico,mostrar_tabela_pdf, 
    inserir_imagem_centrada_relatorio,
    cabecalho_dinamico
)


from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
import re
import tempfile
from weasyprint import HTML
import markdown
import tempfile

def gerar_pdf_weasy_ata_cpof(conteudo_pdf, nome_arquivo="relatorio.pdf"):
    # Juntar o conteúdo e converter markdown → HTML
    html_conteudo = "\n".join(conteudo_pdf)  # conteúdo já é HTML, não precisa de conversão
    html_final = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <style>

            /* Define a página */
            @page {{
                size: A3;
                margin: 1cm 0.5cm 1cm 0.5cm;  /* topo, direita, inferior, esquerda */
                
                @bottom-right {{
                    font-family: 'Times New Roman', serif;
                    content: "Página " counter(page);
                    font-size: 10pt;
                }}
            }}

            body {{
                font-family: 'Times New Roman', serif;
                font-size: 12pt;
                line-height: 1.5;
                color: #000;
                text-align: justify;
            }}

            h1 {{
                text-align: center;
                font-size: 20pt;
                font-weight: bold;
                margin-top: 0;
                margin-bottom: 20px;
            }}

            h2 {{
                font-size: 16pt;
                font-weight: bold;
                margin-top: 30px;
                margin-bottom: 15px;
            }}

            h3 {{
                font-size: 14pt;
                font-weight: bold;
                margin-top: 20px;
                margin-bottom: 10px;
            }}

            p {{
                text-indent: 1.25cm;
                margin: 0 0 12pt 0;
            }}

            strong {{
                font-weight: bold;
            }}

            em {{
                font-style: italic;
            }}

        </style>
    </head>
    <body>
        {html_conteudo}
    </body>
    </html>
    """

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as f:
        HTML(string=html_final).write_pdf(f.name)
        return f.name


with st.container():  # LIMPAR A SESSÃO PARA OS GRÁFICOS E TABELS

    if "conteudo_pdf" in st.session_state and not st.session_state.get("gerando_pdf", False):
        del st.session_state["conteudo_pdf"]

    if not st.session_state.get("gerando_pdf", False):
        st.session_state["contador_quadro"] = 1
        st.session_state["contador_grafico"] = 1

with st.container():  # ALOCAÇÃO DO DATAFRAME

    def montar_ata(df, lista_interessados, corpo_ata, numero_reuniao):

        # Imagem do TOPO
        inserir_imagem_centrada_relatorio('https://upload.wikimedia.org/wikipedia/commons/5/5c/Bras%C3%A3o_do_Estado_de_Alagoas.svg', largura=75, altura=75)

        # Cabeçalho
        cabecalho_dinamico(f"""
            <div style="text-align:center; font-family: 'Times New Roman', Times, serif; line-height: 1.1;">
                <p><b>ESTADO DE ALAGOAS</b></p>
                <p><b>SECRETARIA DE ESTADO DO PLANEJAMENTO, GESTÃO E PATRIMÔNIO</b></p>
                <p>Comitê de Programação Orçamentária e Financeira<br>
                Rua Dr. Cincinato Pinto, 503, - Bairro Centro, Maceió/AL, CEP 57020-050<br>
                Telefone: (82) 3315-1823 - www.seplag.al.gov.br</p>
                <p><b>Ata de Reunião</b></p>
                <p><b>ATA DA {numero_reuniao}ª REUNIÃO DO ANO 2025 DO COMITÊ DE PROGRAMAÇÃO ORÇAMENTÁRIA E FINANCEIRA</b></p>
            </div>
            """)
        
        # Corpo da Ata
        digitacao(corpo_ata)

        #  Lista de interessados
        titulo_dinamico("### INTERESSADO:")
        if len(lista_interessados) > 1:
            lista_formatada = ', '.join(lista_interessados[:-1]) + ' e ' + lista_interessados[-1]
        elif lista_interessados:
            lista_formatada = lista_interessados[0]
        else:
            lista_formatada = ''
        digitacao(f"{lista_formatada}.")

        # Deliberação padrão
        titulo_dinamico("### DELIBERAÇÃO:")
        digitacao("Deliberação acerca da disposição contida no art. 42, do Decreto Estadual n° 100.533/2025, de 07 de JANEIRO de 2025, no que concerne as \
        despesas públicas decorrentes de atividades institucionais tais como para as atividades assinaladas no referido artigo, onde preconiza que em casos \
        excepcionais, os mesmos, deverão ser encaminhados com a devida justificativa no formulário padrão de aprovação para apreciação e deliberação \
        do CPOF. Por unanimidade, os integrantes do Comitê presentes deliberaram os processos abaixo:")

        # Tabela dos processos
        mostrar_tabela_pdf(df)
