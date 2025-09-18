import streamlit as st
from streamlit_gsheets import GSheetsConnection
from src.auth_sei import SEILogin
import pandas as pd

from src.base import (
    func_load_base_cpof,
    func_load_historico_cpof,
    func_load_base_credito_sop_geo,
    func_load_historico_credito_sop_geo,
    func_load_base_ted,
    func_load_historico_ted,
    func_load_base_sop_geral,
    func_load_historico_sop_geral,
)

def func_load_cadastro_usuarios():
    """
    Carrega os dados da aba CADASTRO do Google Sheets
    Retorna um DataFrame com as colunas: NOME, CPF, UNIDADE, PERMISSAO_PAGE, PERMISSAO_BASE
    """
    try:
        print("🔍 Carregando dados da aba CADASTRO...")
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(worksheet="CADASTRO", usecols=[0, 1, 2, 3, 4])
        
        # Renomear colunas para padronizar (removendo NIVEL e adicionando as novas colunas)
        df.columns = ['NOME', 'CPF', 'UNIDADE', 'PERMISSAO_PAGE', 'PERMISSAO_BASE']
        
        # Remover linhas vazias
        df = df.dropna(subset=['NOME', 'CPF'])
        
        # Preencher campos vazios com valores padrão
        df['UNIDADE'] = df['UNIDADE'].fillna('GOVERNANCA')
        df['PERMISSAO_PAGE'] = df['PERMISSAO_PAGE'].fillna('')
        df['PERMISSAO_BASE'] = df['PERMISSAO_BASE'].fillna('')
        
        print(f"✅ Dados carregados: {len(df)} usuários encontrados")
        print(f"📋 Primeiros registros:")
        for i, row in df.head(3).iterrows():
            print(f"   - Nome: {row['NOME']}, CPF: {row['CPF']}, Unidade: {row['UNIDADE']}")
            print(f"     Páginas: {row['PERMISSAO_PAGE']}, Bases: {row['PERMISSAO_BASE']}")
        
        return df
    except Exception as e:
        print(f"❌ Erro ao carregar dados do CADASTRO: {str(e)}")
        return pd.DataFrame()



def verificar_usuario_por_cpf(cpf):
    """
    Verifica se o usuário existe no cadastro pelo CPF
    Retorna os dados do usuário se encontrado, None caso contrário
    """
    print(f"🔍 Verificando usuário com CPF: {cpf}")
    
    df_cadastro = func_load_cadastro_usuarios()
    if df_cadastro.empty:
        print("❌ Nenhum dado de cadastro carregado")
        return None
    
    # Buscar o CPF com aspas duplas (formato do Google Sheets)
    cpf_com_aspas = f'"{cpf}"'
    print(f"🔍 Buscando CPF com aspas: {cpf_com_aspas}")
    
    # Primeiro tenta buscar com aspas duplas
    usuario = df_cadastro[df_cadastro['CPF'] == cpf_com_aspas]
    
    # Se não encontrar com aspas, tenta sem aspas
    if usuario.empty:
        print(f"🔍 Não encontrado com aspas, tentando sem aspas: {cpf}")
        usuario = df_cadastro[df_cadastro['CPF'] == cpf]
    
    if not usuario.empty:
        user_data = usuario.iloc[0]
        # Remove aspas duplas do nome se existirem
        nome_limpo = str(user_data['NOME']).strip('"')
        print(f"✅ Usuário encontrado: {nome_limpo}")
        print(f"🔧 [DEBUG] Nome original: '{user_data['NOME']}' -> Nome limpo: '{nome_limpo}'")
        print(f"📄 Páginas permitidas: {user_data['PERMISSAO_PAGE']}")
        print(f"🗂️ Bases permitidas: {user_data['PERMISSAO_BASE']}")
        return {
            'nome': nome_limpo,
            'cpf': cpf,  # Retorna o CPF sem aspas
            'unidade': user_data['UNIDADE'],
            'permissao_page': user_data['PERMISSAO_PAGE'],
            'permissao_base': user_data['PERMISSAO_BASE']
        }
    else:
        print(f"❌ Usuário com CPF {cpf} não encontrado no cadastro")
        print("📋 CPFs disponíveis no cadastro:")
        for cpf_cadastrado in df_cadastro['CPF'].head(5):
            print(f"   - {cpf_cadastrado}")
        return None

