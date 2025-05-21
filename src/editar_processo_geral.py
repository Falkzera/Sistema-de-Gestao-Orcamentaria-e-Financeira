import streamlit as st
import pandas as pd

def formulario_edicao_processo(nome_base, df):

    processo_edit = st.session_state["processo_edit"]
    row_index = df[df["Nº do Processo"] == processo_edit].index[0]
    processo = df.loc[row_index]
    
    salvar_btn = False

    # na coluna Data de Recebimento, pegar a data que estiver e colocar no formato dd/mm/aaaa
    if pd.notna(processo["Data de Recebimento"]):
        try:
            processo["Data de Recebimento"] = pd.to_datetime(processo["Data de Recebimento"]).strftime("%d/%m/%Y")
        except Exception as e:
            st.error(f"Erro ao formatar a Data de Recebimento: {e}")

    if pd.notna(processo["Data de Publicação"]):
        try:
            processo["Data de Publicação"] = pd.to_datetime(processo["Data de Publicação"]).strftime("%d/%m/%Y")
        except Exception as e:
            st.error(f"Erro ao formatar a Data de Publicação: {e}")

    with st.form("form_edicao"): # CONSTRUÇÃO DO FORMS PARA EDIÇÃO

        def editar_select(label, opcoes, coluna): # Função para Construção dos Campos de selectbox.
            valor_atual = processo[coluna]
            return st.selectbox(f"{label} (Editar)", opcoes, index=opcoes.index(valor_atual))

        def editar_texto(label, coluna, tipo="input"): # Função para Construção dos Campos de texto.
            if tipo == "area":
                return st.text_area(f"{label} (Editar)", value=processo[coluna])
            return st.text_input(f"{label} (Editar)", value=processo[coluna])
        
        # TODOS OS CAMPOS E OPÇÕES POSSÍVEIS!
        from utils.opcoes_coluna.deliberacao import opcoes_deliberacao
        from utils.opcoes_coluna.situacao import opcoes_situacao
        from utils.opcoes_coluna.tipo_despesa import opcoes_tipo_despesa
        from utils.opcoes_coluna.orgao_uo import opcoes_orgao_uo
        from utils.opcoes_coluna.fonte_recurso import opcoes_fonte_recurso
        from utils.opcoes_coluna.grupo_despesa import opcoes_grupo_despesa
        from utils.opcoes_coluna.tipo_credito import opcoes_tipo_credito
        from utils.opcoes_coluna.contabilizar_limite import opcoes_contabilizar_limite
        from utils.opcoes_coluna.origem_recurso import opcoes_origem_recursos


        from utils.confeccoes.formatar import formatar_valor_sem_cifrao

        # Lista de campos e suas configurações
        campos_config = [
            {
            "nome": "Deliberação",
            "tipo": "select",
            "opcoes": opcoes_deliberacao,
            "label": "Deliberação"
            },
            {
            "nome": "Situação",
            "tipo": "select",
            "opcoes": opcoes_situacao,
            "label": "Situação"
            },
            {
            "nome": "Tipo de Crédito",
            "tipo": "select",
            "opcoes": opcoes_tipo_credito,
            "label": "Tipo de Crédito"
            },
            {
            "nome": "Contabilizar no Limite?",
            "tipo": "select",
            "opcoes": opcoes_contabilizar_limite,
            "label": "Contabilizar no Limite?"
            },
            {
            "nome": "Origem de Recursos",
            "tipo": "select",
            "opcoes": opcoes_origem_recursos,
            "label": "Origem de Recursos"
            },
            {
            "nome": "Tipo de Despesa",
            "tipo": "select",
            "opcoes": opcoes_tipo_despesa,
            "label": "Tipo de Despesa"
            },
            {
            "nome": "Órgão (UO)",
            "tipo": "select",
            "opcoes": opcoes_orgao_uo,
            "label": "Órgão (UO)"
            },
            {
            "nome": "Nº do Processo",
            "tipo": "texto",
            "label": "Nº do Processo"
            },
            {
            "nome": "Fonte de Recursos",
            "tipo": "select",
            "opcoes": opcoes_fonte_recurso,
            "label": "Fonte de Recursos"
            },
            {
            "nome": "Grupo de Despesas",
            "tipo": "select",
            "opcoes": opcoes_grupo_despesa,
            "label": "Grupo de Despesas"
            },
            {
            "nome": "Valor",
            "tipo": "valor",
            "label": "Valor"
            },
            {
            "nome": "Objetivo",
            "tipo": "area",
            "label": "Objetivo"
            },
            {
            "nome": "Observação",
            "tipo": "texto",
            "label": "Observação"
            },
            {
            "nome": "Data de Recebimento",
            "tipo": "texto",
            "label": "Data de Recebimento"
            },
            {
            "nome": "Data de Publicação",
            "tipo": "texto",
            "label": "Data de Publicação"
            },
            {
            "nome": "Nº ATA",
            "tipo": "texto",
            "label": "Nº ATA"
            },
            {
            "nome": "Nº do decreto",
            "tipo": "decreto",
            "label": "Nº do Decreto"
            }
        ]

        # Dicionário para armazenar os valores editados
        valores_editados = {}

        # Importações específicas
        from utils.opcoes_coluna.validadores.numero_decreto import validar_numero_decreto, formatar_numero_decreto

        for campo in campos_config:
            nome = campo["nome"]
            if nome not in processo.index:
                continue

            if campo["tipo"] == "select":
                valores_editados[nome] = editar_select(campo["label"], campo["opcoes"], nome)
            elif campo["tipo"] == "texto":
                valores_editados[nome] = st.text_input(f"{campo['label']} (Editar)", value="" if pd.isna(processo[nome]) else str(processo[nome]))
            elif campo["tipo"] == "area":
                valores_editados[nome] = editar_texto(campo["label"], nome, tipo="area")
            elif campo["tipo"] == "valor":
                valores_editados[nome] = st.text_input("Valor (Editar)", value=str(formatar_valor_sem_cifrao(processo[nome])))
            elif campo["tipo"] == "decreto":
                if pd.notna(processo[nome]):
                    valores_editados[nome] = st.text_input(
                    f"{campo['label']} (Editar)",
                    value=str(formatar_numero_decreto(str(processo[nome])))
                    )
                else:
                    valores_editados[nome] = st.text_input(f"{campo['label']} (Editar)", value="")

        st.write('---')

        salvar_btn = st.form_submit_button("Salvar Edição", use_container_width=True, type="primary", help='Clique para salvar a edição do processo na base 📁')

        # Validações
        if salvar_btn:
            erros = []
            from utils.opcoes_coluna.validadores.data import validar_data_recebimento, validar_data_publicacao
            from utils.opcoes_coluna.validadores.numero_processo import validar_numero_processo
            from utils.opcoes_coluna.validadores.valor import validar_valor

            # Validações dinâmicas conforme os campos presentes
            if "Nº do Processo" in valores_editados:
                if not validar_numero_processo(valores_editados["Nº do Processo"]):
                    erros.append("Número do processo inválido.")
            if "Valor" in valores_editados:
                if not validar_valor(valores_editados["Valor"]):
                    erros.append("Valor inválido.")
            if "Data de Recebimento" in valores_editados:
                if not validar_data_recebimento(valores_editados["Data de Recebimento"]):
                    erros.append("Data de recebimento inválida.")
            if "Data de Publicação" in valores_editados:
                if not validar_data_publicacao(valores_editados["Data de Publicação"]):
                    erros.append("Data de publicação inválida.")
            if "Nº do decreto" in valores_editados:
                if not validar_numero_decreto(valores_editados["Nº do decreto"]):
                    erros.append("Número do decreto inválido.")

            if erros:
                for erro in erros:
                    st.error(f"❌ {erro}")

            if not erros:
            # Verifica se houve modificação
                houve_modificacao = False
            for nome, novo_valor in valores_editados.items():
                valor_antigo = processo[nome]
                if nome == "Valor":
                    try:
                        novo_valor_float = float(novo_valor.replace(".", "").replace(",", "."))
                        if novo_valor_float != valor_antigo:
                            houve_modificacao = True
                            break
                    except Exception:
                        houve_modificacao = True
                        break
                else:
                    if str(novo_valor) != str(valor_antigo):
                        houve_modificacao = True
                        break

            if not houve_modificacao:
                st.info("ℹ️ Nenhuma modificação foi realizada no processo, o processo permanece inalterado.")
            else:
                from datetime import datetime
                agora = datetime.now()
                base = df
                modificacoes = []

                def is_not_nan(value):
                    return not pd.isna(value)

                for nome, novo_valor in valores_editados.items():
                    valor_antigo = processo[nome]
                    if nome == "Valor":
                        novo_valor_float = float(novo_valor.replace(".", "").replace(",", "."))
                        if novo_valor_float != valor_antigo and is_not_nan(novo_valor) and is_not_nan(valor_antigo):
                            modificacoes.append(f"{nome}: {valor_antigo} -> {novo_valor}")
                            base.loc[row_index, nome] = novo_valor_float
                    else:
                        if str(novo_valor) != str(valor_antigo) and is_not_nan(novo_valor) and is_not_nan(valor_antigo):
                            modificacoes.append(f"{nome}: {valor_antigo} -> {novo_valor}")
                            base.loc[row_index, nome] = novo_valor

                base.loc[row_index, "Última Edição"] = st.session_state.username.title() + ' - ' + agora.strftime("%d/%m/%Y %H:%M:%S")

                try:
                    from src.salvar_alteracoes import salvar_base
                    salvar_base(base, nome_base)
                except Exception as e:
                    st.error(f"Erro ao atualizar a planilha: {e}")
                    st.stop()

                if modificacoes:
                    st.write("### Modificações realizadas:")
                for mod in modificacoes:
                    st.write(f"- {mod}")
                for mod in modificacoes:
                    from src.salvar_historico import salvar_modificacao
                    salvar_modificacao(processo_edit, mod, st.session_state.username.title())

                del st.session_state["processo_edit"]
                st.rerun()

                if modificacoes: # Mostrar a destrinchação do que foi modificado
                    st.write("### Modificações realizadas:")
                    for mod in modificacoes:
                        st.write(f"- {mod}")
                    
                    for mod in modificacoes:
                        from src.salvar_historico import salvar_modificacao
                        salvar_modificacao(processo_edit, mod, st.session_state.username.title())


                del st.session_state["processo_edit"]
                st.rerun()


def editar_unico_processo(selected_row, nome_base, df):

        if selected_row:
            numero_proc = selected_row["Nº do Processo"]

            with st.container(border=True): # VISUALIZAÇÃO DOS DETALHES
                expansor_editar = st.toggle("✏️ Edição de Processos Únicos", help="Clique para editar um único processo.")
                if expansor_editar:
                    st.write(f"🔍 Você selecionou o processo: **{numero_proc}**")

                    if "processo_edit" in st.session_state:
                        if st.session_state["processo_edit"] != numero_proc:
                            del st.session_state["processo_edit"]
                            st.rerun()
                    else:
                        st.session_state["processo_edit"] = numero_proc
                        st.rerun()

                if "processo_edit" in st.session_state:
                    formulario_edicao_processo(nome_base, df)

                    if expansor_editar is False:
                        del st.session_state["processo_edit"]
                        st.rerun()
                    if st.button("❌ Cancelar Edição", use_container_width=True):
                        del st.session_state["processo_edit"]
                        st.rerun()
