import os
import requests
import cv2
import csv
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

# Updated method for extracting account number using Azure Form Recognizer
def extract_details(image_path, endpoint, api_key, model_id='ChequeSheild'):
    document_analysis_client = DocumentAnalysisClient(
        endpoint=endpoint, credential=AzureKeyCredential(api_key)
    )

    with open(image_path, "rb") as f:
        poller = document_analysis_client.begin_analyze_document(model_id, document=f)
    result = poller.result()

    # Initialize variables for extracted data
    Name = None
    Amt_W = None
    Amt_No = None
    Acc_No = None
    Bank_Name = None
    IFSC = None
    Branch_Add = None
    Date = None

    # Extract details and store them in variables
    for idx, document in enumerate(result.documents):
        for name, field in document.fields.items():
            field_value = field.value if field.value else field.content
            if name == "Name":
                Name = field_value
            elif name == "Amt_W":
                Amt_W = field_value
            elif name == "Amt_No":
                Amt_No = field_value
            elif name == "Acc_No":
                Acc_No = field_value
            elif name == "Bank_Name":
                Bank_Name = field_value
            elif name == "IFSC":
                IFSC = field_value
            elif name == "Branch_Add":
                Branch_Add = field_value
            elif name == "Date":
                Date = field_value

    return Name, Amt_W, Amt_No, Acc_No, Bank_Name, IFSC, Branch_Add, Date

# Signature Verification Page
def cheque_processing_app():
    st.title("Cheque Truncation System")

    # Initialize session state if not present
    if 'data_extracted' not in st.session_state:
        st.session_state.data_extracted = False

    # Upload image
    uploaded_image = st.file_uploader("Upload Cheque Image", type=["png", "jpg", "jpeg"])

    if uploaded_image:
        image_path = os.path.join("uploaded_image.jpg")
        with open(image_path, "wb") as f:
            f.write(uploaded_image.getbuffer())
        st.image(image_path, caption="Uploaded Cheque Image")

        # Extract button
        if st.button("Extract"):
            # Form Recognizer configuration
            form_recognizer_endpoint = "https://cts-accno.cognitiveservices.azure.com/"
            form_recognizer_api_key = "6c9933abb91148df9e5cfaeb01c2667f"

            # Extract details from the uploaded image using the new method
            Name, Amt_W, Amt_No, Acc_No, Bank_Name, IFSC, Branch_Add, Date = extract_details(image_path, form_recognizer_endpoint, form_recognizer_api_key)

            # Store extracted data in session state
            st.session_state.data_extracted = True
            st.session_state.extracted_data = {
                "Name": Name,
                "Amt_W": Amt_W,
                "Amt_No": Amt_No,
                "Acc_No": Acc_No,
                "Bank_Name": Bank_Name,
                "IFSC": IFSC,
                "Branch_Add": Branch_Add,
                "Date": Date
            }

        if st.session_state.data_extracted:
            st.subheader("Edit Cheque Details:")
            # Editable fields for extracted data
            data = st.session_state.extracted_data
            Name = st.text_input("Name", value=data["Name"])
            Amt_W = st.text_input("Amount in Words", value=data["Amt_W"])
            Amt_No = st.text_input("Amount in Numbers", value=data["Amt_No"])
            Acc_No = st.text_input("Account Number", value=data["Acc_No"])
            Bank_Name = st.text_input("Bank Name", value=data["Bank_Name"])
            IFSC = st.text_input("IFSC Code", value=data["IFSC"])
            Branch_Add = st.text_input("Branch Address", value=data["Branch_Add"])
            Date = st.text_input("Date", value=data["Date"])

            # Generate button
            if st.button("Generate"):
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
                    extracted_signature_path = "/content/BOBColabProjects/BOBColabProjects/CTS/extracted_signature.jpg"
                    extract_signature(image_path, (x, y, w, h), extracted_signature_path)
                except Exception as e:
                    st.error(f"Error extracting signature: {e}")
                    return

                # Search for the account number in the CSV file and get DB_Signature path
                csv_file_path = "/content/BOBColabProjects/BOBColabProjects/CTS/SignaturesCSV/SignatureGitColab.csv"
                DB_Signature = None
                with open(csv_file_path, mode='r') as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        if row["Acc_No"] == Acc_No:
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
                        st.error
