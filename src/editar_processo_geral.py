import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from streamlit_tags import st_tags

import warnings

warnings.filterwarnings("ignore", category=pd.errors.SettingWithCopyWarning)

from utils.opcoes_coluna.tipo_despesa import opcoes_tipo_despesa
from utils.opcoes_coluna.orgao_uo import opcoes_orgao_uo
from utils.opcoes_coluna.fonte_recurso import opcoes_fonte_recurso
from utils.opcoes_coluna.grupo_despesa import opcoes_grupo_despesa
from utils.opcoes_coluna.tipo_credito import opcoes_tipo_credito
from utils.opcoes_coluna.contabilizar_limite import opcoes_contabilizar_limite
from utils.opcoes_coluna.origem_recurso import opcoes_origem_recursos
from utils.confeccoes.formatar import formatar_valor_sem_cifrao
from utils.opcoes_coluna.validadores.numero_decreto import validar_numero_decreto, formatar_numero_decreto
from utils.opcoes_coluna.validadores.data import validar_data_recebimento, validar_data_publicacao, validar_data_encerramento
from utils.opcoes_coluna.validadores.numero_processo import validar_numero_processo
from utils.opcoes_coluna.validadores.valor import validar_valor
from utils.opcoes_coluna.validadores.numero_ata import validar_numero_ata

from src.salvar_alteracoes import salvar_base
from src.salvar_historico import salvar_modificacao
from utils.opcoes_coluna.validadores.validar_campos_livres import validar_sanitizar_campos_livres

# Ao salvar, desempacotar lista para string "A", "A e B", "A, B e C"
def lista_para_string_tags(tags_list):
    tags_list = [str(x).strip() for x in tags_list if str(x).strip()]
    if not tags_list:
        return ""
    if len(tags_list) == 1:
        return tags_list[0]
    if len(tags_list) == 2:
        return f"{tags_list[0]} e {tags_list[1]}"
    return ", ".join(tags_list[:-1]) + f" e {tags_list[-1]}"

def string_para_lista_tags(valor):
    if not valor or (isinstance(valor, float) and pd.isna(valor)):
        return []
    if isinstance(valor, list):
        # Se já for lista, retorna limpa
        return [str(v).strip() for v in valor if str(v).strip()]
    if isinstance(valor, str):
        valor = valor.strip()
        # Remove colchetes e aspas se vier como string de lista
        if valor.startswith("[") and valor.endswith("]"):
            import ast
            try:
                lista_valores = ast.literal_eval(valor)
                return [str(v).strip() for v in lista_valores if str(v).strip()]
            except Exception:
                pass
        # Trata formato "A, B e C"
        if " e " in valor:
            partes = valor.rsplit(" e ", 1)
            primeiros = [v.strip() for v in partes[0].split(",") if v.strip()]
            ult = partes[1].strip()
            result = primeiros
            if ult:
                result.append(ult)
            return result
        # Trata apenas vírgulas
        elif "," in valor:
            return [v.strip() for v in valor.split(",") if v.strip()]
        elif valor:
            return [valor]
    return []

def desempacotar_multiselect(valor_atual, opcoes):
            """
            Converte string formatada tipo 'A, B e C' ou lista ['A, B e C'] para lista ['A', 'B', 'C']
            """
            import ast
            if pd.isna(valor_atual) or valor_atual == "":
                return []
            if isinstance(valor_atual, list):
                # Se for lista com um único elemento string já formatada, desempacota
                if len(valor_atual) == 1 and isinstance(valor_atual[0], str) and " e " in valor_atual[0]:
                    valor_atual = valor_atual[0]
                else:
                    return [str(v) for v in valor_atual if str(v) in opcoes]
            if isinstance(valor_atual, str):
                # Tenta converter string de lista para lista real
                if valor_atual.startswith("[") and valor_atual.endswith("]"):
                    try:
                        lista_valores = ast.literal_eval(valor_atual)
                        if isinstance(lista_valores, list):
                            return [str(v) for v in lista_valores if str(v) in opcoes]
                    except Exception:
                        pass
                # Desempacotar string tipo 'A, B e C'
                if " e " in valor_atual:
                    partes = valor_atual.rsplit(" e ", 1)
                    primeiros = [v.strip() for v in partes[0].split(",") if v.strip()]
                    ult = partes[1].strip()
                    result = [v for v in primeiros if v in opcoes]
                    if ult in opcoes:
                        result.append(ult)
                    return result
                elif "," in valor_atual:
                    return [v.strip() for v in valor_atual.split(",") if v.strip() in opcoes]
                elif valor_atual in opcoes:
                    return [valor_atual]
            return []

