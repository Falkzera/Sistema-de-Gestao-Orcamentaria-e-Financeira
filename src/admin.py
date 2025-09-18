import streamlit as st
import os
import socket
from utils.auth.auth import func_load_cadastro_usuarios

def modo_local():
    """
    Verifica se a aplicação está rodando localmente (modo desenvolvedor)
    """
    try:
        # Verifica se está rodando em localhost ou 127.0.0.1
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)

        # Verifica variáveis de ambiente que indicam desenvolvimento
        is_dev_env = (
            os.getenv('STREAMLIT_SERVER_PORT') is not None or
            os.getenv('STREAMLIT_DEV_MODE') == 'true' or
            'localhost' in str(os.getenv('STREAMLIT_SERVER_ADDRESS', '')) or
            '127.0.0.1' in str(os.getenv('STREAMLIT_SERVER_ADDRESS', ''))
        )
        
        # Verifica se está rodando em porta de desenvolvimento (8501 é padrão do Streamlit)
        dev_port = os.getenv('STREAMLIT_SERVER_PORT', '8501')
        
        return is_dev_env or dev_port == '8501'
        
    except Exception:
        return False

def enable_developer_mode():
    """
    Ativa configurações de modo desenvolvedor
    """
    
    # Inicializa estado do modo desenvolvedor se não existir
    if 'dev_impersonation' not in st.session_state:
        st.session_state.dev_impersonation = False
    
    # Adiciona indicador visual de modo desenvolvedor
    dev_mode_active = st.sidebar.checkbox(
        "**ATIVAR MODO DESENVOLVEDOR**", 
        value=st.session_state.dev_impersonation
    )
    
    # Atualiza o estado persistente usando apenas dev_impersonation
    st.session_state.dev_impersonation = dev_mode_active
    
    if dev_mode_active:       
        # Seção de impersonificação de usuário
        st.sidebar.markdown("---")
        st.sidebar.subheader("**SELECIONE O USUÁRIO**")
        
        # Obtém lista de usuários do Google Sheets
        try:
            df_usuarios = func_load_cadastro_usuarios()
            if not df_usuarios.empty:
                # Cria lista de usuários no formato "NOME (CPF)"
                usuarios_disponiveis = []
                for _, row in df_usuarios.iterrows():
                    nome = str(row['NOME']).strip()
                    cpf = str(row['CPF']).strip()
                    usuario_display = f"{nome} ({cpf})"
                    usuarios_disponiveis.append(usuario_display)
            else:
                usuarios_disponiveis = ["usuario_teste"]
        except Exception as e:
            print(f"❌ Erro ao carregar usuários do Google Sheets: {str(e)}")
            usuarios_disponiveis = ["usuario_teste"]
        
        # Adiciona opção "Nenhum" para não simular usuário
        opcoes_usuario = ["Nenhum (Login normal)"] + usuarios_disponiveis
        
        # Inicializa seleção de usuário baseada no dev_user_display se existir
        current_user_display = st.session_state.get('dev_user_display', "Nenhum (Login normal)")
        
        # Selectbox para escolher usuário
        usuario_selecionado = st.sidebar.selectbox(
            "Simular como usuário:",
            opcoes_usuario,
            index=opcoes_usuario.index(current_user_display) if current_user_display in opcoes_usuario else 0,
            help="Selecione um usuário para simular o login automático"
        )
        
        # Se um usuário foi selecionado (não "Nenhum")
        if usuario_selecionado != "Nenhum (Login normal)":
            # Extrai o CPF do formato "NOME (CPF)"
            try:
                cpf_usuario = usuario_selecionado.split('(')[1].split(')')[0].strip()
                # Ativa impersonificação usando o CPF como identificador
                st.session_state.logged_in = True
                st.session_state.usuario_atual = cpf_usuario
                st.session_state.dev_user_display = usuario_selecionado  # Para exibição
            except:
                # Fallback se não conseguir extrair o CPF
                st.session_state.logged_in = True
                st.session_state.usuario_atual = usuario_selecionado
            
        else:
            # Remove impersonificação se "Nenhum" for selecionado
            if 'logged_in' in st.session_state:
                st.session_state.logged_in = False
            if 'usuario_atual' in st.session_state:
                del st.session_state.usuario_atual
            if 'dev_user_display' in st.session_state:
                del st.session_state.dev_user_display
        
        # Botão de reset
        
        # Habilita debug info
        st.sidebar.markdown("---")
        if st.sidebar.checkbox("**ATIVAR DEBUG**", value=False):
            st.sidebar.write("---")
            st.sidebar.write("**Informações do Cache:**")
            st.sidebar.write(st.cache_data)
            st.sidebar.write(st.cache_resource)
            st.sidebar.write("---")
            st.sidebar.write("**Informações da Session State:**")
            st.sidebar.write(st.session_state)
            st.sidebar.write("---")
            st.sidebar.write("**Usuários do Google Sheets:**")
            try:
                df_debug = func_load_cadastro_usuarios()
                if not df_debug.empty:
                    st.sidebar.write(f"Total de usuários: {len(df_debug)}")
                    st.sidebar.dataframe(df_debug[['NOME', 'CPF', 'UNIDADE']].head(5))
                else:
                    st.sidebar.write("Nenhum usuário encontrado")
            except Exception as e:
                st.sidebar.write(f"Erro ao carregar usuários: {str(e)}")
        
        st.sidebar.markdown("---")

def check_and_enable_dev_mode():
    """
    Função principal que verifica se deve ativar o modo desenvolvedor
    """
    if modo_local():
        enable_developer_mode()
        return True
    return False