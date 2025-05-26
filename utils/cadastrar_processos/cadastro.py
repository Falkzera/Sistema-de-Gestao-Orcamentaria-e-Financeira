import streamlit as st
import pandas as pd
#mostrar tabela
from utils.ui.dataframe import mostrar_tabela
from utils.opcoes_coluna.deliberacao import opcoes_deliberacao
from utils.opcoes_coluna.situacao import opcoes_situacao
from utils.opcoes_coluna.tipo_despesa import opcoes_tipo_despesa
from utils.opcoes_coluna.orgao_uo import opcoes_orgao_uo
from utils.opcoes_coluna.fonte_recurso import opcoes_fonte_recurso
from utils.opcoes_coluna.grupo_despesa import opcoes_grupo_despesa
from utils.opcoes_coluna.tipo_credito import opcoes_tipo_credito
from utils.opcoes_coluna.contabilizar_limite import opcoes_contabilizar_limite
from utils.opcoes_coluna.origem_recurso import opcoes_origem_recursos
from utils.confeccoes.formatar import formatar_valor_br
from utils.opcoes_coluna.validadores.processo import validar_processamento_campos
from src.salvar_alteracoes import salvar_base


from datetime import datetime
ano_corrente = datetime.now().year

def cadastrar_processos_credito_geo(nome_base, df):
        
    col1, col2, col3 = st.columns(3)

    numero_processo = col1.text_input("Nº do Processo **(Obrigatório)**",placeholder=f"E:00000.0000000000/{ano_corrente}",help=f"Digite o número do processo no formato: E:00000.0000000000/{ano_corrente}")
    numero_processo = str(numero_processo).strip() 

    situacao = col2.selectbox("Situação **(Obrigatório)**",opcoes_situacao,index=None,help="Selecione a situação do processo.", placeholder="Selecione a Situação")

    origem_recursos = col3.selectbox("Origem de Recursos **(Obrigatório)**",opcoes_origem_recursos,index=None,help="Selecione a origem dos recursos.", placeholder="Selecione a Origem de Recursos")


    col1, col2 = st.columns(2)
    orgao_uo = col1.selectbox("Órgão(UO) **(Obrigatório)**",opcoes_orgao_uo,index=None,help="Selecione a Unidade Orçamentária.", placeholder="Selecione a UO")
    contabilizar_limite = col2.selectbox("Contabilizar no Limite? **(Obrigatório)**",opcoes_contabilizar_limite,index=None,help="Selecione se o processo deve ser contabilizado no limite.", placeholder="Selecione Sim ou Não")

    col1, col2, col3 = st.columns(3)
    tipo_credito = col1.selectbox("Tipo de Crédito **(Obrigatório)**",opcoes_tipo_credito,index=None,help="Selecione o tipo de crédito.", placeholder="Selecione o Tipo de Crédito")
    fonte_recurso = col2.selectbox("Fonte de Recrusos **(Obrigatório)**",opcoes_fonte_recurso,index=None,help="Selecione a Unidade Orçamentária.", placeholder="Selecione a Fonte de Recursos")
    grupo_despesa = col3.selectbox("Grupo de Despesas **(Obrigatório)**",opcoes_grupo_despesa,index=None,help="Selecione o grupo de despesa.", placeholder="Selecione um Grupo de Despesas")

    col1, col2 = st.columns(2)
    valor_input = col1.text_input("Valor **(Obrigatório)**", placeholder="Ex: 1.234,56", help="Digite o valor do processo no formato: 1.234,56")
    data_recebimento = col2.text_input("Data de recebimento **(Obrigatório)**", placeholder="DD/MM/AAAA", help="Digite a data de recebimento do processo no formato: DD/MM/AAAA")

    if valor_input and valor_input.isnumeric():
        valor_input = formatar_valor_br(valor_input)

    col1, col2 = st.columns(2)
    objetivo = col1.text_input("Objetivo **(Obrigatório)**", placeholder="Ex: Descrição do objetivo do processo.", help="Digite o objetivo do processo.")
    observacao = col2.text_input("Observação Processual", placeholder="Ex: Digite se houver alguma observação.", help="Digite uma observação ao processo, normalmente utilizado para descrever erros no processo.")

    obs_sop = st.text_area("Opnião Técnica SOP", placeholder="Ex: Opinião técnica da SOP sobre o processo.", help="Digite a opinião da SOP sobre o processo, para instruir a alta gestão.")

    data_publicacao = ''
    numero_decreto = ''

    nao_podem_estar_vazios = [
        situacao,
        origem_recursos,
        orgao_uo,
        numero_processo,
        tipo_credito,
        fonte_recurso,
        grupo_despesa,
        valor_input,
        objetivo,
        data_recebimento, 
        contabilizar_limite   
    ]
    if any(not campo for campo in nao_podem_estar_vazios):
        st.info("⚠️ Preencha todos os campos obrigatórios.")
        st.stop()

    st.write('---')
    if st.button("Cadastrar Processo 📁", use_container_width=True, type="primary", help='Clique para cadastrar o processo na base 📁'):

        # ✅ Valida os campos
        erros, campos_sanitizados = validar_processamento_campos(
            numero_processo,
            valor_input,
            data_recebimento,
            data_publicacao,
            numero_decreto,
            objetivo,
            observacao,
            obs_sop,
        )

        if erros:
            for erro in erros:
                st.error(erro)
            st.stop()

        objetivo_sanitizado = campos_sanitizados['objetivo']
        observacao_sanitizada = campos_sanitizados['observacao']
        obs_sop_sanitizada = campos_sanitizados['obs_sop']

        if numero_processo in df["Nº do Processo"].values:
            st.error("⚠️ Esse processo já foi cadastrado! Veja abaixo:")
            mostrar_tabela(df[df["Nº do Processo"] == numero_processo],altura_max_linhas=99, 
                        nome_tabela="Processo já cadastrado!", mostrar_na_tela=True)
            st.stop()

        else:
            agora = datetime.now()
            novo = pd.DataFrame([{
                "Situação": situacao,
                "Origem de Recursos": origem_recursos,
                "Órgão (UO)": orgao_uo,
                "Nº do Processo": numero_processo,
                "Tipo de Crédito": tipo_credito,
                "Fonte de Recursos": fonte_recurso,
                "Grupo de Despesas": grupo_despesa,
                "Valor": valor_input,
                "Objetivo": objetivo_sanitizado,
                "Observação": observacao_sanitizada,
                "Opnião SOP": obs_sop_sanitizada,
                "Data de Recebimento": data_recebimento,
                "Data de Publicação": data_publicacao,
                "Nº do decreto": numero_decreto,
                "Contabilizar no Limite?": contabilizar_limite,
                "Cadastrado Por": st.session_state.username.title() + ' - ' + agora.strftime("%d/%m/%Y %H:%M:%S"),
            }])

            # TRATAR O VALOR (DE R$ 1.234,56 PARA 1234.56)
            novo["Valor"] = novo["Valor"].apply(
                lambda x: float(x.replace(".", "").replace(",", "."))
            )
            
            nome_base = str(nome_base)
            salvar_base(novo, nome_base)