def is_empty_or_none(val):
    return val is None or (isinstance(val, float) and pd.isna(val)) or str(val).strip() == ""

def normalize_multiselect(val):
    """
    Converte qualquer representação (string formatada, lista, etc) em lista de strings, ignorando ordem.
    Corrige erro de ValueError para arrays numpy/pandas.
    """

    # Corrigir erro para arrays numpy/pandas
    if isinstance(val, (np.ndarray, pd.Series)):
        val = val.tolist()
    # Checagem segura para pd.isna
    try:
        if pd.isna(val):
            return []
    except Exception:
        pass
    if val == "" or val is None:
        return []
    if isinstance(val, list):
        # Se for lista com um único elemento string já formatada, desempacota
        if len(val) == 1 and isinstance(val[0], str) and " e " in val[0]:
            val = val[0]
        else:
            return sorted([str(v).strip() for v in val])
    if isinstance(val, str):
        import ast
        # Tenta converter string de lista para lista real
        if val.startswith("[") and val.endswith("]"):
            try:
                lista_valores = ast.literal_eval(val)
                if isinstance(lista_valores, list):
                    return sorted([str(v).strip() for v in lista_valores])
            except Exception:
                pass
        # Desempacotar string tipo 'A, B e C'
        if " e " in val:
            partes = val.rsplit(" e ", 1)
            primeiros = [v.strip() for v in partes[0].split(",") if v.strip()]
            ult = partes[1].strip()
            result = primeiros
            if ult:
                result.append(ult)
            return sorted([v for v in result if v])
        elif "," in val:
            return sorted([v.strip() for v in val.split(",") if v.strip()])
        elif val.strip():
            return [val.strip()]
    return []

def editar_unico_processo(selected_row, nome_base, df, nome_base_historica):

    if selected_row:
        numero_proc = selected_row["Nº do Processo"]

        with st.container(): # VISUALIZAÇÃO DOS DETALHES

            st.write(f"🔍 Você selecionou o processo: **{numero_proc}**")
            st.session_state["editar_processo_btn_clicked"] = True

            if "processo_edit" in st.session_state:
                if st.session_state["processo_edit"] != numero_proc:
                    del st.session_state["processo_edit"]
                    st.session_state["editar_processo_btn_clicked"] = False
                    st.rerun()
            else:
                st.session_state["processo_edit"] = numero_proc
                st.rerun()

            if "processo_edit" not in st.session_state and st.session_state.get("editar_processo_btn_clicked"):
                st.session_state["editar_processo_btn_clicked"] = False

            if "processo_edit" in st.session_state:
                formulario_edicao_processo(nome_base, df, nome_base_historica)

def normalize_tags(val):
    if not val or (isinstance(val, float) and pd.isna(val)):
        return []
    if isinstance(val, list):
        return sorted([str(v).strip() for v in val if str(v).strip()])
    if isinstance(val, str):
        if " e " in val:
            partes = val.rsplit(" e ", 1)
            primeiros = [v.strip() for v in partes[0].split(",") if v.strip()]
            ult = partes[1].strip()
            result = primeiros
            if ult:
                result.append(ult)
            return sorted([v for v in result if v])
        elif "," in val:
            return sorted([v.strip() for v in val.split(",") if v.strip()])
        elif val.strip():
            return [val.strip()]

