import io
import streamlit as st
from datetime import datetime, timedelta

from src.coleta_de_dados.ibge_abate_animais import funcao_ibge_abate_animais
from src.coleta_de_dados.ibge_leite_industrializado import funcao_ibge_leite_industrializado
from src.coleta_de_dados.mdic_comercio_exterior import funcao_mdic_comercio_exterior
from src.coleta_de_dados.anp_preco_combustivel import funcao_anp_preco_combustivel
from src.coleta_de_dados.anp_producao_combustivel import funcao_anp_producao_combustivel
from src.coleta_de_dados.sefaz_dotacao_completo import funcao_sefaz_dotacao
from src.coleta_de_dados.sefaz_despesa_completo import funcao_sefaz_despesa_completo
from src.coleta_de_dados.sefaz_despesa_ano_corrente import funcao_sefaz_despesa_ano_corrente
from src.coleta_de_dados.sefaz_dotacao_ano_corrente import funcao_sefaz_dotacao_ano_corrente
from src.coleta_de_dados.rgf import funcao_rgf

from src.google_drive_utils import read_pickle_file_from_drive, save_pickle_file_to_drive
from src.google_drive_utils import read_parquet_file_from_drive



bases = [
    {
        "id": "dotacao_ano_corrente",
        "nome": "Dotação Orçamentária",
        "arquivo": "sefaz_dotacao_ano_corrente.parquet",
        "descricao": "Informações sobre a dotação orçamentária do exercício corrente.",
        "tags": ["Orçamento", "Siafe", "Exercício Corrente", "Alagoas"],
        "icone": "💰",
        "tamanho": "12.5 MB"
    },
    {
        "id": "despesas_ano_corrente",
        "nome": "Despesas Orçamentárias",
        "arquivo": "sefaz_despesa_ano_corrente.parquet",
        "descricao": "Despesas detalhadas do exercício corrente com classificação por categoria.",
        "tags": ["Orçamento", "Siafe", "Exercício Corrente", "Alagoas"],
        "icone": "📊",
        "tamanho": "6.8 MB"
    },
    {
        "id": "leite",
        "nome": "Leite Industrializado",
        "arquivo": "ibge_leite_industrializado.parquet",
        "descricao": "Produção de leite industrializado para todas Unidades Federativas segundo dados do IBGE.",
        "tags": ["IBGE", "Agro", "Série Histórica", "Brasil"],
        "icone": "🥛",
        "tamanho": "23.8 KB"
    },
    {
        "id": "abate",
        "nome": "Abate de Animais",
        "arquivo": "ibge_abate_animais.parquet",
        "descricao": "Estatísticas de abate de animais para todas Unidades Federativas segundo dados do IBGE.",
        "tags": ["IBGE", "Agro", "Série Histórica", "Brasil"],
        "icone": "🐄",
        "tamanho": "23.9 KB"
    },
    {
        "id": "comercio",
        "nome": "Comércio Exterior",
        "arquivo": "mdic_comercio_exterior.parquet",
        "descricao": "Dados da balança comercial de Alagoas segundo o Ministério do Desenvolvimento (MDIC).",
        "tags": ["MDIC", "Exterior", "Série Histórica", "Alagoas"],
        "icone": "🌍",
        "tamanho": "4.6 MB"
    },
    {
        "id": "etanol",
        "nome": "Produção de Etanol",
        "arquivo": "anp_etanol.parquet",
        "descricao": "Dados de produção de etanol segundo a Agência Nacional de Petróleo e Gás Natural (ANP).",
        "tags": ["ANP", "Combustíveis", "Série Histórica", "Brasil"],
        "icone": "⛽",
        "tamanho": "229 KB"
    },
    {
        "id": "gn",
        "nome": "Gás Natural",
        "arquivo": "anp_gn.parquet",
        "descricao": "Dados de produção de gás natural segundo a Agência Nacional de Petróleo e Gás Natural (ANP).",
        "tags": ["ANP", "Combustíveis", "Série Histórica", "Brasil"],
        "icone": "🔥",
        "tamanho": "222 KB"
    },
    {
        "id": "lgn",
        "nome": "Gás Liquefeito Natural",
        "arquivo": "anp_lgn.parquet",
        "descricao": "Dados de produção de GLN segundo a Agência Nacional de Petróleo e Gás Natural (ANP).",
        "tags": ["ANP", "Combustíveis", "Série Histórica", "Brasil"],
        "icone": "🛢️",
        "tamanho": "94.8 KB"
    },
    {
        "id": "petroleo",
        "nome": "Petróleo",
        "arquivo": "anp_petroleo.parquet",
        "descricao": "Dados de produção de Petróleo segundo a Agência Nacional de Petróleo e Gás Natural (ANP).",
        "tags": ["ANP", "Combustíveis", "Série Histórica", "Brasil"],
        "icone": "🛢️",
        "tamanho": "228 KB"
    },
    {
        "id": "preco_combustivel",
        "nome": "Preço de Combustíveis",
        "arquivo": "anp_preco_combustivel.parquet",
        "descricao": "Preços de combustíveis segundo a Agência Nacional de Petróleo e Gás Natural (ANP).",
        "tags": ["ANP", "Combustíveis", "Série Histórica", "Alagoas"],
        "icone": "⛽",
        "tamanho": "8.2 MB"
    },
    {
        "id": "rgf_completo",
        "nome": "RGF Completo",
        "arquivo": "RGF.parquet",
        "descricao": "Relatório de Gestão Fiscal Completo e atualizado com diversos indicadores.",
        "tags": ["Fiscal", "RGF", "Série Histórica", "Alagoas"],
        "icone": "📋",
        "tamanho": "468 KB"
    },
    {
        "id": "divida_consolidada",
        "nome": "Dívida sobre RCL",
        "arquivo": "DIVIDA_CONSOLIDADA_SOBRE_RCL.parquet",
        "descricao": "Indicador de dívida consolidada em relação à Receita Corrente Líquida.",
        "tags": ["Fiscal", "RGF", "Série Histórica", "Alagoas"],
        "icone": "📉",
        "tamanho": "5.3 KB"
    },
    {
        "id": "divida_liquida",
        "nome": "Dívida Líquida sobre RCL",
        "arquivo": "DIVIDIDA_CONSOLIDADA_LIQUIDA_SOBRE_RCL.parquet",
        "descricao": "Dívida consolidada líquida em relação à Receita Corrente Líquida.",
        "tags": ["Fiscal", "RGF", "Série Histórica", "Alagoas"],
        "icone": "📉",
        "tamanho": "5.3 KB"
    },
    {
        "id": "despesa_pessoal",
        "nome": "Despesa com Pessoal / RCL",
        "arquivo": "DESPESA_COM_PESSOAL_SOBRE_RCL_AJUSTADA.parquet",
        "descricao": "Despesa com pessoal em relação à Receita Corrente Líquida ajustada.",
        "tags": ["Fiscal", "RGF", "Série Histórica", "Alagoas"],
        "icone": "👥",
        "tamanho": "5.3 KB"
    },
    {
        "id": "itcmd",
        "nome": "ITCMD",
        "arquivo": "sefaz_itcmd_completo.parquet",
        "descricao": "Informações completas da arrecadação sobre o ITCMD de Alagoas.",
        "tags": ["Imposto", "Fiscal", "Série Histórica", "Alagoas"],
        "icone": "💵",
        "tamanho": "15.3 KB"
    },
    {
        "id": "icms",
        "nome": "ICMS",
        "arquivo": "sefaz_icms_completo.parquet",
        "descricao": "Informações completas da arrecadação sobre o ICMS de Alagoas.",
        "tags": ["Imposto", "Fiscal", "Série Histórica", "Alagoas"],
        "icone": "💵",
        "tamanho": "17.3 KB"
    },
    {
        "id": "ipva",
        "nome": "IPVA",
        "arquivo": "sefaz_ipva_completo.parquet",
        "descricao": "Informações completas da arrecadação sobre o IPVA de Alagoas.",
        "tags": ["Imposto", "Sefaz", "Série Histórica", "Alagoas"],
        "icone": "🚗",
        "tamanho": "13.9 KB"
    }
]



