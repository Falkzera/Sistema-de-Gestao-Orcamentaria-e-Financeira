# SIGOF - Sistema de Gestão Orçamentário e Financeiro

<div align="center">

<img src="./image/sigof.png" alt="SIGOF Logo" width="400"/>

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-red.svg)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Build Status](https://img.shields.io/badge/Build-Passing-brightgreen.svg)]()
[![Code Quality](https://img.shields.io/badge/Code%20Quality-A-brightgreen.svg)]()
[![Coverage](https://img.shields.io/badge/Coverage-85%25-yellow.svg)]()

**Sistema web moderno para gestão orçamentária e financeira do Estado de Alagoas**

*Desenvolvido com Python/Streamlit • Integração Google Sheets • Relatórios Automatizados*

</div>

---

## 📋 Índice

- [Sobre o Projeto](#-sobre-o-projeto)
- [Arquitetura](#️-arquitetura)
- [Instalação](#-instalação)
- [Configuração](#️-configuração)
- [Estrutura de Arquivos](#-estrutura-de-arquivos)
- [Funcionalidades](#-funcionalidades)
- [APIs e Integrações](#-apis-e-integrações)
- [Fluxo de Dados](#-fluxo-de-dados)
- [Autenticação](#-autenticação)
- [Desenvolvimento](#-desenvolvimento)
- [Licença](#-licença)
- [Contato](#-contato)

---

## 🎯 Sobre o Projeto

O **SIGOF** (Sistema de Gestão Orçamentário e Financeiro) é uma aplicação web desenvolvida em Python com Streamlit para modernizar e centralizar a gestão orçamentária do Estado de Alagoas. O sistema substitui planilhas Excel dispersas por uma solução integrada, colaborativa e auditável.

### 🎯 Objetivos Principais

- **Centralização**: Unificar dados orçamentários em uma única plataforma
- **Automação**: Eliminar processos manuais propensos a erros
- **Colaboração**: Permitir acesso simultâneo de múltiplos usuários
- **Rastreabilidade**: Manter histórico completo de todas as modificações
- **Integração**: Conectar com APIs externas para dados atualizados
- **Padronização**: Estabelecer workflows consistentes e relatórios uniformes

### 📊 Métricas do Sistema

| Métrica | Valor |
|---------|-------|
| **Linhas de Código** | +10k |
| **Arquivos Python** | +40 |
| **Módulos Principais** | 9 |
| **Integrações Externas** | 6+ APIs |
| **Tipos de Relatório** | 3 principais + dashboards |

---

## 🏗️ Arquitetura

### Stack Tecnológica

```mermaid
graph TB
    subgraph "Frontend"
        A[Streamlit UI]
        B[Plotly Charts]
        C[AgGrid Tables]
    end
    
    subgraph "Backend"
        D[Python 3.8+]
        E[Pandas DataFrames]
        F[Session State]
    end
    
    subgraph "Storage"
        G[Google Sheets API]
        H[Google Drive]
    end
    
    subgraph "External APIs"
        I[IBGE]
        J[ANP]
        K[MDIC]
        L[SEFAZ]
    end
    
    A --> D
    B --> E
    C --> E
    D --> F
    F --> G
    G --> H
    D --> I
    D --> J
    D --> K
    D --> L
```

### Tecnologias Utilizadas

| Categoria | Tecnologia | Versão | Propósito |
|-----------|------------|--------|-----------|
| **Framework Web** | Streamlit | 1.28+ | Interface de usuário |
| **Linguagem** | Python | 3.8+ | Lógica de negócio |
| **Manipulação de Dados** | Pandas | 2.0+ | Processamento de dados |
| **Visualização** | Plotly | 5.0+ | Gráficos interativos |
| **Tabelas** | Streamlit-AgGrid | 0.3+ | Tabelas avançadas |
| **Armazenamento** | Google Sheets | API v4 | Persistência de dados |
| **Autenticação** | Google OAuth2 | 2.0 | Acesso seguro |
| **PDF Generation** | WeasyPrint | 60+ | Relatórios em PDF |
| **HTTP Requests** | Requests | 2.31+ | APIs externas |

### Design Patterns

- **MVC Pattern**: Separação clara entre Model (src/), View (pages/) e Controller (utils/)
- **Repository Pattern**: Camada de abstração para acesso a dados (src/base.py)
- **Factory Pattern**: Geração dinâmica de relatórios (utils/confeccoes/)
- **Observer Pattern**: Sistema de cache e atualização de estado
- **Strategy Pattern**: Diferentes estratégias de autenticação e validação

---

## 🚀 Instalação

### Pré-requisitos

- **Python 3.8+**
- **pip** (gerenciador de pacotes Python)
- **Conta Google** com acesso ao Google Sheets API
- **Git** (para clonagem do repositório)

### Instalação Local

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/sigof.git
cd sigof

# 2. Crie um ambiente virtual
python -m venv venv

# 3. Ative o ambiente virtual
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 4. Instale as dependências
pip install -r requirements.txt

# 5. Configure as variáveis de ambiente
cp .env.example .env
# Edite o arquivo .env com suas configurações

# 6. Execute a aplicação
streamlit run Home.py
```

### Dependências Principais

```txt
streamlit>=1.28.0
pandas>=2.0.0
plotly>=5.0.0
streamlit-aggrid>=0.3.0
streamlit-gsheets-connection>=0.0.3
gspread>=5.0.0
google-auth>=2.0.0
google-auth-oauthlib>=1.0.0
google-auth-httplib2>=0.1.0
weasyprint>=60.0
requests>=2.31.0
python-dotenv>=1.0.0
```

### Instalação via Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "Home.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

```bash
# Build e execução
docker build -t sigof .
docker run -p 8501:8501 sigof
```

---

## ⚙️ Configuração

### Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
# Google Sheets Configuration
GOOGLE_SHEETS_URL=https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID
GOOGLE_SERVICE_ACCOUNT_FILE=path/to/exemple-service-account.json

# Application Settings
APP_TITLE=SIGOF - Sistema de Gestão Orçamentário
APP_ICON=🏛️
DEBUG_MODE=False

# Cache Settings
CACHE_TTL=300
SESSION_TIMEOUT=3600

# External APIs
IBGE_API_URL
ANP_API_URL
MDIC_API_URL
SEFAZ_API_URL
```

### Configuração do Google Sheets

#### 1. Criar Service Account

```bash
# 1. Acesse o Google Cloud Console
# 2. Crie um novo projeto ou selecione existente
# 3. Ative a Google Sheets API
# 4. Crie uma Service Account
# 5. Baixe o arquivo JSON de credenciais
```

#### 2. Configurar Permissões

```python
# Compartilhe a planilha com o email da service account
# Exemplo: sigof-service@projeto-123456.iam.gserviceaccount.com
# Permissão: Editor
```

#### 3. Estrutura das Planilhas

```
Google Sheets Document:
├── Base CPOF                    # Processos do CPOF
├── Base Crédito SOP/GEO        # Créditos adicionais
├── Histórico CPOF              # Auditoria CPOF
├── Histórico Crédito SOP/GEO   # Auditoria créditos
└── Configurações               # Parâmetros do sistema
```

### Configuração de Autenticação

Edite o arquivo `.streamlit/secrets.toml`:

```toml
[passwords]
admin = "senha_admin_hash"
usuario1 = "senha_usuario1_hash"
usuario2 = "senha_usuario2_hash"

[permissions]
admin = ["Base CPOF", "Base Crédito SOP/GEO"]
usuario1 = ["Base CPOF"]
usuario2 = ["Base Crédito SOP/GEO"]

[gcp_service_account]
type = "exemple-service_account"
project_id = "seu-projeto-id"
private_key_id = "key-id"
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "exemple.gserviceaccount.com"
client_id = "exemple"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
```

---

## 📁 Estrutura de Arquivos

```
sigof_project/
├── 📄 Home.py                           # Página principal (250 linhas)
│   ├── Dashboard de indicadores orçamentários
│   ├── Métricas do orçamento
│   ├── Cálculo de limite de execução
│   └── Gráficos de pizza e indicadores visuais
│
├── 📁 pages/                           # Módulos da aplicação (444 linhas)
│   ├── 🔐 login.py                     # Sistema de autenticação (34 linhas)
│   ├── ➕ cadastro.py                  # Cadastro de processos (24 linhas)
│   ├── 👁️ visualizar.py                # Visualização e edição (50 linhas)
│   ├── 💬 canal_resposta_cpof.py       # Interface CPOF (76 linhas)
│   ├── 📊 relatorio.py                 # Geração de relatórios (159 linhas)
│   ├── 📜 historico.py                 # Auditoria e histórico (71 linhas)
│   └── 📈 dashboards.py                # Dashboards especializados (30 linhas)
│
├── 📁 src/                             # Lógica de negócio (1.229 linhas)
│   ├── 🗄️ base.py                      # Camada de dados (55 linhas)
│   │   ├── func_load_base_cpof()
│   │   ├── func_load_base_credito_sop_geo()
│   │   └── Gerenciamento de cache
│   │
│   ├── ☁️ google_drive_utils.py        # Integração Google Drive (306 linhas)
│   │   ├── Upload/download de arquivos
│   │   ├── Autenticação OAuth2
│   │   └── Gestão de permissões
│   │
│   ├── 💾 salvar_alteracoes.py         # Persistência de dados (269 linhas)
│   │   ├── salvar_base()
│   │   ├── salvar_modificacoes_selectbox_mae()
│   │   └── Validação antes do salvamento
│   │
│   ├── 📝 salvar_historico.py          # Sistema de auditoria (135 linhas)
│   │   ├── salvar_modificacao()
│   │   ├── exibir_historico()
│   │   └── Comparação de estados
│   │
│   └── ✏️ editar_processo_geral.py     # Edição de processos (464 linhas)
│       ├── formulario_edicao_processo()
│       ├── Validação de campos
│       └── Sanitização de dados
│
├── 📁 utils/                            # Componentes reutilizáveis
│   ├── 🔐 auth/                         # Autenticação (132 linhas)
│   │   ├── login()
│   │   ├── verificar_permissao()
│   │   └── carregar_base_por_usuario()
│   │
│   ├── 📋 confeccoes/                   # Relatórios (2.565 linhas - 27% do código)
│   │   ├── 🎨 formatar.py               # Formatação (935 linhas)
│   │   ├── 📄 gerar_baixar_confeccao.py # PDFs (155 linhas)
│   │   ├── 📝 confeccao_ata.py          # Atas CPOF (138 linhas)
│   │   ├── 📊 resumos.py                # Resumos orçamentários (340 linhas)
│   │   ├── 📈 dashboards/               # Dashboards específicos
│   │   └── 📋 relatorio/                # Relatórios especializados
│   │
│   ├── 💰 limite/                       # Cálculos orçamentários (26 linhas)
│   │   ├── ORÇAMENTO_APROVADO_2025 = R$ 18.544.820.466,00
│   │   ├── VALOR_DO_LIMITE = 10% do orçamento
│   │   └── calcular_limite_credito_atual()
│   │
│   ├── 🏷️ opcoes_coluna/               # Validações (238 linhas)
│   │   ├── Listas de opções para dropdowns
│   │   ├── Mapeamento de cores por categoria
│   │   └── Validadores específicos
│   │
│   ├── 🔍 filtros/                      # Sistema de busca (131 linhas)
│   │   ├── Filtros por ano/mês
│   │   ├── Busca por palavras-chave
│   │   └── Modos de busca "E" e "OU"
│   │
│   └── 🎨 ui/                           # Interface (779 linhas)
│       ├── 📊 dataframe.py             # Tabelas AgGrid (510 linhas)
│       ├── 🎨 display.py               # Customização visual (268 linhas)
│       └── Padronização de estilos
│
├── 📁 image/                            # Assets visuais
│   ├── logo_sigof.png
│   ├── favicon.ico
│   └── backgrounds/
│
├── 📁 .streamlit/                       # Configurações Streamlit
│   ├── config.toml
│   └── secrets.toml
│
├── 📄 requirements.txt                  # Dependências Python
├── 📄 .env.example                      # Exemplo de variáveis de ambiente
├── 📄 .gitignore                        # Arquivos ignorados pelo Git
├── 📄 Dockerfile                        # Container Docker
├── 📄 docker-compose.yml               # Orquestração Docker
└── 📄 README_TECNICO.md                # Este documento
```

### Detalhamento dos Módulos Principais

#### 🏠 **Home.py** - Dashboard Principal
```python
# Funcionalidades principais:
- Métricas do orçamento aprovado do ano corrente
- Cálculo do limite de execução do ano corrente

# Integrações:
- utils.limite.limite_credito (cálculos)
- src.base (carregamento de dados)
- utils.confeccoes.formatar (formatação)
```

#### 📄 **Pages/** - Módulos da Aplicação
```python
# login.py - Autenticação
- Sistema baseado em usuário/senha
- Integração com utils.auth.auth
- Redirecionamento pós-login

# cadastro.py - Cadastro de Processos
- Interface para novos processos
- Controle de permissões por usuário

# visualizar.py - Visualização e Edição
- Visualização tabular de processos
- Sistema de filtros avançados
- Edição inline de processos
- Geração de resumos orçamentários

# canal_resposta_cpof.py - Interface CPOF
- Manifestação de pareceres técnicos

# relatorio.py - Geração de Relatórios
- Demais relatórios

# historico.py - Auditoria
- Rastreamento de modificações
- Visualização de histórico por processo
- Auditoria de alterações

# dashboards.py - Dashboards Especializados
- Dashboards
```

---

## 🚀 Funcionalidades

### 1. 📊 **Gestão de Processos Orçamentários**

#### Cadastro de Créditos Adicionais
```python
# Função:
- Cadastro processual
```

#### Edição com Validação Completa
```python
# Validações implementadas:
- Validação e sanitização
```

#### Controle de Situação e Deliberação
```python
# Estados possíveis:
- Status
```

### 2. 💰 **Controle Orçamentário**

#### Monitoramento do Limite de aleteração
```python

def calcular_limite_credito_atual():
    """Calcula métricas do limite orçamentário"""
    return {
        'limite_total': LIMITE_EXECUCAO,
        'limite_executado': valor_executado,
        'limite_disponivel': LIMITE_EXECUCAO - valor_executado,
        'percentual_executado': (valor_executado / LIMITE_EXECUCAO) * 100
    }
```

#### Indicadores Visuais de Execução
```python
# Gráficos implementados:
- Pizza: Executado vs Disponível
- Barras: Evolução mensal
- Gauge: Percentual de execução
- Cards: Métricas principais
```

### 3. 🏛️ **Sistema CPOF**

#### Interface para Membros do Comitê
```python
# Membros com acesso:
- Membros do Cômite
```

#### Workflow de Aprovação
```python
def processar_parecer_cpof(processo_id, membro, parecer, justificativa):
    """Processa parecer de membro do CPOF"""
    # 1. Validar permissões do membro
    # 2. Registrar parecer no histórico
    # 3. Atualizar status do processo
    # 4. Notificar outros membros
    # 5. Gerar ata se todos responderam
```

### 4. 📋 **Relatórios Automatizados**

#### Relatório CPOF Mensal
```python
def gerar_relatorio_cpof(mes, ano):
    """Gera relatório mensal do CPOF"""
    # 1. Filtrar processos do período
    # 2. Agrupar por situação/deliberação
    # 3. Calcular totais e percentuais
    # 4. Gerar gráficos e tabelas
    # 5. Exportar para PDF
```

#### Boletim Conjuntural Alagoano
```python
def gerar_boletim_conjuntural():
    """Gera boletim com dados econômicos"""
    # APIs integradas:
    # - IBGE: Abate de animais, leite industrializado
    # - ANP: Preços e produção de combustíveis
    # - MDIC: Comércio exterior
    # - SEFAZ: Despesas e dotações orçamentárias
```

### 5. 🔒 **Segurança e Auditoria**

#### Sistema de Login por Usuário
```python
def login(username, password):
    """Autentica usuário no sistema"""
    # 1. Verificar credenciais em secrets.toml
    # 2. Validar hash da senha
    # 3. Carregar permissões do usuário
    # 4. Inicializar session state
    # 5. Redirecionar para página principal
```

#### Histórico Completo de Modificações
```python
def salvar_modificacao(usuario, processo_id, campo, valor_anterior, valor_novo):
    """Registra modificação no histórico"""
    historico = {
        'timestamp': datetime.now(),
        'usuario': usuario,
        'processo_id': processo_id,
        'campo': campo,
        'valor_anterior': valor_anterior,
        'valor_novo': valor_novo,
    }
    # Salvar no Google Sheets
```

---

## 🔗 APIs e Integrações

### 🗄️ **Google Sheets API**

#### Configuração
```python
from streamlit_gsheets import GSheetsConnection

# Conexão principal
conn = st.connection("gsheets", type=GSheetsConnection)

# Carregamento de dados
@st.cache_data(ttl=300)
def func_load_base_cpof():
    """Carrega do Google Sheets"""
    return conn.read(
        worksheet="Example",
        usecols=list(range(20)),
        ttl=300
    )
```

#### Worksheets Utilizadas
```python
WORKSHEETS = {
   "Examples"
}
```

### 🌐 **APIs Externas**

#### IBGE - Instituto Brasileiro de Geografia e Estatística
```python
IBGE_ENDPOINTS = {
    'dados'
}

def buscar_dados_ibge(endpoint, params):
    """Busca dados do IBGE"""
    response = requests.get(f"{IBGE_ENDPOINTS[endpoint]}", params=params)
    return response.json()
```

#### ANP - Agência Nacional do Petróleo
```python
def buscar_precos_combustiveis():
    """Busca preços de combustíveis da ANP"""
```

#### MDIC - Ministério do Desenvolvimento, Indústria e Comércio
```python
def buscar_comercio_exterior():
    """Busca dados de comércio exterior"""
```

#### SEFAZ - Secretaria da Fazenda de Alagoas
```python
def buscar_despesas_orgaos():
    """Busca despesas dos órgãos estaduais"""
```

### 🔄 **Integração com Google Drive**

#### Upload de Arquivos
```python
def upload_arquivo_drive(arquivo, pasta_id):
    """Faz upload de arquivo para o Google Drive"""
    service = build('drive', 'v3', credentials=creds)
    
    file_metadata = {
        'name': arquivo.name,
        'parents': [pasta_id]
    }
    
    media = MediaFileUpload(arquivo, resumable=True)
    
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()
    
    return file.get('id')
```

#### Gestão de Permissões
```python
def compartilhar_arquivo(file_id, email, role='reader'):
    """Compartilha arquivo com usuário específico"""
    service = build('drive', 'v3', credentials=creds)
    
    permission = {
        'type': 'user',
        'role': role,
        'emailAddress': email
    }
    
    service.permissions().create(
        fileId=file_id,
        body=permission
    ).execute()
```

---

## 🔄 Fluxo de Dados

### 📊 **Arquitetura de Dados**

```mermaid
graph TD
    subgraph "Data Sources"
        A[Google Sheets]
        B[IBGE API]
        C[ANP API]
        D[MDIC API]
        E[SEFAZ API]
    end
    
    subgraph "Data Layer"
        F[src/base.py]
        G[Session State Cache]
        H[Data Validation]
    end
    
    subgraph "Business Logic"
        I[src/salvar_alteracoes.py]
        J[src/editar_processo_geral.py]
        K[utils/confeccoes/]
    end
    
    subgraph "Presentation"
        L[pages/]
        M[utils/ui/]
        N[Streamlit Components]
    end
    
    A --> F
    B --> F
    C --> F
    D --> F
    E --> F
    F --> G
    G --> H
    H --> I
    H --> J
    H --> K
    I --> L
    J --> L
    K --> L
    L --> M
    M --> N
```

### 🔄 **Fluxo de Autenticação**

```python
def fluxo_autenticacao():
    """Fluxo completo de autenticação"""
    
    # 1. Verificar se usuário está logado
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    # 2. Se não autenticado, mostrar tela de login
    if not st.session_state.authenticated:
        username, password = exibir_tela_login()
        
        # 3. Validar credenciais
        if validar_credenciais(username, password):
            st.session_state.authenticated = True
            st.session_state.username = username
            st.session_state.permissions = carregar_permissoes(username)
            st.rerun()
    
    # 4. Se autenticado, carregar dados permitidos
    else:
        carregar_dados_usuario()
```

### 💾 **Fluxo de Persistência**

```python
def fluxo_salvamento(dados_modificados):
    """Fluxo completo de salvamento"""
    
    # 1. Validação de dados
    erros = validar_dados(dados_modificados)
    if erros:
        exibir_erros(erros)
        return False
    
    # 2. Sanitização
    dados_limpos = sanitizar_dados(dados_modificados)
    
    # 3. Backup do estado anterior
    estado_anterior = obter_estado_atual()
    
    # 4. Salvamento no Google Sheets
    try:
        salvar_no_sheets(dados_limpos)
        
        # 5. Registro no histórico
        registrar_historico(
            usuario=st.session_state.username,
            estado_anterior=estado_anterior,
            estado_novo=dados_limpos
        )
        
        # 6. Atualização do cache
        atualizar_cache()
        
        return True
        
    except Exception as e:
        # 7. Rollback em caso de erro
        restaurar_estado(estado_anterior)
        exibir_erro(f"Erro ao salvar: {e}")
        return False
```

### 📋 **Fluxo de Geração de Relatórios**

```python
def fluxo_relatorio(tipo_relatorio, parametros):
    """Fluxo de geração de relatórios"""
    
    # 1. Validar parâmetros
    if not validar_parametros_relatorio(parametros):
        return None
    
    # 2. Carregar dados necessários
    dados = carregar_dados_relatorio(tipo_relatorio, parametros)
    
    # 3. Buscar dados externos se necessário
    if tipo_relatorio == 'boletim_conjuntural':
        dados_externos = buscar_dados_externos()
        dados.update(dados_externos)
    
    # 4. Processar e formatar dados
    dados_processados = processar_dados_relatorio(dados)
    
    # 5. Gerar visualizações
    graficos = gerar_graficos(dados_processados)
    tabelas = gerar_tabelas(dados_processados)
    
    # 6. Renderizar HTML
    html_content = renderizar_template(
        tipo_relatorio,
        dados=dados_processados,
        graficos=graficos,
        tabelas=tabelas
    )
    
    # 7. Gerar PDF
    pdf_bytes = gerar_pdf(html_content)
    
    # 8. Disponibilizar para download
    return pdf_bytes
```

---

## 🔐 Autenticação

### 🔑 **Sistema de Login**

#### Implementação da Autenticação
```python
import bcrypt
import streamlit as st

def hash_password(password):
    """Gera hash da senha"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password, hashed):
    """Verifica senha contra hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def login(username, password):
    """Autentica usuário"""
    try:
        stored_hash = st.secrets["passwords"][username]
        if verify_password(password, stored_hash):
            st.session_state.authenticated = True
            st.session_state.username = username
            st.session_state.permissions = st.secrets["permissions"][username]
            return True
    except KeyError:
        pass
    return False

def logout():
    """Faz logout do usuário"""
    for key in ['authenticated', 'username', 'permissions']:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()
```

### 🛡️ **Controle de Permissões**

#### Verificação de Acesso
```python
def verificar_permissao(recurso_requerido):
    """Verifica se usuário tem permissão para acessar recurso"""
    if not st.session_state.get('authenticated', False):
        st.error("❌ Acesso negado. Faça login primeiro.")
        st.stop()
    
    user_permissions = st.session_state.get('permissions', [])
    
    if recurso_requerido not in user_permissions:
        st.error(f"❌ Você não tem permissão para acessar: {recurso_requerido}")
        st.stop()
    
    return True

def require_permission(permission):
    """Decorator para verificar permissões"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            verificar_permissao(permission)
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Uso do decorator
@require_permission("Base CPOF")
def editar_processo_cpof():
    """Função que requer permissão específica"""
    pass
```

#### Carregamento Baseado em Permissões
```python
def carregar_base_por_usuario():
    """Carrega dados baseado nas permissões do usuário"""
    user_permissions = st.session_state.get('permissions', [])
    
    dados = {}
    
    if "Base CPOF" in user_permissions:
        dados['cpof'] = func_load_base_cpof()
    
    if "Base Crédito SOP/GEO" in user_permissions:
        dados['credito'] = func_load_base_credito_sop_geo()
    
    if "Relatórios" in user_permissions:
        dados['relatorios'] = True
    
    return dados
```

### 🔒 **Segurança Adicional**

#### Rate Limiting
```python
import time
from collections import defaultdict

# Controle de tentativas de login
login_attempts = defaultdict(list)
MAX_ATTEMPTS = 5
LOCKOUT_TIME = 300  # 5 minutos

def check_rate_limit(username):
    """Verifica limite de tentativas de login"""
    now = time.time()
    attempts = login_attempts[username]
    
    # Remove tentativas antigas
    attempts[:] = [t for t in attempts if now - t < LOCKOUT_TIME]
    
    if len(attempts) >= MAX_ATTEMPTS:
        return False, LOCKOUT_TIME - (now - attempts[0])
    
    return True, 0

def record_login_attempt(username):
    """Registra tentativa de login"""
    login_attempts[username].append(time.time())
```

#### Sanitização de Inputs
```python
import re
import html

def sanitizar_input(valor, tipo='texto'):
    """Sanitiza input do usuário"""
    if valor is None:
        return None
    
    # Escape HTML
    valor = html.escape(str(valor))
    
    if tipo == 'numero_processo':
        # Formato: NNNN.NNNN/AAAA
        pattern = r'^\d{4}\.\d{4}/\d{4}$'
        if not re.match(pattern, valor):
            raise ValueError("Formato de processo inválido")
    
    elif tipo == 'valor_monetario':
        # Remove caracteres não numéricos exceto vírgula e ponto
        valor = re.sub(r'[^\d,.]', '', valor)
        valor = valor.replace(',', '.')
        try:
            float(valor)
        except ValueError:
            raise ValueError("Valor monetário inválido")
    
    elif tipo == 'data':
        # Formato: DD/MM/AAAA
        pattern = r'^\d{2}/\d{2}/\d{4}$'
        if not re.match(pattern, valor):
            raise ValueError("Formato de data inválido")
    
    return valor
```

---

## 👨‍💻 Desenvolvimento

### 🚀 **Como Contribuir**

#### 1. Fork e Clone
```bash
# 1. Faça fork do repositório no GitHub
# 2. Clone seu fork
git clone https://github.com/seu-usuario/sigof.git
cd sigof

# 3. Adicione o repositório original como upstream
git remote add upstream https://github.com/original-repo/sigof.git
```

#### 2. Configuração do Ambiente
```bash
# 1. Crie ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# 2. Instale dependências de desenvolvimento
pip install -r requirements-dev.txt

# 3. Configure pre-commit hooks
pre-commit install
```

#### 3. Workflow de Desenvolvimento
```bash
# 1. Crie branch para sua feature
git checkout -b feature/nova-funcionalidade

# 2. Faça suas alterações
# ... código ...

# 3. Execute testes
pytest tests/

# 4. Execute linting
flake8 src/ utils/ pages/
black src/ utils/ pages/

# 5. Commit suas alterações
git add .
git commit -m "feat: adiciona nova funcionalidade X"

# 6. Push para seu fork
git push origin feature/nova-funcionalidade

# 7. Abra Pull Request no GitHub
```

### 🧪 **Testes**

#### Estrutura de Testes
```
tests/
├── unit/                    # Testes unitários
│   ├── test_auth.py
│   ├── test_base.py
│   ├── test_validations.py
│   └── test_formatters.py
├── integration/             # Testes de integração
│   ├── test_google_sheets.py
│   ├── test_external_apis.py
│   └── test_workflows.py
├── e2e/                     # Testes end-to-end
│   ├── test_login_flow.py
│   ├── test_process_creation.py
│   └── test_report_generation.py
└── fixtures/                # Dados de teste
    ├── sample_data.json
    └── mock_responses.json
```

#### Executando Testes
```bash
# Todos os testes
pytest

# Testes específicos
pytest tests/unit/test_auth.py

# Com cobertura
pytest --cov=src --cov=utils --cov-report=html

# Testes de integração (requer configuração)
pytest tests/integration/ --integration
```

#### Exemplo de Teste
```python
# tests/unit/test_auth.py
import pytest
from utils.auth.auth import login, verify_password, hash_password

class TestAuth:
    def test_hash_password(self):
        """Testa geração de hash de senha"""
        password = "senha123"
        hashed = hash_password(password)
        
        assert hashed != password
        assert verify_password(password, hashed)
    
    def test_login_success(self, mock_secrets):
        """Testa login com credenciais válidas"""
        mock_secrets.return_value = {
            "passwords": {"user1": hash_password("senha123")},
            "permissions": {"user1": ["Base CPOF"]}
        }
        
        result = login("user1", "senha123")
        assert result is True
    
    def test_login_failure(self, mock_secrets):
        """Testa login com credenciais inválidas"""
        mock_secrets.return_value = {
            "passwords": {"user1": hash_password("senha123")}
        }
        
        result = login("user1", "senha_errada")
        assert result is False
```

### 📝 **Padrões de Código**

#### Convenções de Nomenclatura
```python
# Variáveis e funções: snake_case
def calcular_limite_credito():
    valor_total = 0
    
# Classes: PascalCase
class ProcessadorRelatorio:
    pass

```

#### Documentação de Funções
```python
def salvar_modificacao(usuario: str, processo_id: str, campo: str, 
                      valor_anterior: any, valor_novo: any) -> bool:
    """
    Registra modificação no histórico de auditoria.
    
    Args:
        usuario: Nome do usuário que fez a modificação
        processo_id: ID único do processo modificado
        campo: Nome do campo que foi alterado
        valor_anterior: Valor antes da modificação
        valor_novo: Novo valor após modificação
    
    Returns:
        bool: True se salvamento foi bem-sucedido, False caso contrário
    
    Raises:
        ValueError: Se processo_id não for encontrado
        ConnectionError: Se não conseguir conectar ao Google Sheets
    
    Example:
        >>> salvar_modificacao("admin", "2024.0001/2024", "valor", 1000, 1500)
        True
    """
    pass
```

#### Tratamento de Erros
```python
import logging
from typing import Optional

logger = logging.getLogger(__name__)

def funcao_com_tratamento_erro() -> Optional[dict]:
    """Exemplo de função com tratamento de erro adequado"""
    try:
        # Operação que pode falhar
        resultado = operacao_perigosa()
        return resultado
        
    except ConnectionError as e:
        logger.error(f"Erro de conexão: {e}")
        st.error("❌ Erro de conexão. Tente novamente.")
        return None
        
    except ValueError as e:
        logger.warning(f"Valor inválido: {e}")
        st.warning(f"⚠️ Dados inválidos: {e}")
        return None
        
    except Exception as e:
        logger.exception(f"Erro inesperado: {e}")
        st.error("❌ Erro interno. Contate o administrador.")
        return None
```

### 🔧 **Ferramentas de Desenvolvimento**

#### requirements-dev.txt
```txt
# Ferramentas de desenvolvimento
pytest>=7.0.0
pytest-cov>=4.0.0
black>=23.0.0
flake8>=6.0.0
isort>=5.0.0
mypy>=1.0.0
pre-commit>=3.0.0

# Documentação
sphinx>=6.0.0
sphinx-rtd-theme>=1.0.0

# Debugging
ipdb>=0.13.0
```

#### .pre-commit-config.yaml
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.1.0
    hooks:
      - id: black
        language_version: python3.9

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.0.0
    hooks:
      - id: mypy
```

### 📊 **Monitoramento e Logs**

#### Configuração de Logging
```python
import logging
import sys
from datetime import datetime

def setup_logging():
    """Configura sistema de logging"""
    
    # Formato dos logs
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Handler para arquivo
    file_handler = logging.FileHandler(
        f'logs/sigof_{datetime.now().strftime("%Y%m%d")}.log'
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    
    # Handler para console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.WARNING)
    
    # Logger principal
    logger = logging.getLogger('sigof')
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger
```

#### Métricas de Performance
```python
import time
import functools

def monitor_performance(func):
    """Decorator para monitorar performance de funções"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            logger.info(f"{func.__name__} executada em {execution_time:.2f}s")
            
            # Alertar se função demorar muito
            if execution_time > 5.0:
                logger.warning(f"{func.__name__} demorou {execution_time:.2f}s")
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"{func.__name__} falhou após {execution_time:.2f}s: {e}")
            raise
    
    return wrapper

# Uso
@monitor_performance
def funcao_lenta():
    time.sleep(2)
    return "resultado"
```

---

## 📄 Licença

```
MIT License

Copyright (c) 2024 Estado de Alagoas - SIGOF

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 📞 Contato

### 👥 **Desenvolvedor**

| Função | Nome | Email | GitHub |
|--------|------|-------|--------|
| **Developer** | Lucas Falcão | falcovisk@gmail.com | [@Falkzera](https://github.com/falkzera) |

### 🐛 **Reportar Bugs**

Para reportar bugs ou solicitar novas funcionalidades:

1. **Email**: falcovisk@gmail.com
2. **Telefone**: (82) 98713-0635

### 🌐 **Links Úteis**

- **Instagram**: [https://www.instagram.com/falkzera/](https://www.instagram.com/falkzera/)
- **linkedin**: [linkedin.com/in/falkzera/](linkedin.com/in/falkzera/)
- **e-mail**: [falcovisk@gmail.com](https://www.instagram.com/falkzera/)

---

<div align="center">

**SIGOF - Sistema de Gestão Orçamentário e Financeiro**

*Modernizando a gestão pública com tecnologia e transparência*

</div>