def formulario_edicao_processo(nome_base, df, nome_base_historica):

    processo_edit = st.session_state["processo_edit"]
    try:
        row_index = df[df["Nº do Processo"] == processo_edit].index[0]
        processo = df.loc[row_index]
    except IndexError:
        del st.session_state["processo_edit"]
        st.stop()
        st.rerun()
        return
    
    salvar_btn = False

    try:
        if pd.notna(processo["Data de Recebimento"]):
            try:
                df.at[row_index, "Data de Recebimento"] = pd.to_datetime(processo["Data de Recebimento"]).strftime("%d/%m/%Y")
                processo["Data de Recebimento"] = df.at[row_index, "Data de Recebimento"]
            except Exception as e:
                st.error(f"Erro ao formatar a Data de Recebimento: {e}")
    except KeyError as e:
        print("Coluna Inexistente:", e)

    try:
        if pd.notna(processo["Data de Publicação"]):
            try:
                df.at[row_index, "Data de Publicação"] = pd.to_datetime(processo["Data de Publicação"]).strftime("%d/%m/%Y")
                processo["Data de Publicação"] = df.at[row_index, "Data de Publicação"]
            except Exception as e:
                st.error(f"Erro ao formatar a Data de Publicação: {e}")
    except KeyError as e:
        print("Coluna Inexistente:", e)
    
    try:
        if pd.notna(processo["Data de Encerramento"]):
            try:
                df.at[row_index, "Data de Encerramento"] = pd.to_datetime(processo["Data de Encerramento"]).strftime("%d/%m/%Y")
                processo["Data de Encerramento"] = df.at[row_index, "Data de Encerramento"]
            except Exception as e:
                st.error(f"Erro ao formatar a Data de Encerramento: {e}")
    except KeyError as e:
        print("Coluna Inexistente:", e)

    with st.form("form_edicao"): 

        def editar_select(label, opcoes, coluna): # Função para Construção dos Campos de selectbox.
            valor_atual = processo[coluna]
            return st.selectbox(f"{label} **(Editar)**", opcoes, index=opcoes.index(valor_atual))

        def editar_texto(label, coluna, tipo="input"): # Função para Construção dos Campos de texto.
            if tipo == "area":
                return st.text_area(f"{label} **(Editar)**", value=processo[coluna])
            return st.text_input(f"{label} **(Editar)**", value=processo[coluna])
        
        # TODOS OS CAMPOS E OPÇÕES POSSÍVEIS!

        campos_config = [
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
            "tipo": "multiselect",
            "opcoes": opcoes_fonte_recurso,
            "label": "Fonte de Recursos"
            },
            {
            "nome": "Grupo de Despesas",
            "tipo": "multiselect",
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
            {"nome": "Opnião SOP",
            "tipo": "area",
            "label": "Opinião SOP"
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
            "nome": "Data de Encerramento", # <<<<<<<<<<<<<<<<< PROCESSO DO TED <<<<<<<<<<<<<<<<<
            "tipo": "texto",
            "label": "Data de Encerramento"
            },
            {
            "nome": "Nº ATA",
            "tipo": "texto",
            "label": "Nº ATA"
            },
            {
            "nome": "Nº do decreto",
            "tipo": "decreto",
            "label": "Nº do decreto"
            },
            {
            "nome": "Nº do TED", #<<<<<<<<<< PROCESSO DO TED DAQUI PARA BAIXO<<<<<<<<<<<<<<<
            "tipo": "texto",
            "label": "Nº do TED"
            },
            {
            "nome": "Termo Aditivo",
            "tipo": "texto",
            "label": "Termo Aditivo"
            },
            {
            "nome": "UO Concedente",
            "tipo": "select",
            "opcoes": opcoes_orgao_uo,
            "label": "UO Concedente"
            },
            {
            "nome": "UO Executante",
            "tipo": "select",
            "opcoes": opcoes_orgao_uo,
            "label": "UO Executante"
            },
            {
            "nome": "Programa de Trabalho",
            "tipo": "tags",
            "label": "Programa de Trabalho"
            },
            {
            "nome": "Natureza de Despesa",
            "tipo": "tags",
            "label": "Natureza de Despesa"
            },
        ]

        # Dicionário para armazenar os valores editados
        valores_editados = {}
        with st.container(border=True):
            st.info("ℹ️ Se a opção de edição não aparecer, tente aumentar ou diminuir o zoom da página (CTRL + ou CTRL -) ℹ️")

        for campo in campos_config:
            nome = campo["nome"]
            if nome not in processo.index:
                continue

            if campo["tipo"] == "select":
                valores_editados[nome] = editar_select(campo["label"], campo["opcoes"], nome)

            elif campo["tipo"] == "multiselect":
                valor_atual = processo[nome]
                default = desempacotar_multiselect(valor_atual, campo["opcoes"])
                # st.write(f"**DEFAULT MULTISELECT:** {valor_atual}")  # Exibe o valor atual para referência
                valores_editados[nome] = st.multiselect(
                    f"{campo['label']} **(Editar)**",
                    options=campo["opcoes"],
                    default=default,
                    key=f"multiselect_{nome}"
                )
            elif campo["tipo"] == "tags":
                
                # Corrige: sempre converte string "A, B e C" para lista ["A", "B", "C"] para o st_tags
                valor_atual = processo[nome]
                # st.write(f"**VALOR ATUAL:** {valor_atual}")  # Exibe o valor atual para referência
                default = string_para_lista_tags(valor_atual)
                # default = valor_atual
                # st.write(f"**Valor DEFAULT:** {default}")  # Exibe o valor atual para referência
                # Garante que default seja sempre uma lista (mesmo se None ou vazio)
                if not default:
                    default = []

                # Garante que default seja uma lista de strings únicas e limpas
                # st.write(f"**Valor DEFAULT (após limpeza):** {default}")  # Exibe o valor atual para referência
                # Use a dynamic key that changes with the default value to force re-render

                # NOTA: ST_TAGS neste caso está com um bug, que provavelmente vem de dentro da biblioteca, algo relacionado com o estado de sessão do componente imagino. Pois em determinado momento ele não renderiza o proprio widget, ficnado um espaço em branco, e não exibe o valor atual, mesmo que esteja correto. A solução é clicar no botão de editar novamente, e ele renderiza corretamente.
                # e para resolver é necessario: adicionar uma chave única para o componente
                # adicionando a chave unica:
                # st.write(f"**Chave única:** {f'tags_{nome}_{default}'}")  # Exibe a chave única para referência

                # Adicionar KEY no parametro abaixo só atrapalhou!

                # Aqui claramente existe um bug do wigdet st_tags que deve ter algum conflito por estar inserido dentro de um form!
                # Ocorre que as vezes, quando se modifica a seleção em select_row de dataframe, ocasiona um "sumiço" do widget, porém a solução para o usuário de maniera rápida é modificar o zoom da página e o widget volta a aparecer kkkkkk.
                # então CTRL + ou CTRL - para aumentar ou diminuir o zoom da página, e o widget volta a aparecer. Ridículo, mas é o que temos no momento.


                tags = st_tags(
                    label=f"{campo['label']} **(Editar)**",
                    text='Pressione enter para adicionar',
                    value=default,
                )

                valores_editados[nome] = lista_para_string_tags(tags)
                # st.write(f"Valores editados: {valores_editados[nome]}")  # Exibe os valores editados para referência

            elif campo["tipo"] == "texto":
                valores_editados[nome] = st.text_input(f"{campo['label']} **(Editar)**", value="" if pd.isna(processo[nome]) else str(processo[nome]))
            elif campo["tipo"] == "area":
                valores_editados[nome] = editar_texto(campo["label"], nome, tipo="area")
            elif campo["tipo"] == "valor":
                valores_editados[nome] = st.text_input("Valor **(Editar)**", value=str(formatar_valor_sem_cifrao(processo[nome])))
            elif campo["tipo"] == "decreto":
                valor_atual = "" if pd.isna(processo[nome]) else str(processo[(nome)])
                valores_editados[nome] = st.text_input(f"{campo['label']} **(Editar)**", value=formatar_numero_decreto(valor_atual))
            elif campo["tipo"] == "Nº ATA":
                valor_atual = "" if pd.isna(processo[nome]) else str(processo[(nome)])
                valores_editados[nome] = st.text_input(f"{campo['label']} **(Editar)**", value=(valor_atual))
            else:
                valores_editados[nome] = st.text_input(f"{campo['label']} **(Editar)**", value="")

        erros = []

        # Sanitização e validação dos campos livres
        if "Observação" in valores_editados:
            valido, observacao_sanitizada = validar_sanitizar_campos_livres(valores_editados["Observação"])
            if not valido:
                erros.append("Observação inválida ou vazia.")
            else:
                valores_editados["Observação"] = observacao_sanitizada

        if "Objetivo" in valores_editados:
            valido, objetivo_sanitizada = validar_sanitizar_campos_livres(valores_editados["Objetivo"])
            if not valido:
                erros.append("Objetivo inválido ou vazia.")
            else:
                valores_editados["Objetivo"] = objetivo_sanitizada

        if "Opnião SOP" in valores_editados:
            valido, opniao_sop_sanitizada = validar_sanitizar_campos_livres(valores_editados["Opnião SOP"])
            if not valido:
                erros.append("Opnião SOP inválida ou vazia.")
            else:
                valores_editados["Opnião SOP"] = opniao_sop_sanitizada

        salvar_btn = st.form_submit_button("Salvar Edição ✅", use_container_width=True, type="primary", help='Clique para salvar a edição do processo na base 📁')
        cancelar_btn = st.form_submit_button("Cancelar Edição ❌", use_container_width=True, type="secondary", help='Clique para cancelar a edição ❌')
        if cancelar_btn:
            if "processo_edit" in st.session_state:
                del st.session_state["processo_edit"]
            st.rerun()
            return

        # Validações
        if salvar_btn:
            erros = []

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
            if "Data de Encerramento" in valores_editados:
                if not validar_data_encerramento(valores_editados["Data de Encerramento"]):
                    erros.append("Data de encerramento inválida.")
            if "Nº do decreto" in valores_editados:
                if not validar_numero_decreto(valores_editados["Nº do decreto"]):
                    erros.append("Número do decreto inválido, utilize o padrão: 123456")
            if "Nº ATA" in valores_editados:
                if not validar_numero_ata(valores_editados["Nº ATA"]):
                    erros.append("Preencha apenas com o número da ATA.")
            
            if erros:
                for erro in erros:
                    st.error(f"❌ {erro}")
                    if cancelar_btn:
                        del st.session_state["processo_edit"]
                        st.rerun()

            else:

                # coletar resposta de Data de Publicação, que virá da seguinte forma -> DIA/MES/ANO e converter para formato yyyy-mm-dd

                if "Data de Publicação" in valores_editados:
                    try:
                        if valores_editados["Data de Publicação"]:
                            valores_editados["Data de Publicação"] = pd.to_datetime(valores_editados["Data de Publicação"], format="%d/%m/%Y").strftime("%Y-%m-%d")
                    except Exception as e:
                        st.error(f"Erro ao converter Data de Publicação: {e}")
                        st.stop()

                if "Data de Recebimento" in valores_editados:
                    try:
                        if valores_editados["Data de Recebimento"]:
                            valores_editados["Data de Recebimento"] = pd.to_datetime(valores_editados["Data de Recebimento"], format="%d/%m/%Y").strftime("%Y-%m-%d")
                    except Exception as e:
                        st.error(f"Erro ao converter Data de Recebimento: {e}")
                        st.stop()
                if "Data de Encerramento" in valores_editados:
                    try:
                        if valores_editados["Data de Encerramento"]:
                            valores_editados["Data de Encerramento"] = pd.to_datetime(valores_editados["Data de Encerramento"], format="%d/%m/%Y").strftime("%Y-%m-%d")
                    except Exception as e:
                        st.error(f"Erro ao converter Data de Encerramento: {e}")
                        st.stop()

                agora = datetime.now()
                base = df
                modificacoes = []
            
                for nome, novo_valor in valores_editados.items():
                    valor_antigo = processo[nome]

                    if is_empty_or_none(valor_antigo) and is_empty_or_none(novo_valor):
                        continue  # Não considerar como modificação

                    if nome == "Valor":
                        novo_valor_float = float(novo_valor.replace(".", "").replace(",", "."))
                        if (is_empty_or_none(valor_antigo) and not is_empty_or_none(novo_valor_float)) or \
                           (not is_empty_or_none(valor_antigo) and novo_valor_float != valor_antigo):
                            modificacoes.append(f"{nome}: {valor_antigo} -> {novo_valor}")
                            base.loc[row_index, nome] = novo_valor_float

                    elif nome in ["Fonte de Recursos", "Grupo de Despesas"]:
                        # Normaliza ambos para lista de strings e compara ignorando ordem e formatação
                        antigo_list = normalize_multiselect(valor_antigo)
                        novo_list = normalize_multiselect(novo_valor)
                        if antigo_list != novo_list:
                            modificacoes.append(f"{nome}: {antigo_list} -> {novo_list}")
                            # Salva no formato string "A, B e C"
                            if len(novo_list) == 0:
                                valor_formatado = ""
                            elif len(novo_list) == 1:
                                valor_formatado = str(novo_list[0])
                            else:
                                valor_formatado = ", ".join(str(x) for x in novo_list[:-1])
                                valor_formatado += f" e {novo_list[-1]}"
                            base.at[row_index, nome] = valor_formatado

                    elif nome in ["Programa de Trabalho", "Natureza de Despesa"]:
                        # Normaliza ambos para lista de strings e compara ignorando ordem e formatação

                        antigo_list = normalize_tags(valor_antigo)
                        # st.write(f"Valor antigo: {antigo_list}")  # Exibe o valor antigo para referência
                        novo_list = normalize_tags(novo_valor)
                        # esse valor que deve estar em tags !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                        # st.write(f"Valor novo: {novo_list}")  # Exibe o valor novo para referência
                        if antigo_list != novo_list:
                            modificacoes.append(f"{nome}: {antigo_list} -> {novo_list}")
                            # Salva no formato string "A, B e C"
                            if len(novo_list) == 0:
                                valor_formatado = ""
                            elif len(novo_list) == 1:
                                valor_formatado = str(novo_list[0])
                            else:
                                valor_formatado = ", ".join(str(x) for x in novo_list[:-1])
                                valor_formatado += f" e {novo_list[-1]}"
                            base.at[row_index, nome] = valor_formatado
                    elif nome in ["Data de Recebimento", "Data de Publicação", "Data de Encerramento"]:
                        # Este bloco impede que a mudança do formato da data seja considerada uma modificação, pois o formato é apenas visual.
                        def normalizar_data(data):
                            if is_empty_or_none(data):
                                return None
                            try:
                                # Tenta converter para datetime, aceitando ambos formatos
                                return pd.to_datetime(str(data), dayfirst=True).date()
                            except Exception:
                                return None

                        data_antiga = normalizar_data(valor_antigo)
                        data_nova = normalizar_data(novo_valor)
                        if data_antiga != data_nova:
                            modificacoes.append(f"{nome}: {valor_antigo} -> {novo_valor}")
                            base.at[row_index, nome] = novo_valor

                    else:
                        if (is_empty_or_none(valor_antigo) and not is_empty_or_none(novo_valor)) or \
                            (not is_empty_or_none(valor_antigo) and str(novo_valor) != str(valor_antigo)):
                            modificacoes.append(f"{nome}: {valor_antigo} -> {novo_valor}")
                            base.at[row_index, nome] = novo_valor

                base.loc[row_index, "Última Edição"] = st.session_state.username.title() + ' - ' + agora.strftime("%d/%m/%Y %H:%M:%S")

                if modificacoes:
                    try:
                        salvar_base(base, nome_base)
                    except Exception as e:
                        st.error(f"Erro ao atualizar a planilha: {e}")
                        st.stop()

                    if modificacoes: # Mostrar a destrinchação do que foi modificado
                        st.write("### Modificações realizadas:")
                        for mod in modificacoes:
                            st.write(f"- {mod}")
                        
                        for mod in modificacoes:
                            salvar_modificacao(processo_edit, mod, st.session_state.username.title(), nome_base_historica)

                    del st.session_state["processo_edit"]
                    st.rerun()
                
                if not modificacoes:
                    st.info("ℹ️ Nenhuma modificação foi realizada pois o mesmo permanece inalterado. ℹ️")