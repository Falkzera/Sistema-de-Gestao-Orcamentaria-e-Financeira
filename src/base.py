import streamlit as st

from streamlit_gsheets import GSheetsConnection

def func_load_base_cpof(forcar_recarregar=False):
    if "base" not in st.session_state or forcar_recarregar:
        conn = st.connection("gsheets", type=GSheetsConnection)
        base = conn.read(worksheet="Base CPOF", ttl=300)
        base["Fonte de Recursos"] = base["Fonte de Recursos"].astype(str)
        base["Grupo de Despesas"] = base["Grupo de Despesas"].astype(str)
        base["Nº do Processo"] = base["Nº do Processo"].astype(str).str.strip()
        base["Nº ATA"] = base["Nº ATA"].astype(str)
        base["Nº ATA"] = base["Nº ATA"].str.replace('0.', '', regex=False)
        base["Nº ATA"] = base["Nº ATA"].str.replace('Sem Informação', '', regex=False)
        base["Nº ATA"] = base["Nº ATA"].str.replace('nan', '', regex=False)

        st.session_state.base_cpof = base

    return st.session_state.base_cpof

def func_load_historico_cpof(forcar_recarregar=False):
    if "historico" not in st.session_state or forcar_recarregar:
        conn = st.connection("gsheets", type=GSheetsConnection)
        base = conn.read(worksheet="Histórico CPOF", ttl=300)
        st.session_state.historico_cpof = base
    
    return st.session_state.historico_cpof

def func_load_base_credito_sop_geo(forcar_recarregar=False):
    if "base" not in st.session_state or forcar_recarregar:
        conn = st.connection("gsheets", type=GSheetsConnection)
        base = conn.read(worksheet="Base Crédito SOP/GEO", ttl=300)
        base["Fonte de Recursos"] = base["Fonte de Recursos"].astype(str)
        base["Grupo de Despesas"] = base["Grupo de Despesas"].astype(str)
        base["Nº do decreto"] = base["Nº do decreto"].astype(str)
        base["Nº do Processo"] = base["Nº do Processo"].astype(str).str.strip()
        base["Nº do decreto"] = base["Nº do decreto"].str.replace('.0', '', regex=False)
        base["Nº do decreto"] = base["Nº do decreto"].str.replace('nan', '', regex=False)
        base["Nº do decreto"] = base["Nº do decreto"].fillna('')
        base["Nº ATA"] = base["Nº ATA"].astype(str)
        base["Nº ATA"] = base["Nº ATA"].str.replace('0.', '', regex=False)
        base["Nº ATA"] = base["Nº ATA"].str.replace('nan', '', regex=False)
        # converter em datetime
        base = base[['Situação', 'Nº do Processo', 'Origem de Recursos', 'Órgão (UO)', 'Fonte de Recursos', 'Grupo de Despesas',  'Tipo de Crédito', 'Valor', 'Objetivo', 'Observação', 'Opnião SOP', 'Data de Recebimento',	'Data de Publicação', 'Nº do decreto', 'Nº ATA','Contabilizar no Limite?', 'Cadastrado Por',	'Última Edição']]
        st.session_state.base_creditos_sop_geo = base

    return st.session_state.base_creditos_sop_geo

def func_load_historico_credito_sop_geo(forcar_recarregar=False):
    if "historico" not in st.session_state or forcar_recarregar:
        conn = st.connection("gsheets", type=GSheetsConnection)
        base = conn.read(worksheet="Histórico Crédito SOP/GEO", ttl=300)
        st.session_state.historico_credito_sop_geo = base

    return st.session_state.historico_credito_sop_geo