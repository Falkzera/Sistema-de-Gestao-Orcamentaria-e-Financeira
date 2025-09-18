import streamlit as st
import pandas as pd
from utils.ui.display import padrao_importacao_pagina, titulos_pagina, rodape_desenvolvedor
from utils.auth.auth import verificar_permissao, func_load_cadastro_usuarios
from streamlit_gsheets import GSheetsConnection

# Configuração da página
st.set_page_config(
    page_title="Manutenção - SIGOF",
    page_icon="🔧",
    layout="wide"
)

# Verificar permissões
verificar_permissao()

# Aplicar padrões visuais
padrao_importacao_pagina()
titulos_pagina("🔧 Manutenção do Sistema", "Gerenciamento de usuários, cargos e permissões")

def verificar_acesso_manutencao():
    """
    Verifica se o usuário tem permissão para acessar a página de manutenção
    Verifica se o usuário tem permissão para a página 'manutencao'
    """
    user_cpf = st.session_state.get("user_cpf", "")
    user_paginas = st.session_state.get("user_paginas", [])
    
    if not user_cpf:
        st.error("🚫 Usuário não autenticado!")
        st.stop()
    
    # Verificar se o usuário tem permissão para acessar a página de manutenção
    if "manutencao" not in user_paginas:
        st.error("🚫 Acesso negado! Você não tem permissão para acessar esta página.")
        st.info(f"Suas páginas permitidas: {', '.join(user_paginas) if user_paginas else 'Nenhuma'}")
        st.stop()
    
    return True

def carregar_dados_usuarios():
    """Carrega dados dos usuários cadastrados"""
    try:
        df_usuarios = func_load_cadastro_usuarios()
        if df_usuarios.empty:
            st.error("❌ Não foi possível carregar os dados dos usuários.")
            return pd.DataFrame()
        
        # Limpar aspas duplas dos dados se existirem
        for col in df_usuarios.columns:
            if df_usuarios[col].dtype == 'object':
                df_usuarios[col] = df_usuarios[col].astype(str).str.strip('"')
        
        return df_usuarios
    except Exception as e:
        st.error(f"❌ Erro ao carregar dados dos usuários: {str(e)}")
        return pd.DataFrame()



def salvar_alteracoes_usuario(df_usuarios, linha_editada, indice):
    """Salva as alterações feitas em um usuário específico"""
    try:
        # Conectar ao Google Sheets
        conn = st.connection("gsheets", type=GSheetsConnection)
        
        # Atualizar o DataFrame com os dados editados
        for col in df_usuarios.columns:
            if col in linha_editada:
                df_usuarios.loc[indice, col] = linha_editada[col]
        
        # Salvar no Google Sheets
        conn.update(worksheet="CADASTRO", data=df_usuarios)
        
        # Limpar cache para forçar recarregamento
        if "cadastro_usuarios" in st.session_state:
            del st.session_state["cadastro_usuarios"]
        
        st.success("✅ Alterações salvas com sucesso!")
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Erro ao salvar alterações: {str(e)}")