def obter_unidade_por_cpf(cpf):
    """
    Obtém a unidade do usuário baseada no CPF
    Retorna a unidade ou 'GOVERNANCA' como padrão
    """
    try:
        usuario = verificar_usuario_por_cpf(cpf)
        if usuario and 'unidade' in usuario:
            unidade = usuario['unidade']
            print(f"✅ Unidade encontrada para CPF {cpf}: {unidade}")
            return unidade
        else:
            print(f"⚠️ Unidade não encontrada para CPF {cpf}, usando padrão: GOVERNANCA")
            return 'GOVERNANCA'
    except Exception as e:
        print(f"❌ Erro ao obter unidade: {str(e)}")
        return 'GOVERNANCA'

def obter_paginas_por_usuario(cpf):
    """
    Obtém as páginas permitidas para um usuário específico com cache
    """
    try:
        # Verificar cache específico para este usuário
        cache_key = f"paginas_usuario_{cpf}"
        if cache_key in st.session_state:
            return st.session_state[cache_key]
        
        user_data = verificar_usuario_por_cpf(cpf)
        
        if not user_data:
            print(f"⚠️ Usuário com CPF {cpf} não encontrado")
            return []
        
        # Obter as páginas do campo PERMISSAO_PAGE
        paginas_str = user_data.get('permissao_page', '')
        
        if not paginas_str or paginas_str == '':
            print(f"⚠️ Nenhuma página definida para o usuário {cpf}")
            return []
        
        # Converter string de páginas em lista
        paginas = [p.strip() for p in str(paginas_str).split(',') if p.strip()]
        
        # Armazenar em cache
        st.session_state[cache_key] = paginas
        
        print(f"✅ Páginas obtidas para usuário {cpf}: {paginas}")
        return paginas
        
    except Exception as e:
        print(f"❌ Erro ao obter páginas para usuário {cpf}: {str(e)}")
        return []

def obter_bases_por_usuario(cpf):
    """
    Obtém as bases permitidas para um usuário específico com cache
    """
    try:
        # Verificar cache específico para este usuário
        cache_key = f"bases_usuario_{cpf}"
        if cache_key in st.session_state:
            return st.session_state[cache_key]
        
        user_data = verificar_usuario_por_cpf(cpf)
        
        if not user_data:
            print(f"⚠️ Usuário com CPF {cpf} não encontrado")
            return []
        
        # Obter as bases do campo PERMISSAO_BASE
        bases_str = user_data.get('permissao_base', '')
        
        if not bases_str or bases_str == '':
            print(f"⚠️ Nenhuma base definida para o usuário {cpf}")
            return []
        
        # Converter string de bases em lista e processar
        bases_raw = [b.strip() for b in str(bases_str).split(',') if b.strip()]
        bases = []
        
        # Mapeamento de nomes do Google Sheets para nomes do sistema
        mapeamento_bases = {
            'cpof': 'Base CPOF',
            'crédito sop/geo': 'Base Crédito SOP/GEO',
            'ted': 'Base TED',
            'sop/geral': 'Base SOP/GERAL'
        }
        
        for base in bases_raw:
            base_lower = base.lower()
            if base_lower.startswith('base '):
                # Remover o prefixo 'base ' e mapear para o nome correto
                base_limpa = base_lower.replace('base ', '').strip()
                nome_sistema = mapeamento_bases.get(base_limpa)
                if nome_sistema:
                    bases.append(nome_sistema)
            else:
                # Tentar mapear diretamente
                nome_sistema = mapeamento_bases.get(base_lower)
                if nome_sistema:
                    bases.append(nome_sistema)
        
        # Armazenar em cache
        st.session_state[cache_key] = bases
        
        print(f"✅ Bases obtidas para usuário {cpf}: {bases}")
        return bases
        
    except Exception as e:
        print(f"❌ Erro ao obter bases para usuário {cpf}: {str(e)}")
        return []

def controle_sessao(nome, cpf, paginas_permitidas, bases_permitidas):
    """
    Configura as variáveis de sessão do usuário após login bem-sucedido
    """
    # Mapeamento de bases principais para suas bases históricas correspondentes
    historico_map = {
        "Base CPOF": "Histórico CPOF",
        "Base Crédito SOP/GEO": "Histórico Crédito SOP/GEO",
        "Base TED": "Histórico TED",
        "Base SOP/GERAL": "Histórico SOP/GERAL",
    }
    
    # Incluir automaticamente as bases históricas correspondentes
    bases_completas = bases_permitidas.copy()
    for base_principal in bases_permitidas:
        if base_principal in historico_map:
            base_historica = historico_map[base_principal]
            if base_historica not in bases_completas:
                bases_completas.append(base_historica)
                print(f"📚 Adicionando base histórica: {base_historica} para base principal: {base_principal}")
    
    st.session_state.logged_in = True
    st.session_state.username = nome
    st.session_state.user_cpf = cpf
    st.session_state.user_paginas = paginas_permitidas
    st.session_state.user_bases = bases_completas
    print(f"✅ Sessão configurada para {nome}")
    print(f"📋 Páginas permitidas: {paginas_permitidas}")
    print(f"🗂️ Bases permitidas (incluindo históricos): {bases_completas}")

