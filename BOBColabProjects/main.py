import streamlit as st
from policypro import run_policypro  # Import the run_policypro function
from ChequeShield import cheque_truncation_sys  # Import the cheque_truncation_sys function
from StockInsight import stock_stat_pro  # Import the stock_stat_pro function
from WorkSpace import workspace_app  # Import the workspace_app function
from scheduler import scheduler_feature  # Import the scheduler_feature function

def home():
    st.title("Welcome to BankSaarthi-AI")
    st.markdown("""
    ## Overview
    BankSaarthi-AI is designed to enhance operational efficiency in banking through the power of AI. Our application includes the following features:
    - **SchedulerPro AI:** Smart scheduling and reminders.
    - **PolicyPro AI:** Generate RBI guidelines text.
    - **MyWorkSpace:** Document Management App.
    - **ChequeShield AI:** Automated cheque verification.
    - **StockInsight AI:** Automated Stock Statement Analysis.

    ## How to Use
    Use the dropdown menu below to navigate to the desired feature. Each feature has a dedicated interface for specific tasks.

    ## About Us
    We BankSarthi AI, are committed to leveraging AI to streamline banking operations, ensuring security, and enhancing user experience.

    ## About Our Founder
    Aryann Chitnis is pursuing his B.Tech in Computer Science Engineering at Manipal University Jaipur. He is focused on making AI accessible and general for everyone, actively involved in research, and currently exploring the world of General AI.
    """)
    st.image("/content/BOBColabProjects/BOBColabProjects/AryannPic.JPG", caption='Aryann Chitnis (Founder and CEO)', width=200)

def main():
    st.title("BankSaarthi-AI")
    st.sidebar.title("BankSaarthi-AI Menu")
    menu_options = ["Home", "SchedulerPro AI", "PolicyPro AI",  "Workspace", "ChequeShield AI", "StockInsight AI"]
    choice = st.sidebar.selectbox("Go to", menu_options)

    if choice == "Home":
        home()
    elif choice == "SchedulerPro AI":
        scheduler_feature()  # Call the function for SchedulerPro AI
    elif choice == "PolicyPro AI":
        run_policypro()
    elif choice == "ChequeShield AI":
        cheque_truncation_sys()  # Call the function for ChequeShield AI
    elif choice == "StockInsight AI":
        stock_stat_pro()
    elif choice == "Workspace":
        workspace_app()

if __name__ == "__main__":
    main()
