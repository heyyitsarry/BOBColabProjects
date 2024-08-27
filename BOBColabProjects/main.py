import streamlit as st
from policypro import run_policypro
from StockInsight import stock_stat_pro
from WorkSpace import workspace_app
from ChequeShield import signature_verification
from currency_chest import currency_chest_management
from aadhaar_kyc import aadhaar_kyc_verification  # Import the Aadhaar KYC module

def home():
    st.title("Welcome to BankSaarthi-AI")
    st.markdown("""
    ## Overview
    BankSaarthi-AI is designed to enhance operational efficiency in banking through the power of AI. Our application includes the following features:
    - **StockInsight AI:** Automated Stock Statement Analysis.
    - **ChequeShield AI:** Automated cheque verification.
    - **KYCxpert:** Aadhaar KYC Verification.
    - **PolicyPro AI:** Generate RBI guidelines text.
    - **CurrencyVault:** Manage and track currency chests.
    - **MyWorkSpace:** Document Management App.
    
    ## How to Use
    Use the dropdown menu on the left to navigate to the desired feature. Each feature has a dedicated interface for specific tasks.

    ## About Us
    We BankSarthi AI, are committed to leveraging AI to streamline banking operations, ensuring security, and enhancing user experience.

    ## About Our Founder
    Aryann Chitnis is pursuing his B.Tech in Computer Science Engineering at Manipal University Jaipur. He is focused on making AI accessible and general for everyone, actively involved in research, and currently exploring the world of General AI.
    """)
    st.image("/content/BOBColabProjects/BOBColabProjects/AryannPic.JPG", caption='Aryann Chitnis (Founder and CEO)', width=200)

def main():
    st.title("BankSaarthi-AI")
    st.sidebar.title("BankSaarthi-AI Menu")
    menu_options = ["Home", "StockInsight AI", "ChequeShield AI", "KYCxpert", "PolicyPro AI", "CurrencyVault", "Workspace", ]
    choice = st.sidebar.selectbox("Go to", menu_options)

    if choice == "Home":
        home()
    elif choice == "PolicyPro AI":
        run_policypro()
    elif choice == "ChequeShield AI":
        signature_verification()    
    elif choice == "StockInsight AI":
        stock_stat_pro()
    elif choice == "Workspace":
        workspace_app()
    elif choice == "CurrencyVault":
        currency_chest_management()
    elif choice == "KYCxpert":
        aadhaar_kyc_verification()  # Call the Aadhaar KYC function

if __name__ == "__main__":
    main()
