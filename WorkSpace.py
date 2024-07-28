import streamlit as st
import subprocess

# Install the ODBC driver for SQL Server
subprocess.run("curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -", shell=True)
subprocess.run("curl https://packages.microsoft.com/config/ubuntu/$(lsb_release -rs)/prod.list > /etc/apt/sources.list.d/mssql-release.list", shell=True)
subprocess.run("apt-get update", shell=True)
subprocess.run("ACCEPT_EULA=Y apt-get install -y msodbcsql17", shell=True)
subprocess.run("apt-get install -y mssql-tools unixodbc-dev", shell=True)

import streamlit as st
from azure.identity import ClientSecretCredential
from azure.storage.blob import BlobServiceClient
import pyodbc
import os

# Database connection setup
server = 'stockstatementserver.database.windows.net'
database = 'myworkspace'
username = 'AryannChitnis'
password = 'Sulonian@005'
driver = '{ODBC Driver 17 for SQL Server}'
connection_string = f'DRIVER={driver};SERVER={server};PORT=1433;DATABASE={database};UID={username};PWD={password}'

# Azure credentials
client_id = os.getenv('AZURE_CLIENT_ID')
tenant_id = os.getenv('AZURE_TENANT_ID')
client_secret = os.getenv('AZURE_CLIENT_SECRET')
account_url = os.getenv('AZURE_STORAGE_URL')

# Azure Blob Storage credential setup
credentials = ClientSecretCredential(client_id=client_id, client_secret=client_secret, tenant_id=tenant_id)

# Streamlit App for Azure Blob Storage and File Sharing
def workspace_app():
    st.title("Azure Blob Storage and File Sharing App")

    menu = ["Upload File", "List Files", "Get File", "Share File"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Upload File":
        st.subheader("Upload File")
        uploaded_file = st.file_uploader("Choose a file")

        if uploaded_file is not None:
            file_details = {"FileName": uploaded_file.name, "FileType": uploaded_file.type}
            st.write(file_details)

            with open(uploaded_file.name, "wb") as f:
                f.write(uploaded_file.getbuffer())

            upload_blob(uploaded_file.name)
            st.success("File uploaded successfully")

    elif choice == "List Files":
        st.subheader("List Files")
        list_blob()

    elif choice == "Get File":
        st.subheader("Get File")
        blob_name = st.text_input("Enter the blob name to retrieve")

        if st.button("Get File"):
            if blob_name:
                get_blob_data(blob_name)

    elif choice == "Share File":
        st.subheader("Share File")
        blob_name = st.text_input("Enter the blob name to share")
        receiver_user_id = st.text_input("Enter the receiver's UserID")

        if st.button("Share File"):
            if blob_name and receiver_user_id:
                share_file(blob_name, receiver_user_id)
                st.success(f"File {blob_name} shared with UserID {receiver_user_id}")

def upload_blob(file_path):
    container_name = 'user-documents'
    blob_service_client = BlobServiceClient(account_url=account_url, credential=credentials)
    container_client = blob_service_client.get_container_client(container=container_name)

    user_blob_path = os.path.basename(file_path)
    with open(file_path, "rb") as data:
        container_client.upload_blob(name=user_blob_path, data=data)

def list_blob():
    container_name = 'user-documents'
    blob_service_client = BlobServiceClient(account_url=account_url, credential=credentials)
    container_client = blob_service_client.get_container_client(container=container_name)

    blobs = container_client.walk_blobs()
    for blob in blobs:
        st.write(blob.name)

def get_blob_data(blob_name):
    container_name = 'user-documents'
    blob_service_client = BlobServiceClient(account_url=account_url, credential=credentials)
    container_client = blob_service_client.get_container_client(container=container_name)

    blob_client = container_client.get_blob_client(blob_name)
    download_stream = blob_client.download_blob()
    st.download_button(label="Download File", data=download_stream.readall(), file_name=blob_name)

def share_file(blob_name, receiver_user_id):
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO SharedFiles (BlobName, ReceiverUserID) VALUES (?, ?)", (blob_name, receiver_user_id))
    conn.commit()
    conn.close()
