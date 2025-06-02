import streamlit as st
import io
import re

from utils.limite.limite_credito import calcular_limite_credito_atual
from utils.confeccoes.formatar import formatar_valor
from utils.confeccoes.formatar import por_extenso
from utils.confeccoes.gerar_baixar_confeccao import botao_gerar_e_baixar_arquivo
from utils.confeccoes.confeccao_ata import montar_ata
from utils.ui.display import titulos_pagina
from datetime import datetime, time

st.markdown(
'<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" integrity="sha512-9usAa10IRO0HhonpyAIVpjrylPvoDwiPUiKdWk5t3PyolY1cOd4DSE0Ga+ri4AuTroPR5aQvXU9xC6qOPnzFeg==" crossorigin="anonymous" referrerpolicy="no-referrer" />',
unsafe_allow_html=True
)

def resumo_cpof(df):
    with st.expander("📋 **Gerador Automático de Resumos** 📋", expanded=False):
        df['Valor'] = df['Valor'].apply(formatar_valor)
        titulos_pagina("Gerador de Resumos", font_size="1.9em", text_color="#3064AD", icon='<i class="fas fa-clipboard-list"></i>')
        
        def formatar_linha(numero):
            linha = df[df["Nº do Processo"] == numero].iloc[0]
            return f"{linha['Nº do Processo']} | {linha['Órgão (UO)']} | {linha['Valor']} | {linha['Tipo de Despesa']}"

        opcoes_processo = ["TODOS"] + df["Nº do Processo"].tolist()
        numero_processo = st.multiselect(
            "Selecione a linha do dataframe",
            options=opcoes_processo,
            format_func=lambda x: "TODOS" if x == "TODOS" else formatar_linha(x)
        )

        if "TODOS" in numero_processo:
            numero_processo = df["Nº do Processo"].tolist()

        if numero_processo:
            processo_selecionado = df[df["Nº do Processo"].isin(numero_processo)]

            processo_selecionado = processo_selecionado.copy()
            processo_selecionado['Valor_sem_formatacao'] = (
                processo_selecionado['Valor']
                .fillna('0')
                .replace({r'R\$ ': '', r'\.': '', ',': '.'}, regex=True)
                .astype(float, errors='ignore')
            )
        
            descricao_texto = f""

            for i, (_, row) in enumerate(processo_selecionado.iterrows(), start=1):
                descricao = f"{i}. {row['Nº do Processo']} - {row['Órgão (UO)']}\n"
                descricao += f"Objeto: {row['Objetivo']}\n"
                descricao += f"Fonte: {row['Fonte de Recursos']}\n"
                descricao += f"Valor: {row['Valor']}\n"
                descricao += f"Sugestão SEC.EXEC, SEPLAG e SEFAZ: \n"
                descricao += f"\n"
                
                descricao_texto += descricao

            st.text_area("📝 Resultados:", descricao_texto, height=400)
            
            output = io.BytesIO()
            output.write(descricao_texto.encode("utf-8"))
            output.seek(0)

            st.download_button(
                label="📥 Baixar Relatório 📥", 
                data=output, 
                file_name=f"relatorio_processo_{numero_processo}.txt", 
                mime="text/plain", 
                use_container_width=True, 
                type='primary'
            )
        else:
            st.info("⚠️ Selecione um número de processo para visualizar o resumo.")


