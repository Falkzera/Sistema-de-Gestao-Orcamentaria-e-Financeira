import json
import os
import io

import gspread
import tempfile

import pandas as pd
import streamlit as st

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload

def authenticate_service_account():
    """
    Autentica no Google Drive usando credenciais do secrets.toml (Streamlit).
    """
    SCOPES = ['https://www.googleapis.com/auth/drive']
    credentials_info = json.loads(st.secrets["GOOGLE_CREDENTIALS"])
    credentials = Credentials.from_service_account_info(credentials_info, scopes=SCOPES)
    return build('drive', 'v3', credentials=credentials)

def list_files_in_folder(service, folder_id):
    """
    Lista arquivos de uma pasta no Google Drive.
    """
    query = f"'{folder_id}' in parents and trashed = false"
    results = service.files().list(q=query, fields="files(id, name, modifiedTime)").execute()
    return results.get('files', [])

def download_file(service, file_id):
    """
    Faz o download de um arquivo do Google Drive para um objeto em memória.
    """
    request = service.files().get_media(fileId=file_id)
    file_data = io.BytesIO()
    downloader = MediaIoBaseDownload(file_data, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
    file_data.seek(0)
    return file_data

def upload_file_to_drive(service, file_buffer, file_name, folder_id):
    """
    Faz o upload de um arquivo em memória para o Google Drive.
    """
    # Cria um arquivo temporário no sistema de arquivos
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file_path = tmp_file.name
        # Escreve os dados do buffer (BytesIO) no arquivo temporário
        tmp_file.write(file_buffer.getvalue())

    # Cria o MediaFileUpload usando o caminho do arquivo temporário
    media = MediaFileUpload(tmp_file_path, resumable=True)

    # Define os metadados do arquivo
    file_metadata = {
        'name': file_name,
        'parents': [folder_id]
    }

    # Faz o upload do arquivo
    file = service.files().create(
        media_body=media,
        body=file_metadata
    ).execute()

    # Exclui o arquivo temporário após o upload
    os.remove(tmp_file_path)

    return file['id']

def create_folder_in_drive(service, folder_name, parent_folder_id):
    """
    Cria uma pasta no Google Drive. Se já existir, retorna o ID da pasta.
    """
    query = f"'{parent_folder_id}' in parents and name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    items = results.get('files', [])
    if items:
        return items[0]['id']
    else:
        folder_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [parent_folder_id]
        }
        folder = service.files().create(body=folder_metadata, fields='id').execute()
        return folder.get('id')

def remove_duplicate_files_in_subfolders(service, folder_id):
    """
    Remove arquivos duplicados (.parquet) dentro de uma pasta e suas subpastas no Google Drive.
    Mantém apenas o arquivo mais recente baseado no `modifiedTime`.
    """
    def list_files_and_folders(folder_id):
        """
        Lista arquivos e subpastas dentro de uma pasta no Google Drive.
        """
        query = f"'{folder_id}' in parents and trashed = false"
        results = service.files().list(q=query, fields="files(id, name, mimeType, modifiedTime)").execute()
        return results.get('files', [])

    def process_folder(folder_id):
        """
        Processa uma pasta para verificar duplicatas de arquivos .parquet e as remove.
        """
        items = list_files_and_folders(folder_id)
        parquet_files = [item for item in items if item['name'].endswith('.parquet')]

        files_by_name = {}
        for file in parquet_files:
            name = file['name']
            if name not in files_by_name:
                files_by_name[name] = []
            files_by_name[name].append(file)

        for name, file_list in files_by_name.items():
            if len(file_list) > 1:
                file_list.sort(key=lambda x: x['modifiedTime'], reverse=True) 
                for file in file_list[1:]:
                    service.files().delete(fileId=file['id']).execute()
                    print(f"Excluído: {file['name']} (ID: {file['id']})")

        subfolders = [item for item in items if item['mimeType'] == 'application/vnd.google-apps.folder']
        for subfolder in subfolders:
            process_folder(subfolder['id'])

    # Iniciar o processamento da pasta principal
    process_folder(folder_id)

