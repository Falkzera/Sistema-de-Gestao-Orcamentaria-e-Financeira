import streamlit as st
import pandas as pd
from datetime import datetime

from utils.opcoes_coluna.deliberacao import opcoes_deliberacao
from utils.opcoes_coluna.situacao import opcoes_situacao
from utils.opcoes_coluna.situacao_ted import opcoes_situacao_ted
from utils.opcoes_coluna.situacao_sop_geral import opcoes_situacao_geral_sop
from utils.opcoes_coluna.tipo_despesa import opcoes_tipo_despesa
from utils.opcoes_coluna.orgao_uo import opcoes_orgao_uo
from utils.opcoes_coluna.fonte_recurso import opcoes_fonte_recurso
from utils.opcoes_coluna.grupo_despesa import opcoes_grupo_despesa
from utils.opcoes_coluna.tipo_credito import opcoes_tipo_credito
from utils.opcoes_coluna.tipo_processo import opcoes_tipo_processo
from utils.opcoes_coluna.contabilizar_limite import opcoes_contabilizar_limite
from utils.opcoes_coluna.origem_recurso import opcoes_origem_recursos
from utils.ui.dataframe import mostrar_tabela
from utils.confeccoes.formatar import formatar_valor_br
from utils.opcoes_coluna.validadores.processo import validar_processamento_campos
from src.salvar_alteracoes import salvar_base
from utils.ui.display import titulos_pagina

def formatar_lista(lista):

    if isinstance(lista, list) and len(lista) == 1 and isinstance(lista[0], str) and " e " in lista[0]:
        partes = [parte.strip() for parte in lista[0].split(" e ")]
        if len(partes) > 1:
            lista = partes
    if isinstance(lista, list):
        if len(lista) == 0:
            return ""
        elif len(lista) == 1:
            return str(lista[0])
        elif len(lista) == 2:
            return f"{lista[0]} e {lista[1]}"
        else:
            return f"{', '.join(map(str, lista[:-1]))} e {lista[-1]}"
    return lista

ano_corrente = datetime.now().year

