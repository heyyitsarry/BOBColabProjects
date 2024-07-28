import os
from datetime import datetime, timedelta
import streamlit as st
from azure.identity import ClientSecretCredential
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
import pyodbc
import subprocess

# Install the ODBC driver for SQL Server
subprocess.run("curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -", shell=True)
subprocess.run("curl https://packages.microsoft.com/config/ubuntu/$(lsb_release -rs)/prod.list > /etc/apt/sources.list.d/mssql-release.list", shell=True)
subprocess.run("apt-get update", shell=True)
subprocess.run("ACCEPT_EULA=Y apt-get install -y msodbcsql17", shell=True)
subprocess.run("apt-get install -y mssql-tools unixodbc-dev", shell=True)

# Ensure environment variables are set
os.environ['AZURE_CLIENT_ID'] = "80c7bd7d-13bd-40d0-ac0f-4e47b1cb811a"
os.environ['AZURE_TENANT_ID'] = "8b4ec0c7-9e79-4e6b-9f9d-f57ad49dcfef"
os.environ['AZURE_CLIENT_SECRET'] = "5K08Q~XGNWtNN5thQO1hr.5EClSbDZzkV5-msbVT"
os.environ['AZURE_STORAGE_URL'] = "https://documanstor.blob.core.windows.net/"
os.environ['AZURE_STORAGE_ACCOUNT_NAME'] = "documanstor"
os.environ['AZURE_STORAGE_ACCOUNT_KEY'] = "Rwc4kNek1G7N/bE8wEKFMrrWn3cLbxRD3aa02tZNYssS+qZ84iIfCGnReSvdI99H/QYbiJ7Mqg0A+ASt9v9JpQ=="

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

# Function to generate a blob SAS token
def create_blob_sas(account_name, container_name, blob_name, account_key, permission, expiry):
    sas_token = generate_blob_sas(
        account_name=account_name,
        container_name=container_name,
        blob_name=blob_name,
        account_key=account_key,
        permission=permission,
        expiry=expiry
    )
    return sas_token

# Function to share a blob
def share_file(blob_name, expiry_hours=1):
    account_name = os.environ['AZURE_STORAGE_ACCOUNT_NAME']
    account_key = os.environ['AZURE_STORAGE_ACCOUNT_KEY']
    container_name = 'user-documents'

    # Generate a SAS token for the blob
    sas_token = create_blob_sas(
        account_name=account_name,
        container_name=container_name,
        blob_name=blob_name,
        account_key=account_key,
        permission=BlobSasPermissions(read=True),
        expiry=datetime.utcnow() + timedelta(hours=expiry_hours)
    )
    
    blob_url = f"https://{account_name}.blob.core.windows.net/{container_name}/{blob_name}?{sas_token}"
    return blob_url

# Streamlit App for Azure Blob Storage and File Sharing
def workspace_app():
    st.title("Data Storage and File Sharing App")

    menu = ["Welcome", "Upload File", "List Files", "Get File", "Share File"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Welcome":
        st.subheader("Welcome")
        st.markdown("""
        ## How to Use This App
        - **Upload File:** Upload a file to the Azure Blob Storage.
        - **List Files:** List all files in the Azure Blob Storage.
        - **Get File:** Retrieve and download a specific file from the Azure Blob Storage.
        - **Share File:** Share a file with another user.

        Use the menu on the left to navigate through the different functionalities of this app.
        """)

    elif choice == "Upload File":
        st.subheader("Upload File")
        uploaded_file = st.file_uploader("Choose a file")

        if uploaded_file is not None:
            file_name = uploaded_file.name
            with open(file_name, "wb") as f:
                f.write(uploaded_file.getbuffer())

            upload_blob(file_name)
            st.success(f"'{file_name}' has been uploaded successfully.")

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

        if st.button("Share File"):
            if blob_name:
                sas_url = share_file(blob_name)
                st.success(f"File '{blob_name}' shared successfully. Access it [here]({sas_url})")

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

    blobs = container_client.list_blobs()
    for blob in blobs:
        st.write(blob.name)

def get_blob_data(blob_name):
    container_name = 'user-documents'
    blob_service_client = BlobServiceClient(account_url=account_url, credential=credentials)
    container_client = blob_service_client.get_container_client(container=container_name)

    blob_client = container_client.get_blob_client(blob_name)
    download_stream = blob_client.download_blob()
    st.download_button(label="Download File", data=download_stream.readall(), file_name=blob_name)

if __name__ == "__main__":
    workspace_app()