def resumo_publicados_geo(df):
    with st.expander("📋 **Gerador Automático de Créditos Publicados** 📋", expanded=False):
        from datetime import datetime
        hoje = datetime.now().date()

        datas_disponiveis = df['Data de Publicação'].dropna().unique()

        datas_disponiveis = [data for data in datas_disponiveis if re.match(r"\d{4}-\d{2}-\d{2}", data)]
        datas_disponiveis = [datetime.strptime(data, "%Y-%m-%d").date() for data in datas_disponiveis]

        datas_disponiveis.append(hoje)
        datas_disponiveis.sort(reverse=True)
        hoje = st.selectbox(
            label="Datas disponíveis:",
            options=datas_disponiveis,
            format_func=lambda x: x.strftime("%d/%m/%Y"),  # Mostra em dd/mm/aaaa
        )

        st.session_state.data_atual = hoje.strftime("%Y-%m-%d")  # Pesquisa/filtra em yyyy-mm-dd

        titulos_pagina(f"Resumos de Créditos Publicados - ({st.session_state.data_atual})", font_size="1.9em", text_color="#3064AD", icon='<i class="fas fa-calendar"></i>')

        df_resumo_publicado = df[df['Data de Publicação'] == st.session_state.data_atual]

        if df_resumo_publicado.empty:
            st.info(f"⚠️ Não há processos publicados em ({st.session_state.data_atual}).")
            st.stop()

        if df_resumo_publicado is not df_resumo_publicado.empty:
            
            st.success(f"{(len(df_resumo_publicado))} ({por_extenso(len(df_resumo_publicado)).title()}) Processos Publicados em ({st.session_state.data_atual}).")

            colunas_escolhidas = ['Órgão (UO)','Nº do decreto', 'Fonte de Recursos', 'Valor']
            limite = calcular_limite_credito_atual()

            descricao_texto = f"_Relação dos *Publicados em {st.session_state.data_atual}*_\n\n"
            for index, row in df_resumo_publicado.iterrows():
                descricao = f""
                for coluna in colunas_escolhidas:
                    if coluna == 'Órgão (UO)':
                        descricao += f"*{row[coluna]}*"
                    if coluna == 'Nº do decreto':
                        numero = ''.join(filter(str.isdigit, str(row[coluna])))
                        valor_formatado = f"{numero[:3]}.{numero[3:-1]}"
                        descricao += f" - Decreto Nº *{valor_formatado}*"
                    if coluna == 'Fonte de Recursos':
                        descricao += f" - Fonte *{row[coluna]}*"
                    if coluna == 'Valor':
                        descricao += f" - *{(row[coluna])}*"
                descricao_texto += descricao + "\n"

            descricao_texto += "\n"
            
            descricao_texto += f"Total publicado no dia (somando os processos especiais e de poderes que não contam para o limite): *{(df_resumo_publicado['Valor'].sum())}*. Portanto, *atualizando o limite para {limite['percentual_executado_total']:.2f}%*, representando um *valor utilizado de {formatar_valor(limite['valor_utilizado'])}* do total autorizado ({formatar_valor(limite['valor_limite'])}) totalizando um saldo de *{formatar_valor(limite['valor_disponivel'])}*. \n\n"

            output = io.BytesIO()
            output.write(descricao_texto.encode("utf-8"))
            output.seek(0)

            st.text_area("📝 Resultados:", descricao_texto, height=230)

def resumo_geral_geo(df):
    with st.expander("📋 **Gerador Automático de Resumos** 📋", expanded=False):
        df['Valor'] = df['Valor'].apply(formatar_valor)
        titulos_pagina("Gerador de Resumos", font_size="1.9em", text_color="#3064AD", icon='<i class="fas fa-clipboard-list"></i>')
        # st.caption("Os resumos aparecem conforme os filtros aplicados na tabela.")

        def formatar_linha(numero):
            linha = df[df["Nº do Processo"] == numero].iloc[0]
            return f"{linha['Situação']} | {linha['Nº do Processo']} | {linha['Órgão (UO)']} | {linha['Valor']} | {linha['Origem de Recursos']}"
        

        opcoes_processo = ["TODOS"] + df["Nº do Processo"].tolist()
        numero_processo = st.multiselect(
            "Selecione a linha do dataframe",
            options=opcoes_processo,
            format_func=lambda x: "TODOS" if x == "TODOS" else formatar_linha(x)
        )
        if "TODOS" in numero_processo:
            numero_processo = df["Nº do Processo"].tolist()
        
        if numero_processo:
            processo_selecionado = df[df["Nº do Processo"].isin(numero_processo)]

            colunas_desejadas = ["Nº do Processo", "Órgão (UO)", "Objetivo", "Fonte de Recursos", "Valor", "Opnião SOP"]

             

            cada_tipo_origem = processo_selecionado['Origem de Recursos'].unique()  

            processo_selecionado = processo_selecionado.copy()
            processo_selecionado['Valor_sem_formatacao'] = (
                processo_selecionado['Valor']
                .fillna('0')
                .replace({r'R\$ ': '', r'\.': '', ',': '.'}, regex=True)
                .astype(float, errors='ignore')
            )
        
            descricao_texto = f"*Resumo das solicitações de créditos orçamentários - SOP*\n"
            descricao_texto += f"_Atualizado em_: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
            descricao_texto += f"*Quantidade de solicitações*: _{len(processo_selecionado)} ({por_extenso(len(processo_selecionado)).title()}) Processo{'s' if len(processo_selecionado) > 1 else ''}_\n"
            descricao_texto += f"*Valor total das solicitações*: {formatar_valor(processo_selecionado['Valor_sem_formatacao'].sum())}\n"

            for tipo_origem in cada_tipo_origem:
                processos_por_origem = processo_selecionado[processo_selecionado['Origem de Recursos'] == tipo_origem]
                descricao_texto += f"\n"
                descricao_texto += f"*{tipo_origem.title()}*: _{len(processos_por_origem)} ({por_extenso(len(processos_por_origem)).title()}) Processo{'s' if len(processos_por_origem) > 1 else ''}_\n"
                
                processos_por_origem.loc[:, 'Valor_sem_formatacao'] = (
                    processos_por_origem['Valor']
                    .fillna('0')
                    .replace({'R\$ ': '', '\.': '', ',': '.'}, regex=True)
                    .astype(float, errors='ignore')
                    )
                
                descricao_texto += f"*Valor total das solicitações {tipo_origem.lower()}*: {formatar_valor(processos_por_origem['Valor_sem_formatacao'].sum())}\n"

                for _, row in processos_por_origem.iterrows():
                    descricao = f"\n"
                    for coluna in colunas_desejadas:
                        # Só adiciona se não for vazia ou NaN
                        # import pandas as pd
                        # if coluna in row and pd.notna(row[coluna]) and str(row[coluna]).strip() != "":
                        #     descricao += f"*{coluna}*: {row[coluna]}\n"

                    # OPNIÃO SOP NÃO SALVANDO NA EDIÇÃO DE PROCESSOS
                        if coluna in row:
                            import pandas as pd
                            if coluna == "Opnião SOP" and pd.isna(row[coluna]):
                                pass
                            else:
                                descricao += f"*{coluna}*: {row[coluna]}\n"
                    descricao_texto += descricao

            st.text_area("📝 Resultados:", descricao_texto, height=400)
            output = io.BytesIO()
            output.write(descricao_texto.encode("utf-8"))
            output.seek(0)

            st.download_button(
            label="📥 Baixar Relatório 📥", 
            data=output, 
            file_name=f"relatorio_processo_{numero_processo}.txt", 
            mime="text/plain", 
            use_container_width=True, 
            type='primary'
        )
        else:
            st.info("⚠️ Selecione um número de processo para visualizar o resumo.")



