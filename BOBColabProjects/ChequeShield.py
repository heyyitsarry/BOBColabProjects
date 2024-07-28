import streamlit as st
import requests
import cv2
import os
import csv
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential

# Azure Form Recognizer credentials
form_recognizer_endpoint = "https://cts-accno.cognitiveservices.azure.com/"
form_recognizer_api_key = "3b7755f81dc145c8a1f0d0c0b1656538"

# Custom Vision credentials for signature detection
signature_detection_key = '0c0ef834d1f446069736654d6370a2d8'
signature_detection_endpoint = 'https://visiondetnpred-prediction.cognitiveservices.azure.com/customvision/v3.0/Prediction/b8415553-0527-4962-a118-b8615cd44c19/detect/iterations/Iteration1/image'

# Custom Vision credentials for signature verification
signature_verification_key = '0c0ef834d1f446069736654d6370a2d8'
signature_verification_endpoint = 'https://visiondetnpred-prediction.cognitiveservices.azure.com/customvision/v3.0/Prediction/d0ea49cb-c85a-4219-a20e-0b7f57643a9b/classify/iterations/sig_ver/image'

# CSV file path
csv_file_path = "/content/BOBColabProjects/BOBColabProjects/CTS/SignaturesCSV/SignatureColab.csv"

# Initialize variables to hold content values
content1 = None
content2 = None
content3 = None
content4 = None
content5 = None
content6 = None
Account_Number = None


def detect_signature(image_path):
    with open(image_path, "rb") as image_file:
        image_data = image_file.read()

    headers = {
        'Content-Type': 'application/octet-stream',
        'Prediction-Key': signature_detection_key
    }

    response = requests.post(signature_detection_endpoint, headers=headers, data=image_data)

    if response.status_code != 200:
        st.error(f"Error: {response.status_code} - {response.text}")
        return None

    predictions = response.json()
    return predictions


def extract_signature(image_path, coordinates, output_path):
    if os.path.exists(output_path):
        os.remove(output_path)

    image = cv2.imread(image_path)
    x, y, width, height = coordinates
    signature_image = image[y:y + height, x:x + width]
    cv2.imwrite(output_path, signature_image)


def analyze_document(image_path):
    document_analysis_client = DocumentAnalysisClient(form_recognizer_endpoint,
                                                      AzureKeyCredential(form_recognizer_api_key))

    with open(image_path, "rb") as f:
        poller = document_analysis_client.begin_analyze_document("prebuilt-document", document=f)

    result = poller.result()
    return result.to_dict()


def store_content_values(d):
    global content1, content2, content3, content4, content5, content6, Account_Number
    if isinstance(d, dict):
        for key, value in d.items():
            if key == 'value':
                if isinstance(value, dict):
                    content = value.get('content', None)
                    if content is not None:
                        if content1 is None:
                            content1 = content
                        elif content2 is None:
                            content2 = content
                        elif content3 is None:
                            content3 = content
                        elif content4 is None:
                            content4 = content
                        elif content5 is None:
                            content5 = content
                        elif content6 is None:
                            content6 = content
                        elif Account_Number is None:
                            Account_Number = content
            if isinstance(value, (dict, list)):
                store_content_values(value)
    elif isinstance(d, list):
        for item in d:
            store_content_values(item)


def predict_signature_similarity(image_path):
    headers = {
        "Prediction-Key": signature_verification_key,
        "Content-Type": "application/octet-stream"
    }
    with open(image_path, "rb") as image_file:
        image_data = image_file.read()
    response = requests.post(signature_verification_endpoint, headers=headers, data=image_data)

    st.write("Custom Vision response status:", response.status_code)
    st.write("Custom Vision response text:", response.text)

    if response.status_code == 200:
        predictions = response.json()["predictions"]
        highest_prob = max(predictions, key=lambda x: x["probability"])
        return highest_prob["tagName"], highest_prob["probability"]
    else:
        st.error(f"Error: {response.status_code} - {response.text}")
        return None, None


def verify_signature(extracted_signature_path, db_signature_path):
    tag, probability = predict_signature_similarity(db_signature_path)
    if tag is None or probability is None:
        return "Error: Could not get a valid prediction from the Custom Vision service."

    if tag == "similar" and probability >= 0.75:
        return f"Verified: The signatures match with {probability * 100:.2f}% confidence."
    else:
        return f"Not Verified: The signatures do not match. Confidence: {probability * 100:.2f}%"


def cheque_truncation_sys():
    st.title("Cheque Truncation System")

    uploaded_file = st.file_uploader("Upload a cheque image", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        image_path = os.path.join("/content/BOBColabProjects/BOBColabProjects/CTS", uploaded_file.name)
        with open(image_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.image(image_path, caption="Uploaded Cheque Image", use_column_width=True)

        if st.button("Verify"):
            with st.spinner("Analyzing the cheque..."):
                try:
                    predictions = detect_signature(image_path)
                    if predictions is None:
                        st.error("Signature detection failed.")
                        st.stop()

                    signature_prediction = predictions['predictions'][0]
                    bounding_box = signature_prediction['boundingBox']

                    image = cv2.imread(image_path)
                    height, width, _ = image.shape
                    x = int(bounding_box['left'] * width)
                    y = int(bounding_box['top'] * height)
                    w = int(bounding_box['width'] * width)
                    h = int(bounding_box['height'] * height)

                    extracted_signature_path = "/content/BOBColabProjects/BOBColabProjects/CTS/extracted_signature.jpg"
                    extract_signature(image_path, (x, y, w, h), extracted_signature_path)

                    result_dict = analyze_document(image_path)
                    store_content_values(result_dict)

                    db_signature_path = None
                    with open(csv_file_path, mode='r') as file:
                        reader = csv.DictReader(file)
                        for row in reader:
                            if row["Acc_No"] == Account_Number:
                                db_signature_path = row["signature"]
                                break

                    if db_signature_path:
                        verification_result = verify_signature(extracted_signature_path, db_signature_path)
                        st.success(verification_result)
                    else:
                        st.error("Account number not found in the database.")
                except Exception as e:
                    st.error(f"An error occurred: {e}")
