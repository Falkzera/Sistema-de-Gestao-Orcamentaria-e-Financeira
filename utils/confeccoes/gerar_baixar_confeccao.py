import streamlit as st
import inspect
import base64
import hashlib
import json
import pandas as pd
from typing import Any, Dict

def make_param_hash(parametros_funcao: Dict[str, Any]) -> str:
    """
    Cria um hash dos parâmetros, tratando tipos não serializáveis como DataFrames.

    Args:
        parametros_funcao: Dicionário de parâmetros para a função

    Returns:
        String com o hash MD5 dos parâmetros
    """
    # Cria uma cópia para não modificar o original
    params = {}

    for k, v in parametros_funcao.items():
        # Se for DataFrame, substitua por um resumo
        if isinstance(v, pd.DataFrame):
            params[k] = {
                "shape": v.shape,
                "columns": list(v.columns),
                # Opcional: adicionar um hash do conteúdo do DataFrame
                "content_hash": hashlib.md5(pd.util.hash_pandas_object(v, index=True).values.tobytes()).hexdigest()
            }
        # Se for outro objeto não serializável, trate aqui
        elif hasattr(v, "__dict__"):  # Objetos personalizados
            params[k] = str(v)
        else:
            try:
                # Tenta serializar para verificar se é serializável
                json.dumps(v)
                params[k] = v
            except (TypeError, OverflowError):
                # Se não for serializável, usa a representação em string
                params[k] = str(v)

    # Serializa e cria o hash
    param_str = json.dumps(params, sort_keys=True)
    return hashlib.md5(param_str.encode()).hexdigest()

def botao_gerar_e_baixar_arquivo(
    nome_botao: str,
    montar_conteudo_funcao,
    parametros_funcao: dict,
    nome_arquivo: str,
    tipo_arquivo: str = "pdf",
    ata=False,
):
    """
    Botão genérico para gerar e baixar arquivos (PDF ou DOCX), adaptável a diferentes funções de montagem.
    Usa cache baseado em parâmetros para evitar regeneração desnecessária.
    """
    # Inicializa o buffer de arquivos se não existir
    if "arquivo_buffer" not in st.session_state:
        st.session_state["arquivo_buffer"] = {}

    # Inicializa o dicionário de parâmetros usados se não existir
    if "parametros_usados" not in st.session_state:
        st.session_state["parametros_usados"] = {}

    # Gera um hash dos parâmetros para identificar mudanças
    param_hash = make_param_hash(parametros_funcao)
    cache_key = f"{nome_arquivo}_{param_hash}"

    with st.container():
        button_clicked = False

        # Determina o tipo de botão com base no parâmetro ata
        if not ata:
            button_clicked = st.button(f"📄 {nome_botao}", use_container_width=True, type="primary", key=f"botao_{nome_botao}")
        else:
            button_clicked = st.form_submit_button(f"📄 {nome_botao}", use_container_width=True, type="primary")

        if button_clicked:
            st.session_state["gerando_arquivo"] = True

            # Verifica se o arquivo já existe no buffer com os mesmos parâmetros
            if cache_key in st.session_state["arquivo_buffer"]:
                arquivo_bytes = st.session_state["arquivo_buffer"][cache_key]
                st.success("🔄 Download iniciado!")
            else:
                # Prepara para gerar novo conteúdo
                st.session_state["contador_quadro"] = 1
                st.session_state["contador_grafico"] = 1
                st.session_state["conteudo_pdf"] = []

                # Filtra os parâmetros necessários para a função
                assinatura = inspect.signature(montar_conteudo_funcao)
                parametros_necessarios = assinatura.parameters.keys()
                parametros_filtrados = {
                    nome: valor
                    for nome, valor in parametros_funcao.items()
                    if nome in parametros_necessarios
                }

                # Gera o conteúdo
                montar_conteudo_funcao(**parametros_filtrados)
                conteudo = st.session_state.get("conteudo_pdf", [])

                if not conteudo:
                    st.warning("⚠️ Nenhum conteúdo foi gerado.")
                    st.session_state["gerando_arquivo"] = False
                    return

                # Gera o arquivo PDF com base no tipo de documento (ata ou relatório padrão)
                if tipo_arquivo.lower() == "pdf":
                    if not ata:
                        from utils.confeccoes.relatorio.padronizacao_relatorio import gerar_pdf_weasy_padrao
                        arquivo_path = gerar_pdf_weasy_padrao(conteudo)
                    else:
                        from utils.confeccoes.confeccao_ata import gerar_pdf_weasy_ata_cpof
                        arquivo_path = gerar_pdf_weasy_ata_cpof(conteudo)
                else:
                    st.error(f"❌ Tipo de arquivo '{tipo_arquivo}' não suportado.")
                    st.session_state["gerando_arquivo"] = False
                    return

                # Lê o arquivo e armazena no buffer
                with open(arquivo_path, "rb") as f:
                    arquivo_bytes = f.read()

                # Armazena no buffer com o hash dos parâmetros
                st.session_state["arquivo_buffer"][cache_key] = arquivo_bytes
                # Não armazenamos os parâmetros originais, pois podem conter objetos não serializáveis
                st.session_state["parametros_usados"][cache_key] = param_hash
                st.success("✅ Download iniciado!")

            # Prepara o download
            b64 = base64.b64encode(arquivo_bytes).decode()

            # Define o tipo MIME com base no tipo de arquivo
            if tipo_arquivo.lower() == "pdf":
                mime = "application/pdf"
            else:
                mime = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

            # Script HTML para iniciar o download automaticamente
            download_script = f"""
            <html>
            <body>
            <a id="download_link" href="data:{mime};base64,{b64}" download="{nome_arquivo}" style="display:none"></a>
            <script>
                document.getElementById('download_link').click();
            </script>
            </body>
            </html>
            """
            st.components.v1.html(download_script, height=0)
            st.session_state["gerando_arquivo"] = False