def cadastrar_processos_cpof(nome_base, df):

    col1, col2, col3 = st.columns(3)

    numero_processo = col1.text_input("Nº do Processo **(Obrigatório)**",placeholder=f"E:00000.0000000000/{ano_corrente}",help=f"Digite o número do processo no formato: E:00000.0000000000/{ano_corrente}")
    numero_processo = str(numero_processo).strip() 
    deliberacao = col2.selectbox("Deliberação **(Obrigatório)**",opcoes_deliberacao,index=None,help="Selecione a deliberação do processo.", placeholder="Selecione a deliberação")
    orgao_uo = col3.selectbox("Órgão (UO) **(Obrigatório)**",opcoes_orgao_uo,index=None,help="Selecione o Órgão(UO).", placeholder="Selecione o Órgão(UO)")


    col1, col2, col3 = st.columns(3)
    tipo_despesa = col1.selectbox("Tipo de Despesa **(Obrigatório)**",opcoes_tipo_despesa,index=None,help="Selecione o Tipo de Despesa.", placeholder="Selecione o Tipo de Despesa")
    fonte_recurso = col2.selectbox("Fonte de Recrusos **(Obrigatório)**",opcoes_fonte_recurso,index=None,help="Selecione a Fonte de Recursos.", placeholder="Selecione a Fonte de Recursos")
    grupo_despesa = col3.selectbox("Grupo de Despesas **(Obrigatório)**",opcoes_grupo_despesa,index=None,help="Selecione o grupo de despesa.", placeholder="Selecione um Grupo de Despesas")

    col1, col2 = st.columns(2)
    valor_input = col1.text_input("Valor **(Obrigatório)**", placeholder="Ex: 1.234,56", help="Digite o valor do processo no formato: 1.234,56")
    data_recebimento = col2.text_input("Data de recebimento **(Obrigatório)**", placeholder="DD/MM/AAAA", help="Digite a data de recebimento do processo no formato: DD/MM/AAAA")

    if valor_input and valor_input.isnumeric():
        valor_input = formatar_valor_br(valor_input)

    col1, col2 = st.columns(2)
    objetivo = col1.text_input("Objetivo **(Obrigatório)**", placeholder="Ex: Objetivos do Pedido do Processo.", help="Objetivos do pedido do processo.")
    observacao = col2.text_input("Observação Processual", placeholder="Ex: Digite se houver alguma observação.", help="Digite uma observação ao processo, normalmente utilizado para descrever erros no processo.")

    data_publicacao = ''
    ata = ''

    nao_podem_estar_vazios = [
        deliberacao,
        tipo_despesa,
        orgao_uo,
        numero_processo,
        fonte_recurso,
        grupo_despesa,
        data_recebimento, 
        valor_input,
        objetivo,
    ]

    if any(not campo for campo in nao_podem_estar_vazios):
        st.info("⚠️ Preencha todos os campos obrigatórios.")
        st.stop()

    st.write('---')
    if st.button("Cadastrar Processo 📁", use_container_width=True, type="primary", help='Clique para cadastrar o processo na base 📁'):

        # ✅ Valida os campos
        erros, campos_sanitizados = validar_processamento_campos(
            numero_processo,
            valor_input,
            data_recebimento,
            data_publicacao,
            ata,
            objetivo,
            observacao

        )
        if erros:
            for erro in erros:
                st.error(erro)
                st.write(f'{erro}')
            st.stop()

        objetivo_sanitizado = campos_sanitizados['objetivo']
        observacao_sanitizada = campos_sanitizados['observacao']

        if numero_processo in df["Nº do Processo"].values:
            st.error("⚠️ Esse processo já foi cadastrado! Veja abaixo:")
            mostrar_tabela(df[df["Nº do Processo"] == numero_processo],altura_max_linhas=99, 
                        nome_tabela="Processo já cadastrado!", mostrar_na_tela=True)
            st.stop()
        else:
            agora = datetime.now()
            novo = pd.DataFrame([{
                "Deliberação": deliberacao,
                "Nº do Processo": numero_processo,
                "Tipo de Despesa": tipo_despesa,
                "Órgão (UO)": orgao_uo,
                "Fonte de Recursos": fonte_recurso,
                "Grupo de Despesas": grupo_despesa,
                "Valor": valor_input,
                "Objetivo": objetivo_sanitizado,
                "Observação": observacao_sanitizada,
                "Data de Recebimento": data_recebimento,
                "Data de Publicação": data_publicacao,
                "Nº ATA": ata,
                "Cadastrado Por": st.session_state.username.title() + ' - ' + agora.strftime("%d/%m/%Y %H:%M:%S"),
            }])

            # TRATAR O VALOR (DE R$ 1.234,56 PARA 1234.56)
            novo["Valor"] = novo["Valor"].apply(
                lambda x: float(x.replace(".", "").replace(",", "."))
            )

            nome_base = str(nome_base)
            salvar_base(novo, nome_base)

def mostrar_cadastro_por_permissao(df, nome_base):
    if nome_base == "Base Crédito SOP/GEO":
        cadastrar_processos_credito_geo(df, nome_base)
    elif nome_base == "Base CPOF":
        cadastrar_processos_cpof(df, nome_base)
















