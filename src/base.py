import pandas as pd
import streamlit as st
from streamlit_gsheets import GSheetsConnection

def tratar_data(coluna):
    try:
        # Converte como número de dias desde 1900 (formato Excel)
        datas = pd.to_datetime(coluna.astype(float) - 2, origin='1900-01-01', unit='D')
    except Exception:
        # Se falhar, tenta como string no formato dd/mm/yyyy
        datas = pd.to_datetime(coluna, format='%d/%m/%Y', errors='coerce')
    return datas.dt.strftime('%d/%m/%Y')

def func_load_base_cpof(forcar_recarregar=False):
    if "base" not in st.session_state or forcar_recarregar:
        with st.spinner("🔄 Carregando base de dados..."):
            conn = st.connection("gsheets", type=GSheetsConnection)
            base = conn.read(worksheet="Base CPOF", ttl=0)
            base["Fonte de Recursos"] = base["Fonte de Recursos"].astype(str)
            base["Grupo de Despesas"] = base["Grupo de Despesas"].astype(str)
            base["ATA"] = base["ATA"].astype(str)
            base["Nº do Processo"] = base["Nº do Processo"].astype(str).str.strip()
            # base['Data de Recebimento'] = tratar_data(base['Data de Recebimento'])
            # base['Data de Publicação'] = tratar_data(base['Data de Publicação'])
            st.session_state.base_cpof = base

    return st.session_state.base_cpof


def func_load_historico_cpof(forcar_recarregar=False):
    if "historico" not in st.session_state or forcar_recarregar:
        with st.spinner("🔄 Carregando histórico..."):
            conn = st.connection("gsheets", type=GSheetsConnection)
            base = conn.read(worksheet="Histórico CPOF", ttl=0)
            st.session_state.historico_cpof = base
    
    return st.session_state.historico_cpof

def func_load_base_credito_sop_geo(forcar_recarregar=False):
    if "base" not in st.session_state or forcar_recarregar:
        with st.spinner("🔄 Carregando base de dados..."):
            conn = st.connection("gsheets", type=GSheetsConnection)
            base = conn.read(worksheet="Base Crédito SOP/GEO", ttl=0)
            base["Fonte de Recursos"] = base["Fonte de Recursos"].astype(str)
            base["Grupo de Despesas"] = base["Grupo de Despesas"].astype(str)
            base["Nº do Processo"] = base["Nº do Processo"].astype(str).str.strip()
            st.session_state.base_creditos_sop_geo = base

    return st.session_state.base_creditos_sop_geo


def func_load_historico_credito_sop_geo(forcar_recarregar=False):
    if "historico" not in st.session_state or forcar_recarregar:
        with st.spinner("🔄 Carregando histórico..."):
            conn = st.connection("gsheets", type=GSheetsConnection)
            base = conn.read(worksheet="Histórico Crédito SOP/GEO", ttl=0)
            st.session_state.historico_credito_sop_geo = base

    return st.session_state.historico_credito_sop_geo


                