@st.cache_data
def convert_to_excel(df):
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False, engine='openpyxl')
    return buffer.getvalue()

CACHE_PATH = "repositorio_cache.pkl"

try:
    BASE_UPDATE_CONFIG = {
        "abate": (funcao_ibge_abate_animais, 12), # ok
        "leite": (funcao_ibge_leite_industrializado, 12), # ok
        "comercio": (funcao_mdic_comercio_exterior, 24), # ok
        "preco_combustivel": (funcao_anp_preco_combustivel, 24), # ok
        "etanol": (funcao_anp_producao_combustivel, 24), # ok
        "gn": (funcao_anp_producao_combustivel, 24), # ok
        "lgn": (funcao_anp_producao_combustivel, 24), # ok
        "petroleo": (funcao_anp_producao_combustivel, 24), # ok
        "rgf_completo": (funcao_rgf, 24), # ok
        "dotacao_ano_corrente": (funcao_sefaz_dotacao_ano_corrente, 6), # ok
        "despesas_ano_corrente": (funcao_sefaz_despesa_ano_corrente, 6), # ok
        "divida_consolidada": (funcao_rgf, 24), # ok
        "divida_liquida": (funcao_rgf, 24), # ok
        "despesa_pessoal": (funcao_rgf, 24), # ok
        "itcmd": (funcao_rgf, 24), # não ok
        "icms": (funcao_rgf, 24), # não ok
        "ipva": (funcao_rgf, 24), # não ok

        # Adição de outras bases AQUI.
    }