def list_files_in_drive(service, folder_id, file_name):
    """
    Lista arquivos na pasta do Google Drive e filtra por nome de arquivo.
    """
    query = f"'{folder_id}' in parents and trashed = false and name = '{file_name}'"
    results = service.files().list(q=query, fields="files(id, name, mimeType)").execute()
    return results.get('files', [])

def read_parquet_file_from_drive(file_name):
    """
    Lê um arquivo `.parquet` de uma pasta específica no Google Drive a partir de seu nome
    e retorna um DataFrame.
    """
    # Autentica no Google Drive
    service = authenticate_service_account()
    folder_id = st.secrets["pasta_bases"]["FOLDER_ID"]  # ID da pasta de destino no Google Drive
    
    # Buscar o arquivo Parquet pelo nome
    files = list_files_in_drive(service, folder_id, file_name)
    
    if not files:
        print(f"Arquivo {file_name} não encontrado na pasta.")
        return pd.DataFrame()  # Retorna um DataFrame vazio se o arquivo não for encontrado

    # Assumimos que existe apenas um arquivo com o nome especificado na pasta
    file = files[0]

    # Baixar o arquivo Parquet
    request = service.files().get_media(fileId=file['id'])
    file_data = io.BytesIO()
    downloader = MediaIoBaseDownload(file_data, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
    
    file_data.seek(0)  # Volta o ponteiro do arquivo para o início

    # Ler o arquivo Parquet e retornar o DataFrame
    return pd.read_parquet(file_data)

def read_geojson_file_from_drive(file_name):
    """
    Lê um arquivo `.geojson` de uma pasta específica no Google Drive a partir de seu nome
    e retorna o caminho local do arquivo baixado.
    """
    # Autentica no Google Drive
    service = authenticate_service_account()
    folder_id = st.secrets["pasta_bases"]["FOLDER_ID"]  # ID da pasta de destino no Google Drive
    
    # Buscar o arquivo GeoJSON pelo nome
    files = list_files_in_drive(service, folder_id, file_name)
    
    if not files:
        print(f"Arquivo {file_name} não encontrado na pasta.")
        return None  # Retorna None se o arquivo não for encontrado

    # Assumimos que existe apenas um arquivo com o nome especificado na pasta
    file = files[0]

    # Baixar o arquivo GeoJSON
    request = service.files().get_media(fileId=file['id'])
    file_data = io.BytesIO()
    downloader = MediaIoBaseDownload(file_data, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
    
    file_data.seek(0)  # Volta o ponteiro do arquivo para o início

    # Salvar o conteúdo baixado em um arquivo local temporário
    local_file_path = f'/tmp/{file_name}'
    with open(local_file_path, 'wb') as f:
        f.write(file_data.read())

    # Retorna o caminho do arquivo local
    return local_file_path

def download_file_by_name(service, folder_id, file_name):
    """
    Busca e baixa um arquivo específico pelo nome dentro de uma pasta no Google Drive.

    Args:
        service: Serviço autenticado da API do Google Drive.
        folder_id: ID da pasta no Google Drive onde o arquivo está localizado.
        file_name: Nome do arquivo a ser buscado.

    Returns:
        Objeto de arquivo em memória (BytesIO) ou None se o arquivo não for encontrado.
    """
    # Listar arquivos na pasta
    files = list_files_in_folder(service, folder_id)
    
    # Filtrar pelo nome do arquivo
    matching_files = [file for file in files if file['name'] == file_name]
    
    if not matching_files:
        st.error(f"Arquivo '{file_name}' não encontrado na pasta.")
        return None
    
    file_id = matching_files[0]['id']
    
    # Fazer o download do arquivo
    file_data = download_file(service, file_id)
    return file_data

def delete_old_file(service, folder_id, file_name):
    query = f"'{folder_id}' in parents and name = '{file_name}' and trashed = false"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get('files', [])
    for file in files:
        service.files().delete(fileId=file['id']).execute()

def remove_duplicate_files(service, folder_id):
    """
    Remove arquivos duplicados dentro de uma pasta no Google Drive.
    Mantém apenas o arquivo mais recente baseado no `modifiedTime`.
    """
    # Listar arquivos na pasta
    query = f"'{folder_id}' in parents and trashed = false"
    results = service.files().list(q=query, fields="files(id, name, modifiedTime)").execute()
    files = results.get('files', [])

    files_by_name = {}
    for file in files:
        name = file['name']
        if name not in files_by_name:
            files_by_name[name] = []
        files_by_name[name].append(file)
    for name, file_list in files_by_name.items():
        if len(file_list) > 1:
            file_list.sort(key=lambda x: x['modifiedTime'], reverse=True)
            for file in file_list[1:]:
                service.files().delete(fileId=file['id']).execute()

def authenticate_google_sheets_from_secrets():
    """
    Autentica no Google Sheets usando credenciais de serviço do secrets.toml (Streamlit).
    """
    SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    credentials_info = json.loads(st.secrets["GOOGLE_CREDENTIALS"])
    credentials = Credentials.from_service_account_info(credentials_info, scopes=SCOPES)
    client = gspread.authorize(credentials)
    return client

def update_base(file_buffer, nome_arquivo):
    folder_id = st.secrets["pasta_bases"]["FOLDER_ID"]  # ID da pasta de destino no Google Drive
    file_name = nome_arquivo  # Nome do arquivo Parquet

    # Autentica no Google Drive
    service = authenticate_service_account()

    # Função para listar arquivos dentro de uma pasta no Google Drive
    def list_files_in_drive(folder_id, file_name):
        query = f"'{folder_id}' in parents and trashed = false and name = '{file_name}'"
        results = service.files().list(q=query, fields="files(id, name)").execute()
        return results.get('files', [])

    # Verifica se já existe um arquivo com o mesmo nome
    existing_files = list_files_in_drive(folder_id, file_name)

    # Se o arquivo já existir, exclui o arquivo antigo
    if existing_files:
        for file in existing_files:
            service.files().delete(fileId=file['id']).execute()
            print(f"Arquivo antigo {file_name} excluído do Google Drive.")

    # Faz o upload do arquivo mais recente diretamente do buffer de memória
    file_id = upload_file_to_drive(service, file_buffer, file_name, folder_id)
    
    print(f'Arquivo {file_name} enviado com sucesso para o Google Drive!')

def read_pickle_file_from_drive(file_name):
    """
    Lê um arquivo .pkl (pickle) do Google Drive e retorna o objeto carregado.
    """
    import pickle
    # Autentica no Google Drive
    service = authenticate_service_account()
    folder_id = st.secrets["pasta_bases"]["FOLDER_ID"]

    # Buscar o arquivo pelo nome
    files = list_files_in_drive(service, folder_id, file_name)
    if not files:
        print(f"Arquivo pickle '{file_name}' não encontrado na pasta do Drive.")
        return None

    file = files[0]
    file_data = download_file(service, file['id'])
    file_data.seek(0)
    return pickle.load(file_data)

def save_pickle_file_to_drive(file_name, obj):
    """
    Salva um objeto Python como arquivo .pkl (pickle) no Google Drive.
    Se já existir, substitui o arquivo.
    """
    import pickle
    # Serializa o objeto para um buffer em memória
    buffer = io.BytesIO()
    pickle.dump(obj, buffer)
    buffer.seek(0)

    # Autentica no Google Drive
    service = authenticate_service_account()
    folder_id = st.secrets["pasta_bases"]["FOLDER_ID"]

    # Remove arquivo antigo se existir
    existing_files = list_files_in_drive(service, folder_id, file_name)
    for file in existing_files:
        service.files().delete(fileId=file['id']).execute()

    # Faz upload do novo arquivo
    upload_file_to_drive(service, buffer, file_name, folder_id)