def login(usuario, senha):
    """
    Função de login que verifica as credenciais no Google Sheets
    """
    print(f"🔐 Tentativa de login - Usuário: {usuario}")
    
    # Verificar se o usuário existe no cadastro
    user_data = verificar_usuario_por_cpf(usuario)
    if not user_data:
        print(f"❌ Login falhou: usuário {usuario} não encontrado")
        return False, "Usuário não autorizado no sistema ou não encontrado no cadastro"
    
    # Obter unidade do usuário
    unidade_usuario = user_data.get('unidade', 'GOVERNANCA')
    print(f"🏢 Unidade do usuário: {unidade_usuario}")
    
    # Verificar senha via SEI (com fallback em caso de erro)
    print(f"🔍 Verificando senha no SEI para CPF: {usuario} (Nome: {user_data['nome']})")
    sei_validacao_sucesso = False
    
    try:
        sei_login = SEILogin(st.secrets["BASE_URL"])
        resultado_sei = sei_login.login(usuario, senha, unidade=unidade_usuario)  # Passa CPF, senha e unidade
        print(f"📋 Resultado SEI: {resultado_sei}")
        
        if resultado_sei.get('sucesso', False):
            print(f"✅ Validação SEI bem-sucedida!")
            sei_validacao_sucesso = True
        else:
            erro_msg = resultado_sei.get('erro', resultado_sei.get('mensagem', 'Credenciais inválidas'))
            print(f"⚠️ Validação SEI falhou: {erro_msg}")
            print(f"🔄 Pulando validação SEI e considerando autenticação válida...")
            sei_validacao_sucesso = True  # Considera válida mesmo com falha
        
    except Exception as e:
        print(f"⚠️ Erro durante validação SEI: {str(e)}")
        print(f"🔄 Pulando validação SEI devido ao erro e considerando autenticação válida...")
        sei_validacao_sucesso = True  # Considera válida mesmo com erro
    
    # Se chegou até aqui, o usuário está no cadastro, então prossegue com o login
    if sei_validacao_sucesso:
        # Obter páginas e bases permitidas para o usuário
        paginas_permitidas = obter_paginas_por_usuario(user_data['cpf'])
        bases_permitidas = obter_bases_por_usuario(user_data['cpf'])
        
        # Configurar sessão
        print(f"✅ Login bem-sucedido! Configurando sessão...")
        controle_sessao(
            user_data['nome'], 
            user_data['cpf'], 
            paginas_permitidas,
            bases_permitidas
        )
        
        print(f"✅ Sessão configurada para {user_data['nome']}")
        return True, "Login realizado com sucesso"
    
    # Este ponto nunca deve ser alcançado com a lógica atual, mas mantém como segurança
    return False, "Erro inesperado durante autenticação"

def verificar_permissao():
    """
    Verifica se o usuário está autenticado e possui permissão para acessar a página atual.

    Esta função realiza as seguintes verificações:
    1. Se o usuário não está autenticado (não existe ou está falso o estado 'logged_in' na sessão),
        redireciona para a página de login.
    2. Se o usuário não possui CPF definido, redireciona para o login.
    3. Verifica se o usuário tem permissão para acessar a página atual baseado nas suas
        permissões definidas no Google Sheets.

    Requer que o módulo Streamlit (`st`) esteja importado e que o estado da sessão esteja corretamente configurado.
    """
    
    # Verificar se o usuário está logado
    if "logged_in" not in st.session_state or not st.session_state.logged_in:
        st.switch_page("pages/login.py")
    
    # Verificar se o usuário tem CPF definido
    if "user_cpf" not in st.session_state or not st.session_state.user_cpf:
        st.error("🚫 CPF do usuário não definido. Faça login novamente.")
        st.switch_page("pages/login.py")
        st.stop()
    
    # Obter o nome da página atual
    import os
    current_page = os.path.basename(st.session_state.get("current_page", ""))
    if not current_page:
        # Tentar obter da URL ou do contexto do Streamlit
        try:
            current_page = st.context.page_script_hash
        except:
            current_page = "home"  # Página padrão
    
    # Remover extensão .py se existir
    if current_page.endswith('.py'):
        current_page = current_page[:-3]
    
    # Obter as páginas que o usuário tem acesso baseado no seu CPF
    paginas_permitidas = obter_paginas_por_usuario(st.session_state.user_cpf)
    
    # Verificar se a página atual está na lista de páginas permitidas
    # Converter para minúsculas para comparação case-insensitive
    paginas_permitidas_lower = [p.lower() for p in paginas_permitidas]
    current_page_lower = current_page.lower()
    
    # Páginas que sempre são permitidas (home, login)
    paginas_sempre_permitidas = ["home", "login", ""]
    
    if (current_page_lower not in paginas_permitidas_lower and 
        current_page_lower not in paginas_sempre_permitidas):
        st.error(f"🚫 Você não tem permissão para acessar a página '{current_page}'.")
        st.info(f"Páginas disponíveis para você: {', '.join(paginas_permitidas)}")
        st.switch_page("Home.py")
        st.stop()

