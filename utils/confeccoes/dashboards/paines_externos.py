import streamlit.components.v1 as components

def observatorio_orcamento():

    link_bi = "https://app.powerbi.com/view?r=eyJrIjoiZTkyNzU5NGMtOWUwOS00NTZiLWIzYTAtODVkYzY0YjliNDE1IiwidCI6ImNlMTdiNDVkLThmYjctNGYwMy05ZjRlLTYxMTBkMTAzZGI3NiJ9"
    components.html(
        f"""
        <iframe width="100%" height="800" src="{link_bi}" frameborder="0" allowFullScreen="false"></iframe>
        """,
        height=800,
    )

def preco_combustivel(): # não utilizado no momento

    link_bi = "https://app.powerbi.com/view?r=eyJrIjoiMGM0NDhhMTUtMjQwZi00N2RlLTk1M2UtYjkxZTlkNzM1YzE5IiwidCI6IjQ0OTlmNGZmLTI0YTYtNGI0Mi1iN2VmLTEyNGFmY2FkYzkxMyJ9"
    components.html(
        f"""
        <iframe width="100%" height="800" src="{link_bi}" frameborder="0" allowFullScreen="false"></iframe>
        """,
        height=800,
    )



    