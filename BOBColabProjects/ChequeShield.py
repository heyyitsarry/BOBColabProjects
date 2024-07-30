import os
import requests
import cv2
import csv
import json
import streamlit as st
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential

# Function to detect signature using Azure Custom Vision
def detect_signature(image_path, prediction_key, endpoint):
    with open(image_path, "rb") as image_file:
        image_data = image_file.read()

    headers = {
        'Content-Type': 'application/octet-stream',
        'Prediction-Key': prediction_key
    }

    response = requests.post(endpoint, headers=headers, data=image_data)
    if response.status_code == 401:
        raise Exception("Access Denied: The operation is not supported with the current subscription key and pricing tier. Please upgrade your subscription.")
    response.raise_for_status()  # Raise an exception for HTTP errors

    predictions = response.json()
    return predictions

# Function to extract signature from an image using coordinates
def extract_signature(image_path, coordinates, output_path):
    if os.path.exists(output_path):
        os.remove(output_path)

    image = cv2.imread(image_path)
    x, y, width, height = coordinates
    signature_image = image[y:y+height, x:x+width]
    cv2.imwrite(output_path, signature_image)

# Function to predict image label using Azure Custom Vision
def predict_image(image_path, prediction_key, endpoint):
    headers = {
        "Prediction-Key": prediction_key,
        "Content-Type": "application/octet-stream"
    }
    with open(image_path, "rb") as image_file:
        image_data = image_file.read()
    response = requests.post(endpoint, headers=headers, data=image_data)
    if response.status_code == 200:
        predictions = response.json()["predictions"]
        highest_prob = max(predictions, key=lambda x: x["probability"])
        return highest_prob["tagName"], highest_prob["probability"]
    else:
        return None, None

# Define variables to hold content values
content1 = None
content2 = None
content3 = None
content4 = None
content5 = None
content6 = None
content7 = None
Account_Number = None


# Function to extract account number from document using Azure Form Recognizer
def extract_account_number(image_path, endpoint, api_key):
    document_analysis_client = DocumentAnalysisClient(endpoint, AzureKeyCredential(api_key))

    with open(image_path, "rb") as f:
        poller = document_analysis_client.begin_analyze_document("prebuilt-document", document=f)

    result = poller.result()
    result_dict = result.to_dict()

    def store_content_values(d):
        global content1, content2, content3, content4, content5, content6, content7, Account_Number
        if isinstance(d, dict):
            for key, value in d.items():
                if key == 'content' and isinstance(value, str):
                    if len(value) == 15 and value.isdigit():
                        Account_Number = value
                    elif content1 is None:
                        content1 = value
                    elif content2 is None:
                        content2 = value
                    elif content3 is None:
                        content3 = value
                    elif content4 is None:
                        content4 = value
                    elif content5 is None:
                        content5 = value
                    elif content6 is None:
                        content6 = value
                    elif content7 is None:
                        content7 = value
                if isinstance(value, (dict, list)):
                    store_content_values(value)
        elif isinstance(d, list):
            for item in d:
                store_content_values(item)

    store_content_values(result_dict)
    return Account_Number

# Signature Verification Page
def signature_verification():
    st.title("Cheque Truncation System")

    # Upload image
    uploaded_image = st.file_uploader("Upload Cheque Image", type=["png", "jpg", "jpeg"])

    if uploaded_image:
        image_path = os.path.join("uploaded_image.jpg")
        with open(image_path, "wb") as f:
            f.write(uploaded_image.getbuffer())
        st.image(image_path, caption="Uploaded Cheque Image")

        # Verification button
        if st.button("Verify"):
            # Define the fixed path for the signature CSV file
            csv_file_path = "/content/BOBColabProjects/BOBColabProjects/CTS/SignaturesCSV/SignatureGitColab.csv"

            # Define the path to save the extracted signature
            extracted_signature_path = "/content/BOBColabProjects/BOBColabProjects/CTS/extracted_signature.jpg"

            # Form Recognizer configuration
            form_recognizer_endpoint = "https://cts-accno.cognitiveservices.azure.com/"
            form_recognizer_api_key = "3b7755f81dc145c8a1f0d0c0b1656538"

            # Extract Account Number from the uploaded image
            Account_Number = extract_account_number(image_path, form_recognizer_endpoint, form_recognizer_api_key)
            if not Account_Number:
                st.error("Account Number not found in the document.")
                return

            # Paths and keys for signature detection and verification
            detection_prediction_key = '0c0ef834d1f446069736654d6370a2d8'
            detection_endpoint = 'https://visiondetnpred-prediction.cognitiveservices.azure.com/customvision/v3.0/Prediction/b8415553-0527-4962-a118-b8615cd44c19/detect/iterations/Iteration1/image'
            verification_prediction_key = '0c0ef834d1f446069736654d6370a2d8'
            verification_endpoint = 'https://visiondetnpred-prediction.cognitiveservices.azure.com/customvision/v3.0/Prediction/d0ea49cb-c85a-4219-a20e-0b7f57643a9b/classify/iterations/sig_ver/image'

            # Extract signature from the image
            try:
                predictions = detect_signature(image_path, detection_prediction_key, detection_endpoint)
                signature_prediction = predictions['predictions'][0]
                bounding_box = signature_prediction['boundingBox']
                image = cv2.imread(image_path)
                height, width, _ = image.shape
                x = int(bounding_box['left'] * width)
                y = int(bounding_box['top'] * height)
                w = int(bounding_box['width'] * width)
                h = int(bounding_box['height'] * height)
                extract_signature(image_path, (x, y, w, h), extracted_signature_path)
            except Exception as e:
                st.error(f"Error extracting signature: {e}")
                return

            # Search for the account number in the CSV file and get DB_Signature path
            DB_Signature = None
            with open(csv_file_path, mode='r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row["Acc_No"] == Account_Number:
                        DB_Signature = row["signature"]
                        break
            if DB_Signature:
                # Predict labels for both signatures
                extracted_label, extracted_prob = predict_image(extracted_signature_path, verification_prediction_key, verification_endpoint)
                db_label, db_prob = predict_image(DB_Signature, verification_prediction_key, verification_endpoint)

                # Check if probabilities are valid
                if extracted_prob is None or db_prob is None:
                    st.error("Error: One of the predictions failed.")
                    return

                # Check probabilities and assign "none" if below 60%
                if extracted_prob < 0.6:
                    extracted_label = "none"
                if db_prob < 0.6:
                    db_label = "none"

                # Compare the labels
                if extracted_label == db_label:
                    st.success("Verified")
                else:
                    st.error("Rejected")
            else:
                st.error(f"Account number {Account_Number} not found.")