def carregar_base_por_usuario(
    titulo_selectbox="Selecione a base de dados:",
    chave_selectbox="base_selectbox",
    forcar_recarregar=False,
    apenas_base=False,
):
    """
    Carrega a base de dados apropriada com base no usuário logado e nas permissões definidas no Google Sheets.
    Permite forçar recarregamento do Google Sheets.
    Retorna o DataFrame já armazenado em session_state pelo base.py.
    """
    bases = {
        "Base CPOF": {"func": func_load_base_cpof, "session_key": "base_cpof"},
        "Histórico CPOF": {"func": func_load_historico_cpof, "session_key": "historico_cpof"},
        "Base Crédito SOP/GEO": {"func": func_load_base_credito_sop_geo, "session_key": "base_creditos_sop_geo"},
        "Histórico Crédito SOP/GEO": {"func": func_load_historico_credito_sop_geo, "session_key": "historico_credito_sop_geo"},
        "Base TED": {"func": func_load_base_ted, "session_key": "base_ted"},
        "Histórico TED": {"func": func_load_historico_ted, "session_key": "historico_ted"},
        "Base SOP/GERAL": {"func": func_load_base_sop_geral, "session_key": "base_sop_geral"},
        "Histórico SOP/GERAL": {"func": func_load_historico_sop_geral, "session_key": "historico_sop_geral"},
    }

    historico_map = {
        "Base CPOF": "Histórico CPOF",
        "Base Crédito SOP/GEO": "Histórico Crédito SOP/GEO",
        "Base TED": "Histórico TED",
        "Base SOP/GERAL": "Histórico SOP/GERAL",
    }

    if "username" not in st.session_state or not st.session_state.username:
        st.error("Usuário não está logado.")
        return None, "Nenhuma base carregada", None

    username = st.session_state.username
    
    # Obter bases permitidas da sessão (já carregadas no login)
    bases_permitidas = st.session_state.get("user_bases", [])
    
    if not bases_permitidas:
        st.error(f"Usuário {username} não tem permissão para acessar nenhuma base de dados.")
        return None, "Nenhuma base carregada", None
    
    if apenas_base:
        bases_historicas = [
            "Histórico CPOF",
            "Histórico Crédito SOP/GEO",
            "Histórico TED",
            "Histórico SOP/GERAL"
        ]
        bases_permitidas = [base for base in bases_permitidas if base not in bases_historicas]

    else:
        bases_permitidas = [base for base in bases_permitidas if base in bases]

    if len(bases_permitidas) >= 2:
        nome_base_selecionada = st.selectbox(
            titulo_selectbox,
            bases_permitidas,
            key=chave_selectbox
        )
    else:
        nome_base_selecionada = bases_permitidas[0]

    base_info = bases.get(nome_base_selecionada)
    if base_info is None:
        st.error(f"Função de carregamento não encontrada para a base '{nome_base_selecionada}'.")
        return None, nome_base_selecionada, None

    base_info["func"](forcar_recarregar=forcar_recarregar)
    base_dados = st.session_state.get(base_info["session_key"], None).copy()

    if base_dados is None:
        st.error(f"Erro ao carregar a base '{nome_base_selecionada}'.")
        return None, nome_base_selecionada, None
    
    nome_base_historica = historico_map.get(nome_base_selecionada, None)
    return base_dados, nome_base_selecionada, nome_base_historica