def cadastrar_processos_credito_geo(nome_base, df):
    with st.container(border=True):
        titulos_pagina("Cadastro de Processos Crédito SOP/GEO", font_size="1.9em", text_color="#3064AD", icon='<i class="fas fa-folder"></i>' )
            
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
        fonte_recurso = col2.multiselect("Fonte de Recursos **(Obrigatório)**",opcoes_fonte_recurso,help="Selecione a Unidade Orçamentária.", placeholder="Selecione a Fonte de Recursos")
        grupo_despesa = col3.multiselect("Grupo de Despesas **(Obrigatório)**",opcoes_grupo_despesa,help="Selecione o grupo de despesa.", placeholder="Selecione um Grupo de Despesas")
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

            data_recebimento = datetime.strptime(data_recebimento, "%d/%m/%Y").strftime("%Y-%m-%d")
            objetivo_sanitizado = campos_sanitizados['objetivo']
            observacao_sanitizada = campos_sanitizados['observacao']
            obs_sop_sanitizada = campos_sanitizados['obs_sop']

            if numero_processo in df["Nº do Processo"].values:
                st.error("⚠️ Esse processo já foi cadastrado! Veja abaixo:")
                mostrar_tabela(df[df["Nº do Processo"] == numero_processo],altura_max_linhas=99, 
                            nome_tabela="Processo já cadastrado!", mostrar_na_tela=True)
                st.stop()

            else:
                fonte_recurso = [item for sublist in fonte_recurso for item in (sublist.split(" e ") if isinstance(sublist, str) and " e " in sublist else [sublist])]
                grupo_despesa = [item for sublist in grupo_despesa for item in (sublist.split(" e ") if isinstance(sublist, str) and " e " in sublist else [sublist])]
                
                fonte_recurso_str = formatar_lista(fonte_recurso)
                grupo_despesa_str = formatar_lista(grupo_despesa)
                agora = datetime.now()
                novo = pd.DataFrame([{
                    "Situação": situacao,
                    "Origem de Recursos": origem_recursos,
                    "Órgão (UO)": orgao_uo,
                    "Nº do Processo": numero_processo,
                    "Tipo de Crédito": tipo_credito,
                    "Fonte de Recursos": fonte_recurso_str,
                    "Grupo de Despesas": grupo_despesa_str,
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

                novo["Valor"] = novo["Valor"].apply(
                    lambda x: float(x.replace(".", "").replace(",", "."))
                )
                
                nome_base = str(nome_base)
                salvar_base(novo, nome_base)

def cadastrar_processos_cpof(nome_base, df): 

    with st.container(border=True):

        titulos_pagina("Cadastro de Processos CPOF", font_size="1.9em", text_color="#3064AD", icon='<i class="fas fa-folder"></i>' )
        col1, col2, col3 = st.columns(3)
        numero_processo = col1.text_input("Nº do Processo **(Obrigatório)**",placeholder=f"E:00000.0000000000/{ano_corrente}",help=f"Digite o número do processo no formato: E:00000.0000000000/{ano_corrente}")
        numero_processo = str(numero_processo).strip() 
        deliberacao = col2.selectbox("Deliberação **(Obrigatório)**",opcoes_deliberacao,index=None,help="Selecione a deliberação do processo.", placeholder="Selecione a deliberação")
        orgao_uo = col3.selectbox("Órgão (UO) **(Obrigatório)**",opcoes_orgao_uo,index=None,help="Selecione o Órgão(UO).", placeholder="Selecione o Órgão(UO)")
        col1, col2, col3 = st.columns(3)
        tipo_despesa = col1.selectbox("Tipo de Despesa **(Obrigatório)**",opcoes_tipo_despesa,index=None,help="Selecione o Tipo de Despesa.", placeholder="Selecione o Tipo de Despesa")
        fonte_recurso = col2.multiselect("Fonte de Recursos **(Obrigatório)**",opcoes_fonte_recurso,help="Selecione a Fonte de Recursos.", placeholder="Selecione a Fonte de Recursos")
        grupo_despesa = col3.multiselect("Grupo de Despesas **(Obrigatório)**",opcoes_grupo_despesa,help="Selecione o grupo de despesa.", placeholder="Selecione um Grupo de Despesas")
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
                fonte_recurso = [item for sublist in fonte_recurso for item in (sublist.split(" e ") if isinstance(sublist, str) and " e " in sublist else [sublist])]
                grupo_despesa = [item for sublist in grupo_despesa for item in (sublist.split(" e ") if isinstance(sublist, str) and " e " in sublist else [sublist])]

                fonte_recurso_str = formatar_lista(fonte_recurso)
                grupo_despesa_str = formatar_lista(grupo_despesa)

                agora = datetime.now()
                novo = pd.DataFrame([{
                    "Deliberação": deliberacao,
                    "Nº do Processo": numero_processo,
                    "Tipo de Despesa": tipo_despesa,
                    "Órgão (UO)": orgao_uo,
                    "Fonte de Recursos": fonte_recurso_str,
                    "Grupo de Despesas": grupo_despesa_str,
                    "Valor": valor_input,
                    "Objetivo": objetivo_sanitizado,
                    "Observação": observacao_sanitizada,
                    "Data de Recebimento": data_recebimento,
                    "Data de Publicação": data_publicacao,
                    "Nº ATA": ata,
                    "Cadastrado Por": st.session_state.username.title() + ' - ' + agora.strftime("%d/%m/%Y %H:%M:%S"),
                }])

                novo["Valor"] = novo["Valor"].apply(
                    lambda x: float(x.replace(".", "").replace(",", "."))
                )

                nome_base = str(nome_base)
                salvar_base(novo, nome_base)

def cadastrar_processos_ted(nome_base, df): 
    
    with st.container(border=True):
        titulos_pagina("Cadastro de Processos TED", font_size="1.9em", text_color="#3064AD", icon='<i class="fas fa-folder"></i>' )
        col1, col2, col3 = st.columns(3)
        numero_processo = col1.text_input("Nº do Processo **(Obrigatório)**",placeholder=f"E:00000.0000000000/{ano_corrente}",help=f"Digite o número do processo no formato: E:00000.0000000000/{ano_corrente}")
        numero_processo = str(numero_processo).strip() 
        situacao_ted = col2.selectbox("Situação TED **(Obrigatório)**",opcoes_situacao_ted,index=None,help="Selecione a situação do TED.", placeholder="Selecione a situação do TED")
        uo_concedente = col3.selectbox("Órgão Concedente **(Obrigatório)**",opcoes_orgao_uo,index=None,help="Selecione o Órgão Concedente.", placeholder="Selecione o Órgão Concedente")

        col1, col2, col3 = st.columns(3)
        numero_ted = col1.text_input("Nº do TED", placeholder="Digite o número do TED", help="Digite o número do TED")
        termo_aditivo = col2.text_input("Termo Aditivo",  placeholder="Digite o Termo Aditivo", help="Digite o Termo Aditivo.")
        uo_executante = col3.selectbox("Órgão Executante **(Obrigatório)**",opcoes_orgao_uo,index=None,help="Selecione o Órgão Executante.", placeholder="Selecione o Órgão Executante")
        from streamlit_tags import st_tags

        col1, col2 = st.columns(2)
        with col1:
            programa_trabalho = st_tags(label="Programa de Trabalho **(Obrigatório)**", text="Pressione enter para adicionar vários programas.", value=[], suggestions=[], maxtags=10, key="programa_trabalho")
        with col2:
            natureza_despesa = st_tags(label="Natureza de Despesas **(Obrigatório)**", text="Pressione enter para adicionar várias naturezas.", value=[], suggestions=[], maxtags=10, key="natureza_despesa")

        col1, col2, col3 = st.columns(3)
        fonte_recurso = col1.multiselect("Fonte de Recursos **(Obrigatório)**", opcoes_fonte_recurso, help="Selecione a Fonte de Recursos.", placeholder="Selecione a Fonte de Recursos")
        valor_input = col2.text_input("Valor **(Obrigatório)**", placeholder="Ex: 1.234,56", help="Digite o valor do processo no formato: 1.234,56")
        valor_descentralizado = col3.text_input("Valor Descentralizado", placeholder="Ex: 1.234,56", help="Digite o valor descentralizado do processo no formato: 1.234,56")

        objetivo = st.text_input("Objetivo **(Obrigatório)**", placeholder="Ex: Objetivos do Pedido do Processo.", help="Objetivos do pedido do processo.")

        col1, col2, col3 = st.columns(3)
        data_recebimento = col1.text_input("Data de recebimento **(Obrigatório)**", placeholder="DD/MM/AAAA", help="Digite a data de recebimento do processo no formato: DD/MM/AAAA")
        data_publicacao = col2.text_input("Data de publicação", placeholder="DD/MM/AAAA", help="Digite a data de publicação do processo no formato: DD/MM/AAAA")
        data_encerramento = col3.text_input("Data de encerramento", placeholder="DD/MM/AAAA", help="Digite a data de encerramento do processo no formato: DD/MM/AAAA")

        if valor_input and valor_input.isnumeric():
            valor_input = formatar_valor_br(valor_input)

        nao_podem_estar_vazios = [
            situacao_ted,
            programa_trabalho,
            uo_concedente,
            uo_executante,
            numero_processo,
            fonte_recurso,
            natureza_despesa,
            data_recebimento, 
            valor_input,
            objetivo,
        ]

        if any(not campo for campo in nao_podem_estar_vazios):
            st.info("⚠️ Preencha todos os campos obrigatórios.")
            st.stop()

        st.write('---')
        if st.button("Cadastrar Processo 📁", use_container_width=True, type="primary", help='Clique para cadastrar o processo na base 📁'):

            erros, campos_sanitizados = validar_processamento_campos(
                numero_processo,
                valor_input,
                data_recebimento,
                data_publicacao,
                objetivo,
            )

            if erros:
                for erro in erros:
                    st.error(erro)
                    st.write(f'{erro}')
                st.stop()

            objetivo_sanitizado = campos_sanitizados.get('objetivo', objetivo)

            if numero_processo in df["Nº do Processo"].values:
                st.error("⚠️ Esse processo já foi cadastrado! Veja abaixo:")
                mostrar_tabela(df[df["Nº do Processo"] == numero_processo],altura_max_linhas=99, 
                            nome_tabela="Processo já cadastrado!", mostrar_na_tela=True)
                st.stop()
            else:
                fonte_recurso = [item for sublist in fonte_recurso for item in (sublist.split(" e ") if isinstance(sublist, str) and " e " in sublist else [sublist])]

                def formatar_lista_e(lista):
                    if isinstance(lista, list):
                        if len(lista) == 0:
                            return ""
                        elif len(lista) == 1:
                            return str(lista[0])
                        elif len(lista) == 2:
                            return f"{lista[0]} e {lista[1]}"
                        else:
                            return f"{', '.join(map(str, lista[:-1]))} e {lista[-1]}"
                    return lista

                programa_trabalho = formatar_lista_e(programa_trabalho)
                natureza_despesa = formatar_lista_e(natureza_despesa)
                fonte_recurso_str = formatar_lista(fonte_recurso)

                agora = datetime.now()
                novo = pd.DataFrame([{
                    "Situação TED": situacao_ted,
                    "Nº do Processo": numero_processo,
                    "UO Concedente": uo_concedente,
                    "UO Executante": uo_executante,
                    "Nº do TED": numero_ted,
                    "Termo Aditivo": termo_aditivo,
                    "Programa de Trabalho": programa_trabalho,
                    "Fonte de Recursos": fonte_recurso_str,
                    "Natureza de Despesa": natureza_despesa,
                    "Objetivo": objetivo_sanitizado,
                    "Valor": valor_input,
                    "Valor Descentralizado": valor_descentralizado,
                    "Saldo": '',
                    "Data de Publicação": data_publicacao,
                    "Data de Encerramento": data_encerramento,
                    "Data de Recebimento": data_recebimento,
                    "Cadastrado Por": st.session_state.username.title() + ' - ' + agora.strftime("%d/%m/%Y %H:%M:%S"),
                }])

                novo["Valor"] = novo["Valor"].apply(
                    lambda x: float(x.replace(".", "").replace(",", "."))
                )
                # se for none, vazio, ou '', nao executar
                try:
                    novo["Valor Descentralizado"] = novo["Valor Descentralizado"].apply(
                        lambda x: float(x.replace(".", "").replace(",", "."))
                    )
                    novo["Saldo"] = novo["Valor"] - novo["Valor Descentralizado"]
                except (ValueError, TypeError):
                    print("Valor Descentralizado provavelmente não foi preenchido ou está vazio, então essa linha não terá o calculo automatico do saldo.")
                    pass

                nome_base = str(nome_base)
                salvar_base(novo, nome_base)

def cadastrar_processos_sop_geral(nome_base, df):
    
    with st.container(border=True):
        titulos_pagina("Cadastro de Processos SOP/GERAL", font_size="1.9em", text_color="#3064AD", icon='<i class="fas fa-folder"></i>' )
        col1, col2, col3, col4 = st.columns(4)
        numero_processo = col1.text_input("Nº do Processo **(Obrigatório)**",placeholder=f"E:00000.0000000000/{ano_corrente}",help=f"Digite o número do processo no formato: E:00000.0000000000/{ano_corrente}")
        numero_processo = str(numero_processo).strip()
        orgao_uo = col2.selectbox("Órgão **(Obrigatório)**",opcoes_orgao_uo,index=None,help="Selecione o Órgão.", placeholder="Selecione o Órgão")
        tipo_processo = col3.selectbox("Tipo de Processo **(Obrigatório)**",opcoes_tipo_processo,index=None,help="Selecione o Tipo de Processo.", placeholder="Selecione o Tipo de Processo")
        situacao_sop = col4.selectbox("Situação SOP **(Obrigatório)**",opcoes_situacao_geral_sop,index=None,help="Selecione a situação do SOP.", placeholder="Selecione a situação do SOP")

        objetivo = st.text_input("Objetivo **(Obrigatório)**", placeholder="Ex: Objetivos do Pedido do Processo", help="Objetivos do pedido do processo.")
        data_recebimento = st.text_input("Data de recebimento **(Obrigatório)**", placeholder="DD/MM/AAAA", help="Digite a data de recebimento do processo no formato: DD/MM/AAAA")

        nao_podem_estar_vazios = [
            situacao_sop,
            orgao_uo,
            tipo_processo,
            numero_processo,
            data_recebimento, 
            objetivo,
        ]

        if any(not campo for campo in nao_podem_estar_vazios):
            st.info("⚠️ Preencha todos os campos obrigatórios.")
            st.stop()

        st.write('---')
        if st.button("Cadastrar Processo 📁", use_container_width=True, type="primary", help='Clique para cadastrar o processo na base 📁'):

            erros, campos_sanitizados = validar_processamento_campos(
                numero_processo,
                valor_input=None,
                data_recebimento=data_recebimento, 
                data_publicacao=None,
                numero_decreto=None,
                objetivo=objetivo,
                observacao=None, 
                obs_sop=None
        )

            if erros:
                for erro in erros:
                    st.error(erro)
                    st.write(f'{erro}')
                st.stop()

            objetivo_sanitizado = campos_sanitizados.get('objetivo', objetivo)

            if numero_processo in df["Nº do Processo"].values:
                st.error("⚠️ Esse processo já foi cadastrado! Veja abaixo:")
                mostrar_tabela(df[df["Nº do Processo"] == numero_processo],altura_max_linhas=99, 
                            nome_tabela="Processo já cadastrado!", mostrar_na_tela=True)
                st.stop()
            else:

                agora = datetime.now()
                novo = pd.DataFrame([{
                    "Situação SOP": situacao_sop,
                    "Nº do Processo": numero_processo,
                    "Órgão (UO)": orgao_uo,	
                    "Tipo de Processo": tipo_processo,
                    "Objetivo": objetivo_sanitizado,
                    "Data de Recebimento": data_recebimento,
                    "Cadastrado Por": st.session_state.username.title() + ' - ' + agora.strftime("%d/%m/%Y %H:%M:%S"),
                }])

                nome_base = str(nome_base)
                salvar_base(novo, nome_base)

def mostrar_cadastro_por_permissao(df, nome_base):
    if nome_base == "Base Crédito SOP/GEO":
        cadastrar_processos_credito_geo(df, nome_base)
    elif nome_base == "Base CPOF":
        cadastrar_processos_cpof(df, nome_base)
    elif nome_base == "Base TED":
        cadastrar_processos_ted(df, nome_base)
    elif nome_base == "Base SOP/GERAL":
        cadastrar_processos_sop_geral(df, nome_base)