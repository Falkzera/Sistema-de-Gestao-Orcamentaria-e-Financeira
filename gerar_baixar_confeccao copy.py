import streamlit as st
import inspect
import base64

def botao_gerar_e_baixar_arquivo(
    nome_botao: str,
    montar_conteudo_funcao,
    parametros_funcao: dict,
    nome_arquivo: str,
    tipo_arquivo: str = "pdf",
    ata=False,
    buffer_download=None,
):
    """
    Botão genérico para gerar e baixar arquivos (PDF ou DOCX), adaptável a diferentes funções de montagem.
    buffer_download: dict-like, usado para armazenar arquivos já gerados e evitar recarregamento.
    """

    with st.container():

        if ata is False:

            if st.button(f"📄 {nome_botao}", use_container_width=True, type="primary", key=f"botao_{nome_botao}"):
                st.session_state["gerando_arquivo"] = True
                # Só gera o arquivo se não estiver no buffer
                if buffer_download is not None and nome_arquivo in buffer_download:
                    arquivo_bytes = buffer_download[nome_arquivo]
                else:
                    st.session_state["contador_quadro"] = 1
                    st.session_state["contador_grafico"] = 1
                    st.session_state["conteudo_pdf"] = []

                    assinatura = inspect.signature(montar_conteudo_funcao)
                    parametros_necessarios = assinatura.parameters.keys()

                    parametros_filtrados = {
                        nome: valor
                        for nome, valor in parametros_funcao.items()
                        if nome in parametros_necessarios
                    }

                    montar_conteudo_funcao(**parametros_filtrados)

                    conteudo = st.session_state.get("conteudo_pdf", [])
                    if not conteudo:
                        st.warning("⚠️ Nenhum conteúdo foi gerado.")
                        st.session_state["gerando_arquivo"] = False
                        return

                    if tipo_arquivo.lower() == "pdf":
                        if ata is False:
                            from utils.confeccoes.relatorio.padronizacao_relatorio import gerar_pdf_weasy_padrao
                            arquivo_path = gerar_pdf_weasy_padrao(conteudo)
                        if ata is True:
                            from utils.confeccoes.confeccao_ata import gerar_pdf_weasy_ata_cpof
                            arquivo_path = gerar_pdf_weasy_ata_cpof(conteudo)
                    else:
                        st.error(f"❌ Tipo de arquivo '{tipo_arquivo}' não suportado.")
                        st.session_state["gerando_arquivo"] = False
                        return

                    with open(arquivo_path, "rb") as f:
                        arquivo_bytes = f.read()
                    if buffer_download is not None:
                        buffer_download[nome_arquivo] = arquivo_bytes

                b64 = base64.b64encode(arquivo_bytes).decode()
                if tipo_arquivo.lower() == "pdf":
                    mime = "application/pdf"
                else:
                    mime = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

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
        
        if ata is True:

            if st.form_submit_button(f"📄 {nome_botao}", use_container_width=True, type="primary"):
                st.session_state["gerando_arquivo"] = True
                # Só gera o arquivo se não estiver no buffer
                if buffer_download is not None and nome_arquivo in buffer_download:
                    arquivo_bytes = buffer_download[nome_arquivo]
                else:
                    st.session_state["contador_quadro"] = 1
                    st.session_state["contador_grafico"] = 1
                    st.session_state["conteudo_pdf"] = []

                    assinatura = inspect.signature(montar_conteudo_funcao)
                    parametros_necessarios = assinatura.parameters.keys()

                    parametros_filtrados = {
                        nome: valor
                        for nome, valor in parametros_funcao.items()
                        if nome in parametros_necessarios
                    }

                    montar_conteudo_funcao(**parametros_filtrados)

                    conteudo = st.session_state.get("conteudo_pdf", [])
                    if not conteudo:
                        st.warning("⚠️ Nenhum conteúdo foi gerado.")
                        st.session_state["gerando_arquivo"] = False
                        return

                    if tipo_arquivo.lower() == "pdf":
                        if ata is False:
                            from utils.confeccoes.relatorio.padronizacao_relatorio import gerar_pdf_weasy_padrao
                            arquivo_path = gerar_pdf_weasy_padrao(conteudo)
                        if ata is True:
                            from utils.confeccoes.confeccao_ata import gerar_pdf_weasy_ata_cpof
                            arquivo_path = gerar_pdf_weasy_ata_cpof(conteudo)
                    else:
                        st.error(f"❌ Tipo de arquivo '{tipo_arquivo}' não suportado.")
                        st.session_state["gerando_arquivo"] = False
                        return

                    with open(arquivo_path, "rb") as f:
                        arquivo_bytes = f.read()
                    if buffer_download is not None:
                        buffer_download[nome_arquivo] = arquivo_bytes

                b64 = base64.b64encode(arquivo_bytes).decode()
                if tipo_arquivo.lower() == "pdf":
                    mime = "application/pdf"
                else:
                    mime = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

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
