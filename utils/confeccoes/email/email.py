import smtplib
import streamlit as st
import pandas as pd
from datetime import datetime
from src.google_drive_utils import save_pickle_file_to_drive, read_pickle_file_from_drive
from src.base import func_load_base_ted
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

EMAIL_CACHE_FILENAME = "cache_email_ted.pkl"

def ja_enviou_email_hoje(cache):
    hoje = datetime.now().date().isoformat()
    return cache.get("ultimo_envio_ted") == hoje

def marcar_email_enviado_hoje(cache):
    hoje = datetime.now().date().isoformat()
    cache["ultimo_envio_ted"] = hoje
    save_pickle_file_to_drive(EMAIL_CACHE_FILENAME, cache)

def criar_html_ted_vencimentos(df):
    """
    Gera HTML apenas com processos que possuem Data de Encerramento,
    mostrando Nº do Processo, Objetivo, Data de Encerramento e Dias Restantes,
    ordenados do que está mais próximo de vencer para o mais distante.
    """
    # Filtrar apenas linhas com Data de Encerramento não nula
    df_venc = df[df["Data de Encerramento"].notnull()].copy()
    if df_venc.empty:
        return """
        <html>
        <body>
            <h2>⏰ Processos TED - Prazos de Encerramento</h2>
            <p>Não há processos TED com data de encerramento definida.</p>
        </body>
        </html>
        """

    df_venc["Data de Encerramento"] = pd.to_datetime(df_venc["Data de Encerramento"], dayfirst=False, errors="coerce")
    hoje = datetime.now().date()

    if pd.api.types.is_datetime64_any_dtype(df_venc["Data de Encerramento"]):
        df_venc["Dias Restantes"] = (df_venc["Data de Encerramento"].dt.date - hoje).apply(lambda x: x.days)
    else:
        df_venc["Dias Restantes"] = None

    df_venc = df_venc[df_venc["Dias Restantes"].notnull() & (df_venc["Dias Restantes"] >= 0)]

    if df_venc.empty:
        return """
        <html>
        <body>
            <h2>⏰ Processos TED - Prazos de Encerramento</h2>
            <p>Não há processos TED com prazos futuros para acompanhar.</p>
        </body>
        </html>
        """

    df_venc = df_venc.sort_values("Dias Restantes")
    df_venc["Data de Encerramento"] = df_venc["Data de Encerramento"].dt.strftime('%d/%m/%Y')
    df_email = df_venc[["Nº do Processo", "UO Concedente", "UO Executante", "Objetivo", "Data de Encerramento", "Dias Restantes"]].copy()

    def adicionar_alerta(dias):
        if dias <= 3:
            return f"🔴 {dias} dias"
        elif dias <= 7:
            return f"🟡 {dias} dias"
        else:
            return f"🟢 {dias} dias"
    
    df_email["Status"] = df_email["Dias Restantes"].apply(adicionar_alerta)
    df_email = df_email.drop("Dias Restantes", axis=1)

    total_criticos = len(df_venc[df_venc["Dias Restantes"] <= 3])
    total_atenção = len(df_venc[(df_venc["Dias Restantes"] > 3) & (df_venc["Dias Restantes"] <= 7)])
    total_normais = len(df_venc[df_venc["Dias Restantes"] > 7])

    html = f"""
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 20px;
            }}
            table {{
                border-collapse: collapse;
                width: 100%;
                margin-top: 20px;
            }}
            th, td {{
                border: 1px solid #ddd;
                padding: 12px;
                text-align: left;
            }}
            th {{
                background-color: #f2f2f2;
                font-weight: bold;
            }}
            tr:nth-child(even) {{
                background-color: #f9f9f9;
            }}
            .header {{
                color: #333;
                margin-bottom: 10px;
            }}
            .summary {{
                background-color: #e8f4fd;
                padding: 15px;
                border-radius: 5px;
                margin-bottom: 20px;
            }}
            .critical {{ color: #d32f2f; }}
            .warning {{ color: #f57c00; }}
            .normal {{ color: #388e3c; }}
        </style>
    </head>
    <body>
        <h2 class="header">⏰ Processos TED - Prazos de Encerramento</h2>
        <p class="header">Data do relatório: {hoje.strftime('%d/%m/%Y')}</p>
        
        <div class="summary">
            <h3>📊 Resumo dos Prazos:</h3>
            <p><span class="critical">🔴 Críticos (≤ 3 dias): {total_criticos} processos</span></p>
            <p><span class="warning">🟡 Atenção (4-7 dias): {total_atenção} processos</span></p>
            <p><span class="normal">🟢 Normais (> 7 dias): {total_normais} processos</span></p>
            <p><strong>Total: {len(df_email)} processos</strong></p>
        </div>
        
        {df_email.to_html(index=False, escape=False)}
        
        <p><em>* Ordenado do vencimento mais próximo para o mais distante.</em></p>
        <p><em>* 🔴 = Crítico (≤ 3 dias) | 🟡 = Atenção (4-7 dias) | 🟢 = Normal (> 7 dias)</em></p>
    </body>
    </html>
    """
    return html

def enviar_email_ted(df):
    """Envia email com os processos TED próximos do vencimento"""
    try:
        smtp_server = st.secrets["EMAIL"]["SMTP_SERVER"]
        smtp_port = int(st.secrets["EMAIL"]["SMTP_PORT"])
        email_sender = st.secrets["EMAIL"]["EMAIL_SENDER"]
        email_password = st.secrets["EMAIL"]["EMAIL_PASSWORD"]
        # Destinatários agora vêm do secrets.toml
        destinatarios = st.secrets["EMAIL"].get("DESTINATARIOS", "").split(",")
        destinatarios = [d.strip() for d in destinatarios if d.strip()]

        html_content = criar_html_ted_vencimentos(df)
        if "Não há processos TED" in html_content:
            return False, "Nenhum processo TED com data de encerramento para enviar."

        msg = MIMEMultipart('alternative')
        msg['From'] = email_sender
        msg['To'] = ", ".join(destinatarios)
        msg['Subject'] = f"⏰ Prazos de Encerramento - Processos TED ({datetime.now().strftime('%d/%m/%Y')})"
        html_part = MIMEText(html_content, 'html', 'utf-8')
        msg.attach(html_part)

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(email_sender, email_password)
        for destinatario in destinatarios:
            server.sendmail(email_sender, destinatario, msg.as_string())
        server.quit()
        return True, f"✅ Email enviado para {len(destinatarios)} destinatário(s)"
    except Exception as e:
        return False, f"❌ Erro ao enviar email: {str(e)}"

def rotina_envio_email_ted():
    try:
        try:
            cache = read_pickle_file_from_drive(EMAIL_CACHE_FILENAME)
            if cache is None:
                cache = {}
        except Exception as e:
            print(f"Erro ao ler cache: {e}")
            cache = {}

        if ja_enviou_email_hoje(cache):
            return

        try:
            df = func_load_base_ted(forcar_recarregar=True)
            sucesso, msg = enviar_email_ted(df)
            if sucesso:
                marcar_email_enviado_hoje(cache)
            else:
                print(f"Erro ao enviar email: {msg}")
        except Exception as e:
            print(f"Erro ao carregar base ou enviar email: {e}")

    except Exception as e:
        print(f"Erro geral na rotina de envio de email: {e}")