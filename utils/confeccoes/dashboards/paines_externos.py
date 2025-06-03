import streamlit as st
import streamlit.components.v1 as components



def observatorio_orcamento():

    # link_bi = "https://app.powerbi.com/view?r=eyJrIjoiZTQwNWUwMWEtNmYyYy00NGFlLThiYWEtY2JiYmYwOTIyMWNiIiwidCI6IjQ0OTlmNGZmLTI0YTYtNGI0Mi1iN2VmLTEyNGFmY2FkYzkxMyJ9"
    link_bi = "https://app.powerbi.com/view?r=eyJrIjoiZTkyNzU5NGMtOWUwOS00NTZiLWIzYTAtODVkYzY0YjliNDE1IiwidCI6ImNlMTdiNDVkLThmYjctNGYwMy05ZjRlLTYxMTBkMTAzZGI3NiJ9"
    components.html(
        f"""
        <iframe width="100%" height="800" src="{link_bi}" frameborder="0" allowFullScreen="false"></iframe>
        """,
        height=800,
    )