def funcao_forms_ata(df):
    with st.container():
        membros_padrao = [
            {"nome": "FELIPE DE CARVALHO CORDEIRO", "matricula": "146-5", "cpf": "055.105.674-6", "indicacao": "GCG"},
            {"nome": "MADSON CORREIA MÁXIMO DE LIMA", "matricula": "105-8", "cpf": "051.745.964-77", "indicacao": "GCG"},
            {"nome": "MARCOS VINÍCIUS FERNANDES DE FREITAS", "matricula": "189-9", "cpf": "009.547.041-77", "indicacao": "SEFAZ"},
            {"nome": "MONIQUE SOUZA DE ASSIS", "matricula": "306-9", "cpf": "154.446.887-35", "indicacao": "SEFAZ"},
            {"nome": "PHELIPE GABRIEL CLEMENTINO VARGAS", "matricula": "3876-8", "cpf": "077.036.314-85", "indicacao": "SEPLAG"},
            {"nome": "ELESJANDELY CORREIA CALHEIROS MARQUES BASTOS", "matricula": "3868-7", "cpf": "058.772.074-31", "indicacao": "SEPLAG"},
            {"nome": "ADELY ROBERTA MEIRELES DE OLIVEIRA", "matricula": "16-7", "cpf": "060.014.464-07", "indicacao": "SEGOV"},
            {"nome": "VITOR HUGO PEREIRA DA SILVA", "matricula": "1-9", "cpf": "038.024.814-02", "indicacao": "SEGOV"}
        ]

        if "membros" not in st.session_state:
            st.session_state.membros = membros_padrao.copy()

        def adicionar_membro():
            st.session_state.membros.append({"nome": "", "matricula": "", "cpf": "", "indicacao": ""})

        def remover_membro():
            try:
                del st.session_state.membros[-1]
            except IndexError:
                st.info("⚠️ Não há membros para remover.")

        with st.expander("📋 **Gerador Automático de ATA** 📋", expanded=False):
            with st.form("formulario_ata"):
                titulos_pagina("Configuração da ATA", font_size="1.9em", text_color="#3064AD", icon='<i class="fas fa-cog"></i>')
                st.write("---")
                st.write("**Observação:** A ata é gerada com base nos membros padrão. Você pode adicionar ou remover membros, e a ata será atualizada automaticamente.")
                st.write("---")

                col1, col2, col3 = st.columns(3)
                col1.form_submit_button("➕ Adicionar membro", on_click=adicionar_membro, use_container_width=True, type="primary", help="Clique para adicionar um novo membro.")
                col2.form_submit_button("❌ Remover último membro", on_click=remover_membro, use_container_width=True, type="primary", help="Clique para remover o último membro adicionado.")
                col3.form_submit_button("🔄 Resetar membros padrão", on_click=lambda: st.session_state.update({"membros": membros_padrao.copy()}), use_container_width=True, type="primary", help="Clique para resetar aos membros originais.")

                st.write("---")
                col1, col2, col3, col4 = st.columns(4)
                data_reuniao = col1.date_input("📅 Data da reunião", value=datetime(2025, 5, 6))
                hora_reuniao = col2.time_input("⏰ Hora da reunião", value=time(13, 0))
                ano_exercicio = col3.number_input("📆 Ano do exercício financeiro", value=2025)
                numero_da_reuniao = col4.number_input("🔢 Número da reunião", value=31, min_value=1, max_value=999)

                local = st.text_area("📍 Local da reunião",
                                    "Sala de Reuniões da Secretaria de Estado do Planejamento, Gestão e Patrimônio, localizada na Rua Dr. Cincinato Pinto, nº 503, Centro, em Maceió, Estado de Alagoas")

                col1, col2, col3 = st.columns(3)
                presidente_nome = col1.text_input("👩‍💼 Nome do(a) presidente", "PAULA CINTRA DANTAS")
                presidente_matricula = col2.text_input("🔢 Matrícula do(a) presidente", "32-9")
                presidente_cpf = col3.text_input("🆔 CPF do(a) presidente", "082.478.484-73")

                col1, col2 = st.columns(2)
                for i, membro in enumerate(st.session_state.membros):
                    col = col1 if i % 2 == 0 else col2
                    with col.expander(f"Membro {i+1}", expanded=False):
                        membro["nome"] = st.text_input(f"Nome do membro {i+1}", membro["nome"], key=f"nome_{i}")
                        membro["matricula"] = st.text_input(f"Matrícula do membro {i+1}", membro["matricula"], key=f"matricula_{i}")
                        membro["cpf"] = st.text_input(f"CPF do membro {i+1}", membro["cpf"], key=f"cpf_{i}")
                        membro["indicacao"] = st.text_input(f"Indicado por (órgão) do membro {i+1}", membro["indicacao"], key=f"indicacao_{i}")

                data_formatada = f"{data_reuniao.day:02d}º dia do mês de {data_reuniao.strftime('%B')} do ano dois mil e {por_extenso(str(data_reuniao.year)[-2:])}"

                corpo_ata = f"\
Ao {data_formatada}, às {hora_reuniao.strftime('%H:%M')} horas, na {local}, \
foi realizada a Reunião do Comitê de Programação Orçamentária e Financeira (CPOF), \
instituído pela Portaria Conjunta SEPLAG/GCG/SEFAZ/SEGOV nº 32/2023. \
A reunião foi presidida pela Secretária de Estado do Planejamento, Gestão e Patrimônio, \
Sra. {presidente_nome}, matrícula {presidente_matricula}, \
inscrita no CPF sob o nº {presidente_cpf}. Estiveram presentes os seguintes membros do Comitê:"

                for membro in st.session_state.membros:
                    genero_participante = "inscrita" if membro["nome"].strip().split(" ")[0][-1].lower() == "a" else "inscrito"
                    corpo_ata += f" {membro['nome'].upper()}, matrícula nº {membro['matricula']}, {genero_participante} no CPF sob o nº {membro['cpf']}, indicado pela {membro['indicacao']};"

                corpo_ata += f" O Comitê deu início à sessão com a leitura da pauta, que tratou da execução orçamentária, financeira, patrimonial e contábil do Estado de Alagoas para o exercício financeiro de {ano_exercicio}."

                df_ata = df.copy()
                df_ata = df_ata[['Nº do Processo', 'Órgão (UO)', 'Objetivo', 'Valor', 'Deliberação']]
                df_ata['Deliberação'] = df_ata['Deliberação'].str.upper()
                df_ata.columns = df_ata.columns.str.upper()

                st.write('---')
                lista_interessados = df_ata['ÓRGÃO (UO)'].unique().tolist()

                if len(lista_interessados) > 1:
                    lista_formatada = ', '.join(lista_interessados[:-1]) + ' e ' + lista_interessados[-1]
                elif lista_interessados:
                    lista_formatada = lista_interessados[0]
                else:
                    lista_formatada = ''

                st.write(f"**Lista de Interessados:** {lista_formatada}.")
                df_ata = df_ata.sort_values(by='ÓRGÃO (UO)')
              
                botao_gerar_e_baixar_arquivo(
                            nome_botao="Confecção da ATA",
                            montar_conteudo_funcao=montar_ata,
                            parametros_funcao={"df": df_ata, "lista_interessados": lista_interessados, "corpo_ata": corpo_ata, "numero_reuniao": numero_da_reuniao},
                            nome_arquivo=f"ATA.pdf",
                            tipo_arquivo="pdf",
                            ata=True
                        )

def mostrar_resumos_por_permissao(df, nome_base):
    if nome_base == "Base Crédito SOP/GEO":
        resumo_geral_geo(df)
        resumo_publicados_geo(df)
    elif nome_base == "Base CPOF":
        resumo_cpof(df)
        funcao_forms_ata(df)