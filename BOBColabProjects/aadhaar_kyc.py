import streamlit as st
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from azure.communication.email import EmailClient
import pandas as pd
import random

# Set your Azure Form Recognizer endpoint, key, and model ID
endpoint = "https://banksaarthikyc.cognitiveservices.azure.com/"
api_key = "6ff03177e9ab4de1be790f100578170c"
model_id = "KYCBankSaarthi"

# Initialize the Document Analysis Client
client = DocumentAnalysisClient(endpoint=endpoint, credential=AzureKeyCredential(api_key))

# Set your Azure Communication Services connection string
email_connection_string = "endpoint=https://kyc.india.communication.azure.com/;accesskey=3sUmZhhOwTDq7J5WtnK0C0W5AdIZ1BhPsUbzZaYdOOLHSWrEIn3nJQQJ99AHACULyCpF8uudAAAAAZCShBZf"
email_client = EmailClient.from_connection_string(email_connection_string)

def extract_aadhaar_details(image_data):
    poller = client.begin_analyze_document(model_id=model_id, document=image_data)
    result = poller.result()

    # Initialize variables to store extracted details
    name = None
    aadhar_text = None
    dob = None
    gender = None
    phone_number = None
    aadhaar_number = None

    # Extracting fields from the analyzed document based on your labels
    if result.documents:
        document = result.documents[0]
        for field_name, field in document.fields.items():
            field_value = field.value if field else "Not Found"
            if field_name == "Name":
                name = field_value
            elif field_name == "aadhar":
                aadhar_text = field_value
            elif field_name == "DOB":
                dob = field_value
            elif field_name == "gender":
                gender = field_value
            elif field_name == "phno":
                phone_number = field_value
            elif field_name == "ano":
                aadhaar_number = field_value

    return name, aadhar_text, dob, gender, phone_number, aadhaar_number

def update_csv(details, email):
    csv_path = "/content/BOBColabProjects/BOBColabProjects/aadhaar_details.csv"
    df = pd.DataFrame([details])
    df['Email'] = email
    try:
        existing_df = pd.read_csv(csv_path)
        df = pd.concat([existing_df, df]).drop_duplicates().reset_index(drop=True)
    except FileNotFoundError:
        df.to_csv(csv_path, index=False)
    df.to_csv(csv_path, index=False)

def generate_otp():
    return str(random.randint(1000, 9999))

def send_otp_email(email, otp):
    message = {
        "senderAddress": "DoNotReply@0dab3a2c-dbc6-417c-9c77-aa703deb4d60.azurecomm.net",
        "recipients": {
            "to": [{"address": email}],
        },
        "content": {
            "subject": "Your OTP for Email Verification",
            "plainText": f"Your OTP for email verification is: {otp}\n\nPlease enter this OTP in the form to verify your email.",
        }
    }
    poller = email_client.begin_send(message)
    result = poller.result()
    return result

def verify_otp_and_update_csv(email, input_otp, actual_otp):
    if input_otp == actual_otp:
        kyc_status = "verified"
        csv_path = "/content/BOBColabProjects/BOBColabProjects/aadhaar_details.csv"
        df = pd.read_csv(csv_path)
        df.loc[df['Email'] == email, 'Kyc'] = kyc_status
        df.to_csv(csv_path, index=False)
        return True
    else:
        return False

def aadhaar_kyc_verification():
    st.title("Aadhaar KYC Verification")

    st.markdown("## Upload Aadhaar Card Image")
    
    image_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])

    if image_file is not None:
        image_data = image_file.read()
        name, aadhar_text, dob, gender, phone_number, aadhaar_number = extract_aadhaar_details(image_data)

        st.markdown("### Extracted Details")

        # Display extracted information in a grid of editable text boxes
        col1, col2, col3 = st.columns(3)
        
        with col1:
            name = st.text_input("Name", value=name)
            dob = st.text_input("DOB", value=dob)
            phone_number = st.text_input("Phone Number", value=phone_number)
        
        with col2:
            aadhar_text = st.text_input("Aadhaar Text", value=aadhar_text)
            gender = st.text_input("Gender", value=gender)
            aadhaar_number = st.text_input("Aadhaar Number", value=aadhaar_number)

        with col3:
            st.write("")  # Empty space in the third column

        if aadhar_text == "MERA AADHAAR, MERI PEHCHAN":
            email = st.text_input("Enter your email for OTP verification")
            
            if 'otp' not in st.session_state:
                st.session_state.otp = None

            if st.button("Send OTP"):
                st.session_state.otp = generate_otp()
                send_otp_email(email, st.session_state.otp)
                st.success("OTP sent to your email.")

            if st.session_state.otp:
                input_otp = st.text_input("Enter the OTP sent to your email")
                
                if st.button("Verify OTP"):
                    if verify_otp_and_update_csv(email, input_otp, st.session_state.otp):
                        st.success("KYC Verification successful!")
                    else:
                        st.error("Invalid OTP. Please try again.")
        else:
            st.error("Invalid Aadhaar Card. Please upload a valid Aadhaar card image.")
