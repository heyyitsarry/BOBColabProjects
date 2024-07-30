import streamlit as st
import pandas as pd
from azure.storage.blob import BlobServiceClient
from io import StringIO

# Azure Blob Storage configuration
connection_string = "DefaultEndpointsProtocol=https;AccountName=currchestblob;AccountKey=Vs19yz4uiUumsNRFqJ5ScJXr7mlVX05VEUBTlRpd6pYMKNftYOOck02+643d32OQ7AODucelwTns+AStn8dVnQ==;EndpointSuffix=core.windows.net"
blob_service_client = BlobServiceClient.from_connection_string(connection_string)
container_name = "currency-chests"

def download_blob():
    blob_client = blob_service_client.get_blob_client(container=container_name, blob="currency_chests_data.csv")
    blob_data = blob_client.download_blob()
    return pd.read_csv(StringIO(blob_data.content_as_text()))

def upload_blob(df):
    blob_client = blob_service_client.get_blob_client(container=container_name, blob="currency_chests_data.csv")
    csv_data = df.to_csv(index=False)
    blob_client.upload_blob(csv_data, overwrite=True)

def currency_chest_management():
    st.title("Currency Chest Management System")

    # Display and manage currency chests
    try:
        currency_chests = download_blob()
    except Exception as e:
        st.error(f"Error loading data: {e}")
        currency_chests = pd.DataFrame(columns=["ChestID", "ChestLocation", "CurrencyType", "Amount", "LastUpdated"])

    st.subheader("Currency Chests Table")
    st.write(currency_chests)

    # Add new chest
    st.header("Add New Currency Chest")
    location = st.text_input("Chest Location")
    currency_type = st.text_input("Currency Type")
    amount = st.number_input("Amount", min_value=0.0, step=0.01)
    add_chest_button = st.button("Add Chest")

    if add_chest_button:
        if location and currency_type:
            new_chest_id = currency_chests['ChestID'].max() + 1 if not currency_chests.empty else 1
            new_row = pd.DataFrame({
                "ChestID": [new_chest_id],
                "ChestLocation": [location],
                "CurrencyType": [currency_type],
                "Amount": [amount],
                "LastUpdated": [pd.Timestamp.now()]
            })
            currency_chests = pd.concat([currency_chests, new_row], ignore_index=True)
            upload_blob(currency_chests)
            st.success("Currency chest added successfully!")
        else:
            st.error("Please fill in all fields.")

    # Update existing chest
    st.header("Update Currency Chest")
    chest_id = st.number_input("Chest ID to Update", min_value=1)
    debited = st.text_input("Debited (comma separated)")
    credited = st.text_input("Credited (comma separated)")
    update_chest_button = st.button("Update Chest")

    if update_chest_button:
        try:
            debited_amounts = list(map(float, debited.split(','))) if debited else []
            credited_amounts = list(map(float, credited.split(','))) if credited else []

            total_debited = sum(debited_amounts)
            total_credited = sum(credited_amounts)

            # Update the currency chest record
            if chest_id in currency_chests['ChestID'].values:
                currency_chests.loc[currency_chests['ChestID'] == chest_id, 'Amount'] -= total_debited
                currency_chests.loc[currency_chests['ChestID'] == chest_id, 'Amount'] += total_credited
                currency_chests.loc[currency_chests['ChestID'] == chest_id, 'LastUpdated'] = pd.Timestamp.now()
                upload_blob(currency_chests)
                st.success(f"Chest ID {chest_id} updated: Total Debited = {total_debited}, Total Credited = {total_credited}")
            else:
                st.error("Chest ID not found.")
            
        except ValueError:
            st.error("Invalid amount format. Please enter valid numbers separated by commas.")

    # Delete a chest
    st.header("Delete Currency Chest")
    delete_chest_id = st.number_input("Chest ID to Delete", min_value=1)
    delete_chest_button = st.button("Delete Chest")

    if delete_chest_button:
        if delete_chest_id in currency_chests['ChestID'].values:
            currency_chests = currency_chests[currency_chests['ChestID'] != delete_chest_id]
            upload_blob(currency_chests)
            st.success(f"Chest ID {delete_chest_id} deleted successfully!")
        else:
            st.error("Chest ID not found.")
