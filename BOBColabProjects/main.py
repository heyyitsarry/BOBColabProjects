# main.py or app.py

import streamlit as st
from policypro import run_policypro
from StockInsight import stock_stat_pro
from WorkSpace import workspace_app
from ChequeShield import signature_verification
from currency_chest import currency_chest_management

def home():
    st.title("Welcome to BankSaarthi-AI")
    st.markdown("""
    ## Overview
    BankSaarthi-AI is designed to enhance operational efficiency in banking through the power of AI. Our application includes the following features:
    - **ChequeShield AI:** Automated cheque verification.
    - **StockInsight AI:** Automated Stock Statement Analysis.
    - **Currency Chest Management:** Manage and track currency chests.
    - **MyWorkSpace:** Document Management App.
    - **PolicyPro AI:** Generate RBI guidelines text.

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
    menu_options = ["Home", "ChequeShield AI", "StockInsight AI", "CurrencyVault", "Workspace", "PolicyPro AI"]
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

if __name__ == "__main__":
    main()

elif choice == "ChequeShield AI":
        signature_verification()