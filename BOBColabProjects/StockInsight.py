import streamlit as st
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
import pyodbc
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import re

# Replace with your Form Recognizer endpoint and API key
endpoint = "https://stockstat.cognitiveservices.azure.com/"
api_key = "bee289aa7ec54560a3639c82853fb5e5"

# DocumentAnalysisClient setup
document_analysis_client = DocumentAnalysisClient(endpoint=endpoint, credential=AzureKeyCredential(api_key))

def extract_content_from_pdf(pdf_file):
    # Analyze the document
    poller = document_analysis_client.begin_analyze_document("prebuilt-document", document=pdf_file)
    result = poller.result()

    # Convert the result to a dictionary
    result_dict = result.to_dict()

    def print_content_details(d, content_list=None):
        if content_list is None:
            content_list = []

        if isinstance(d, dict):
            for key, value in d.items():
                if key == 'value':
                    if isinstance(value, dict):
                        content = value.get('content')
                        if content is not None:
                            content_list.append(content)
                if isinstance(value, (dict, list)):
                    print_content_details(value, content_list)
        elif isinstance(d, list):
            for item in d:
                print_content_details(item, content_list)

        return content_list

    content_list = print_content_details(result_dict)

    def extract_values(content_list):
        variable_mapping = {
            'Date': 0,
            'Acc_No': 1,
            'Name': 2,
            'CashCred': 3,
            'StockVal': 6,
            'Margin': 7,
            'NetSales': -6,
            'DuesPurchBank': -5,
            'Dues': -4,
            'TotalDues': -3,
            'TotalDebts': -2,
            'TalStockVal': -1
        }

        variables = {}
        for var_name, index in variable_mapping.items():
            if index < len(content_list):
                content = content_list[index]

                if isinstance(content, str):
                    if var_name in ['Date', 'Name']:
                        value = content.strip()
                    else:
                        if re.search(r'\d', content):
                            match = re.search(r'\b\d+(?:[\.,]\d*)?\b', content)
                            if match:
                                number_str = match.group()
                                value = float(number_str.replace(',', ''))
                            else:
                                value = None
                        else:
                            value = None
                else:
                    value = None

                variables[var_name] = value
            else:
                variables[var_name] = None

        return variables

    extracted_variables = extract_values(content_list)
    return extracted_variables

def connect_to_sql_server():
    conn = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=tcp:stockstatementserver.database.windows.net,1433;'
        'DATABASE=StoStatDataBase;'
        'UID=AryannChitnis;'
        'PWD=Sulonian@005'
    )
    return conn

