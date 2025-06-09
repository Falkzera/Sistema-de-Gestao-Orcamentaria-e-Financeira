from siconfipy import get_fiscal
from datetime import datetime
import streamlit as st
from io import BytesIO
from src.google_drive_utils import update_base

ano_atual = datetime.now().year
ano_atual_lista = ano_atual + 1
ano_passado = ano_atual - 1
anos = list(range(2023, ano_atual_lista))

def funcao_rreo():
    st.write("Em construção...")