except Exception as e:
    print(f"Não foi possível ATUALIZAR a BASE selecionada, MOTIVO: {str(e)}")
    BASE_UPDATE_CONFIG = {}

def load_cache():
    try:
        cache = read_pickle_file_from_drive(CACHE_PATH)
        return cache if cache else {}
    except Exception:
        return {}

def save_cache(cache):
    save_pickle_file_to_drive(CACHE_PATH, cache)

def should_update(base_id):
    cache = load_cache()
    now = datetime.now()
    config = BASE_UPDATE_CONFIG.get(base_id)
    if config is None:
        return False
    _, interval = config
    last_update = cache.get(base_id)
    if not last_update:
        return True
    last_update_dt = datetime.fromisoformat(last_update)
    return now - last_update_dt > timedelta(hours=interval)

def update_base_if_needed(base_id):
    config = BASE_UPDATE_CONFIG.get(base_id)
    if config is None:
        return
    func, _ = config
    if should_update(base_id):
        func()
        cache = load_cache()
        cache[base_id] = datetime.now().isoformat()
        save_cache(cache)

def processar_download(nome_base):
    try:
        usuario = st.session_state.get("username", "")
        is_admin = usuario.lower() in ("sudo", "admin")
        base_id = next((b["id"] for b in bases if b["arquivo"] == nome_base), None)
        if is_admin and base_id:
            try:
                update_base_if_needed(base_id)
            except Exception as e:
                print(f"Falha ao atualizar base {base_id}: {str(e)}")
        progress_bar = st.progress(0)
        status_text = st.empty()
        progress_bar.progress(25)
        df = read_parquet_file_from_drive(nome_base)
        progress_bar.progress(75)
        excel_data = convert_to_excel(df)
        progress_bar.progress(100)
        import time
        time.sleep(1)
        progress_bar.empty()
        status_text.empty()
        return excel_data, df.shape
    except Exception as e:
        print(f"Base NÃO baixada {nome_base}, MOTIVO: {str(e)}")
        return None, None