def upsert_data_to_db(data):
    conn = connect_to_sql_server()
    cursor = conn.cursor()

    # Check if the record exists
    cursor.execute("SELECT COUNT(*) FROM StoStatDataBase WHERE Acc_No = ? AND Date = ?", data['Acc_No'], data['Date'])
    record_exists = cursor.fetchone()[0] > 0

    if record_exists:
        # Update the existing record
        cursor.execute("""
        UPDATE StoStatDataBase
        SET Name = ?, CashCred = ?, StockVal = ?, Margin = ?, NetSales = ?, DuesPurchBank = ?, Dues = ?, TotalDues = ?, TotalDebts = ?, TalStockVal = ?
        WHERE Acc_No = ? AND Date = ?
        """, data['Name'], data['CashCred'], data['StockVal'], data['Margin'], data['NetSales'], data['DuesPurchBank'], data['Dues'], data['TotalDues'], data['TotalDebts'], data['TalStockVal'], data['Acc_No'], data['Date'])
    else:
        # Insert a new record
        cursor.execute("""
        INSERT INTO StoStatDataBase (Date, Acc_No, Name, CashCred, StockVal, Margin, NetSales, DuesPurchBank, Dues, TotalDues, TotalDebts, TalStockVal)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, data['Date'], data['Acc_No'], data['Name'], data['CashCred'], data['StockVal'], data['Margin'], data['NetSales'], data['DuesPurchBank'], data['Dues'], data['TotalDues'], data['TotalDebts'], data['TalStockVal'])

    conn.commit()
    cursor.close()
    conn.close()

def fetch_data(Acc_No):
    conn = connect_to_sql_server()
    query = """
    SELECT Date, NetSales, StockVal, CashCred
    FROM StoStatDataBase
    WHERE Acc_No = ?
    """
    df = pd.read_sql(query, conn, params=[Acc_No])
    conn.close()
    return df

def stock_stat_pro():
    st.title('Stock Statement Analyser')

    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

    if uploaded_file:
        st.write("Processing file...")
        extracted_data = extract_content_from_pdf(uploaded_file)

        # Display extracted data in read-only text boxes
        st.write("Extracted Data:")
        cols = st.columns(3)
        col_keys = list(extracted_data.keys())
        for i in range(0, len(col_keys), 3):
            with cols[0]:
                if i < len(col_keys):
                    st.text_input(f"{col_keys[i]}", value=extracted_data[col_keys[i]], disabled=True)
            with cols[1]:
                if i+1 < len(col_keys):
                    st.text_input(f"{col_keys[i+1]}", value=extracted_data[col_keys[i+1]], disabled=True)
            with cols[2]:
                if i+2 < len(col_keys):
                    st.text_input(f"{col_keys[i+2]}", value=extracted_data[col_keys[i+2]], disabled=True)

        with st.form(key='cc_form'):
            # Input for CC_Used
            CC_Used = st.number_input("Enter the Credit Used (CC_Used)", min_value=0.0, format="%.2f")

            # Generate button
            submit_button = st.form_submit_button("Generate")

            if submit_button:
                if CC_Used > 0:
                    if 'StockVal' in extracted_data and extracted_data['StockVal'] is not None:
                        stock_val = extracted_data['StockVal']
                        cash_cred = extracted_data['CashCred']

                        # Calculate interest
                        interest_amount = 0.11 * CC_Used

                        # Determine creditor status and display appropriate message
                        if stock_val > CC_Used:
                            st.markdown(f"<h3 style='color:green;'>The borrower is good to go</h3>", unsafe_allow_html=True)
                            status_message = "The borrower is good to go."
                        elif stock_val == CC_Used:
                            st.markdown(f"<h3 style='color:orange;'>The borrower is on the edge</h3>", unsafe_allow_html=True)
                            status_message = "The borrower is on the edge."
                        else:
                            st.markdown(f"<h3 style='color:red;'>The borrower has failed the evaluation</h3>", unsafe_allow_html=True)
                            status_message = "The borrower has failed the evaluation."

                        st.write(f"**Current Interest Payment:** The borrower needs to pay 11% interest on the borrowed amount, which amounts to: ${interest_amount:.2f}")

                        st.write(status_message)

                        # Insert or update data in the database
                        upsert_data_to_db(extracted_data)
                        st.write("Data updated in database.")

                        # Fetch data for plotting
                        df = fetch_data(extracted_data['Acc_No'])
                        if df is not None and not df.empty:
                            st.write("Plotting data...")

                            # Create columns for side-by-side plots
                            col1, col2 = st.columns(2)

                            # Plot NetSales vs Date
                            with col1:
                                fig, ax1 = plt.subplots(figsize=(10, 6))
                                fig.patch.set_facecolor('#f5f5f5')  # Light grey background
                                ax1.set_facecolor('#e0e0e0')  # Slightly darker grey for the plot area

                                ax1.plot(df['Date'], df['NetSales'], marker='o', linestyle='-', color='b', label='NetSales')
                                ax1.set_xlabel('Date')
                                ax1.set_ylabel('Net Sales')
                                ax1.set_title('Net Sales Over Time')
                                ax1.legend()
                                ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
                                ax1.xaxis.set_major_locator(mdates.MonthLocator())
                                ax1.grid(True)

                                st.pyplot(fig)

                            # Plot StockVal vs Date
                            with col2:
                                fig, ax2 = plt.subplots(figsize=(10, 6))
                                fig.patch.set_facecolor('#f5f5f5')  # Light grey background
                                ax2.set_facecolor('#e0e0e0')  # Slightly darker grey for the plot area

                                ax2.plot(df['Date'], df['StockVal'], marker='o', linestyle='-', color='g', label='StockVal')
                                ax2.set_xlabel('Date')
                                ax2.set_ylabel('Stock Value')
                                ax2.set_title('Stock Value Over Time')
                                ax2.legend()
                                ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
                                ax2.xaxis.set_major_locator(mdates.MonthLocator())
                                ax2.grid(True)

                                st.pyplot(fig)
                        else:
                            st.write("No data available for the provided Account Number.")
                    else:
                        st.write("Stock Value not found in the extracted data.")
                else:
                    st.write("Please enter a valid Credit Used amount.")

if __name__ == '__main__':
    stock_stat_pro()