def interface_visualizacao_usuarios():
    """Interface para visualização e edição de usuários"""
    st.subheader("👥 Usuários Cadastrados")
    
    df_usuarios = carregar_dados_usuarios()
    if df_usuarios.empty:
        return
    
    # Filtros
    col1, col2 = st.columns(2)
    
    with col1:
        filtro_unidade = st.selectbox(
            "Filtrar por Unidade:",
            options=["Todas"] + sorted(df_usuarios['UNIDADE'].unique().tolist()),
            key="filtro_unidade_usuarios"
        )
    
    with col2:
        busca_nome = st.text_input("Buscar por Nome:", key="busca_nome_usuario")
    
    # Aplicar filtros
    df_filtrado = df_usuarios.copy()
    
    if filtro_unidade != "Todas":
        df_filtrado = df_filtrado[df_filtrado['UNIDADE'] == filtro_unidade]
    
    if busca_nome:
        df_filtrado = df_filtrado[df_filtrado['NOME'].str.contains(busca_nome, case=False, na=False)]
    
    # Exibir estatísticas
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total de Usuários", len(df_usuarios))
    with col2:
        st.metric("Usuários Filtrados", len(df_filtrado))
    with col3:
        st.metric("Unidades Únicas", df_usuarios['UNIDADE'].nunique())
    
    # Tabela de usuários
    if not df_filtrado.empty:
        st.markdown("### 📋 Lista de Usuários")
        
        # Configurar editor de dados
        df_editado = st.data_editor(
            df_filtrado,
            use_container_width=True,
            num_rows="dynamic",
            column_config={
                "CPF": st.column_config.TextColumn("CPF", disabled=True),
                "NOME": st.column_config.TextColumn("Nome"),
                "UNIDADE": st.column_config.TextColumn("Unidade"),
                "PERMISSAO_PAGE": st.column_config.TextColumn("Páginas Permitidas"),
                "PERMISSAO_BASE": st.column_config.TextColumn("Bases Permitidas")
            },
            key="editor_usuarios"
        )
        
        # Verificar se houve alterações
        if not df_editado.equals(df_filtrado):
            st.warning("⚠️ Você fez alterações nos dados. Clique em 'Salvar Alterações' para confirmar.")
            
            if st.button("💾 Salvar Alterações", type="primary"):
                try:
                    # Conectar ao Google Sheets
                    conn = st.connection("gsheets", type=GSheetsConnection)
                    
                    # Atualizar apenas as linhas que foram modificadas
                    for idx in df_editado.index:
                        if not df_editado.loc[idx].equals(df_filtrado.loc[idx]):
                            # Encontrar a linha correspondente no DataFrame original
                            cpf_editado = df_editado.loc[idx, 'CPF']
                            linha_original = df_usuarios[df_usuarios['CPF'] == cpf_editado].index[0]
                            
                            # Atualizar o DataFrame original
                            for col in df_usuarios.columns:
                                df_usuarios.loc[linha_original, col] = df_editado.loc[idx, col]
                    
                    # Salvar no Google Sheets
                    conn.update(worksheet="CADASTRO", data=df_usuarios)
                    
                    # Limpar cache
                    if "cadastro_usuarios" in st.session_state:
                        del st.session_state["cadastro_usuarios"]
                    
                    st.success("✅ Alterações salvas com sucesso!")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Erro ao salvar alterações: {str(e)}")
    else:
        st.info("ℹ️ Nenhum usuário encontrado com os filtros aplicados.")



def obter_bases_disponiveis():
    """Obtém as bases disponíveis do Google Sheets da aba BASES"""
    try:
        # Tentar carregar da aba BASES do Google Sheets
        conn = st.connection("gsheets", type=GSheetsConnection)
        df_bases = conn.read(worksheet="BASES", ttl=300)
        
        if not df_bases.empty and 'BASE' in df_bases.columns:
            # Criar dicionário com as bases do Google Sheets
            bases_sistema = {}
            
            for _, row in df_bases.iterrows():
                base_key = str(row['BASE']).strip().lower()
                
                # Verificar se existe coluna de nome/descrição
                if 'NOME' in df_bases.columns:
                    base_nome = str(row['NOME']).strip()
                elif 'BASE' in df_bases.columns:
                    base_nome = str(row['BASE']).strip()
                else:
                    # Usar o próprio nome da base formatado
                    base_nome = base_key.replace('_', ' ').title()
                
                # Adicionar apenas se não for vazio
                if base_key and base_key != 'nan':
                    bases_sistema[base_key] = base_nome.upper()
            
            if bases_sistema:
                print(f"✅ Bases carregadas do Google Sheets: {len(bases_sistema)} bases")
                return bases_sistema
        
        print("⚠️ Aba BASES vazia ou sem coluna BASE, usando bases padrão")
        
    except Exception as e:
        print(f"❌ Erro ao carregar bases do Google Sheets: {str(e)}")
        print("⚠️ Usando bases padrão do sistema")
    
    # Fallback para bases padrão caso não consiga carregar do Google Sheets
    bases_sistema = {
        "cpof": "CPOF",
        "credito_sop_geo": "CRÉDITO SOP/GEO",
        "receita": "RECEITA",
        "despesa": "DESPESA",
        "dotacao": "DOTAÇÃO",
        "rgf": "RGF"
    }
    return bases_sistema

def obter_paginas_disponiveis():
    """Obtém as páginas disponíveis do Google Sheets da aba PAGINA"""
    try:
        # Tentar carregar da aba PAGINA do Google Sheets
        conn = st.connection("gsheets", type=GSheetsConnection)
        df_paginas = conn.read(worksheet="PAGINA", ttl=300)
        
        if not df_paginas.empty and 'PAGINA' in df_paginas.columns:
            # Criar dicionário com as páginas do Google Sheets
            paginas_sistema = {}
            
            for _, row in df_paginas.iterrows():
                pagina_key = str(row['PAGINA']).strip().lower()
                
                # Verificar se existe coluna de nome/descrição
                if 'NOME' in df_paginas.columns:
                    pagina_nome = str(row['NOME']).strip()
                elif 'PAGINA' in df_paginas.columns:
                    pagina_nome = str(row['PAGINA']).strip()
                else:
                    # Usar o próprio nome da página formatado
                    pagina_nome = pagina_key.replace('_', ' ').title()
                
                # Adicionar apenas se não for vazio
                if pagina_key and pagina_key != 'nan':
                    paginas_sistema[pagina_key] = pagina_nome.upper()
            
            if paginas_sistema:
                print(f"✅ Páginas carregadas do Google Sheets: {len(paginas_sistema)} páginas")
                return paginas_sistema
        
        print("⚠️ Aba PAGINA vazia ou sem coluna PAGINA, usando páginas padrão")
        
    except Exception as e:
        print(f"❌ Erro ao carregar páginas do Google Sheets: {str(e)}")
        print("⚠️ Usando páginas padrão do sistema")
    
    # Fallback para páginas padrão caso não consiga carregar do Google Sheets
    paginas_sistema = {
        "repositorio": "REPOSITÓRIO DE DADOS",
        "canal_resposta_cpof": "MANIFESTAÇÃO TÉCNICA", 
        "dashboards": "DASHBOARDS",
        "relatorio": "RELATÓRIO",
        "historico": "HISTÓRICO",
        "visualizar": "VISUALIZAR PROCESSOS",
        "cadastro": "CADASTRAR PROCESSO",
        "manutencao": "MANUTENÇÃO",
        "home": "HOME"
    }
    return paginas_sistema

def interface_adicionar_usuario():
    """Interface para adicionar novos usuários"""
    st.subheader("➕ Adicionar Novo Usuário")
    
    # Obter dados para os selectboxes
    paginas_disponiveis = obter_paginas_disponiveis()
    bases_disponiveis = obter_bases_disponiveis()
    
    with st.form("form_adicionar_usuario"):
        col1, col2 = st.columns(2)
        
        with col1:
            novo_cpf = st.text_input("CPF", placeholder="Digite o CPF")
            novo_nome = st.text_input("Nome", placeholder="Digite o nome")
            novo_sobrenome = st.text_input("Sobrenome", placeholder="Digite o sobrenome")
        
        with col2:
            nova_unidade = st.text_input("Unidade", placeholder="SEPLAG")
            
        # Multiselect para páginas permitidas
        st.markdown("### 📄 Páginas Permitidas")
        paginas_selecionadas = st.multiselect(
            "Selecione as páginas que o usuário terá acesso:",
            options=list(paginas_disponiveis.keys()),
            format_func=lambda x: paginas_disponiveis[x],
            help="Selecione uma ou mais páginas que o usuário poderá acessar"
        )
        
        # Multiselect para bases permitidas
        st.markdown("### 🗂️ Bases Permitidas")
        bases_selecionadas = st.multiselect(
            "Selecione as bases que o usuário terá acesso:",
            options=list(bases_disponiveis.keys()),
            format_func=lambda x: bases_disponiveis[x],
            help="Selecione uma ou mais bases que o usuário poderá acessar (cada base será associada ao seu par de histórico)"
        )
        
        submitted = st.form_submit_button("➕ Adicionar Usuário", type="primary")
        
        if submitted:
            if novo_cpf and novo_nome and novo_sobrenome and nova_unidade:
                try:
                    # Carregar dados atuais
                    df_usuarios = carregar_dados_usuarios()
                    
                    # Verificar se CPF já existe
                    if novo_cpf in df_usuarios['CPF'].values:
                        st.error("❌ CPF já cadastrado no sistema!")
                        return
                    
                    # Combinar nome e sobrenome
                    nome_completo = f"{novo_nome} {novo_sobrenome}"
                    
                    # Converter listas de permissões para strings separadas por vírgula
                    permissao_page = ','.join(paginas_selecionadas) if paginas_selecionadas else ''
                    permissao_base = ','.join(bases_selecionadas) if bases_selecionadas else ''
                    
                    # Criar novo registro com as novas colunas
                    novo_usuario = pd.DataFrame({
                        'NOME': [nome_completo],
                        'CPF': [novo_cpf],
                        'UNIDADE': [nova_unidade],
                        'PERMISSAO_PAGE': [permissao_page],
                        'PERMISSAO_BASE': [permissao_base]
                    })
                    
                    # Adicionar ao DataFrame existente
                    df_atualizado = pd.concat([df_usuarios, novo_usuario], ignore_index=True)
                    
                    # Conectar ao Google Sheets
                    conn = st.connection("gsheets", type=GSheetsConnection)
                    
                    # Salvar usuário no Google Sheets
                    conn.update(worksheet="CADASTRO", data=df_atualizado)
                    
                    # Limpar cache
                    for key in list(st.session_state.keys()):
                        if key.startswith("cadastro_usuarios") or key.startswith("usuarios_cache"):
                            del st.session_state[key]
                    
                    st.success("✅ Usuário adicionado com sucesso!")
                    if paginas_selecionadas:
                        st.info(f"📄 Páginas configuradas: {', '.join([paginas_disponiveis[p] for p in paginas_selecionadas])}")
                    if bases_selecionadas:
                        st.info(f"🗂️ Bases configuradas: {', '.join([bases_disponiveis[b] for b in bases_selecionadas])}")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Erro ao adicionar usuário: {str(e)}")
            else:
                st.error("❌ Preencha todos os campos obrigatórios!")

def interface_descricao():
    """Interface para exibir descrições das páginas e bases"""
    st.subheader("📋 Descrição de Páginas e Bases")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📄 Páginas do Sistema")
        try:
            # Carregar dados da aba PAGINA
            conn = st.connection("gsheets", type=GSheetsConnection)
            df_paginas = conn.read(worksheet="PAGINA", ttl=300)
            
            if not df_paginas.empty and 'PAGINA' in df_paginas.columns:
                # Verificar se existe coluna DESCRIÇÃO
                if 'DESCRIÇÃO' in df_paginas.columns or 'DESCRICAO' in df_paginas.columns:
                    desc_col = 'DESCRIÇÃO' if 'DESCRIÇÃO' in df_paginas.columns else 'DESCRICAO'
                    
                    # Filtrar apenas linhas com dados válidos
                    df_display = df_paginas[['PAGINA', desc_col]].dropna()
                    df_display = df_display[df_display['PAGINA'].str.strip() != '']
                    
                    # Renomear colunas para exibição
                    df_display.columns = ['PÁGINA', 'DESCRIÇÃO']
                    
                    # Converter para maiúsculas para consistência visual
                    df_display['PÁGINA'] = df_display['PÁGINA'].str.upper()
                    
                    if not df_display.empty:
                        st.dataframe(
                            df_display,
                            use_container_width=True,
                            hide_index=True
                        )
                    else:
                        st.info("📄 Nenhuma página com descrição encontrada")
                else:
                    st.warning("⚠️ Coluna DESCRIÇÃO não encontrada na aba PAGINA")
            else:
                st.error("❌ Erro ao carregar dados da aba PAGINA")
                
        except Exception as e:
            st.error(f"❌ Erro ao carregar páginas: {str(e)}")
    
    with col2:
        st.markdown("### 🗂️ Bases do Sistema")
        try:
            # Carregar dados da aba BASES
            conn = st.connection("gsheets", type=GSheetsConnection)
            df_bases = conn.read(worksheet="BASES", ttl=300)
            
            if not df_bases.empty and 'BASE' in df_bases.columns:
                # Verificar se existe coluna DESCRIÇÃO
                if 'DESCRIÇÃO' in df_bases.columns or 'DESCRICAO' in df_bases.columns:
                    desc_col = 'DESCRIÇÃO' if 'DESCRIÇÃO' in df_bases.columns else 'DESCRICAO'
                    
                    # Filtrar apenas linhas com dados válidos
                    df_display = df_bases[['BASE', desc_col]].dropna()
                    df_display = df_display[df_display['BASE'].str.strip() != '']
                    
                    # Renomear colunas para exibição
                    df_display.columns = ['BASE', 'DESCRIÇÃO']
                    
                    # Converter para maiúsculas para consistência visual
                    df_display['BASE'] = df_display['BASE'].str.upper()
                    
                    if not df_display.empty:
                        st.dataframe(
                            df_display,
                            use_container_width=True,
                            hide_index=True
                        )
                    else:
                        st.info("🗂️ Nenhuma base com descrição encontrada")
                else:
                    st.warning("⚠️ Coluna DESCRIÇÃO não encontrada na aba BASES")
            else:
                st.error("❌ Erro ao carregar dados da aba BASES")
                
        except Exception as e:
            st.error(f"❌ Erro ao carregar bases: {str(e)}")
    
    # Informações adicionais
    st.markdown("---")
    st.markdown("""
    **ℹ️ Informações:**
    - As páginas e bases são carregadas automaticamente do Google Sheets
    - Cada base é associada ao seu respectivo histórico no sistema
    - As descrições ajudam a entender a funcionalidade de cada componente
    """)

# Verificar acesso
verificar_acesso_manutencao()

# Interface principal
tab1, tab2, tab3 = st.tabs(["👥 Usuários", "➕ Adicionar Usuário", "📋 Descrição"])

with tab1:
    interface_visualizacao_usuarios()

with tab2:
    interface_adicionar_usuario()

with tab3:
    interface_descricao()

# Rodapé
rodape_desenvolvedor()