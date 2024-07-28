import streamlit as st
from policypro import run_policypro  # Import the run_policypro function
from cheque_truncation_sys import cheque_truncation_sys  # Import the cheque_truncation_sys function
from StockStatPro import stock_stat_pro


def home():
    st.title("Welcome to BankSaarthi-AI")
    st.markdown("""
    ## Overview
    BankSaarthi-AI is designed to enhance operational efficiency in banking through the power of AI. Our application includes the following features:
    - **PolicyPro.AI:** Generate RBI guidelines text.
    - **ChequeTruncationSys:** Automated cheque verification.
    - **SchedulerPro.AI:** Smart scheduling and reminders.
    - **HandGestureRec:** Recognize hand gestures for various commands.

    ## How to Use
    Use the dropdown menu below to navigate to the desired feature. Each feature has a dedicated interface for specific tasks.

    ## About Us
    We are committed to leveraging AI to streamline banking operations, ensuring security, and enhancing user experience.

    ## About Our Founder
    Aryann Chitnis is pursuing his B.Tech in Computer Science Engineering at Manipal University Jaipur. He is focused on making AI accessible and general for everyone, actively involved in research, and currently exploring the world of General AI.
    """)
    st.image("AryannPic.JPG", caption='Aryann Chitnis (Founder and CEO)', width=200)


def main():
    st.title("BankSaarthi-AI")
    st.sidebar.title("BankSaarthi-AI Menu")
    menu_options = ["Home", "PolicyPro.AI", "ChequeTruncationSys", "SchedulerPro.AI",  "Stock Statement Analysis"]
    choice = st.sidebar.selectbox("Go to", menu_options)

    if choice == "Home":
        home()
    elif choice == "PolicyPro.AI":
        run_policypro()
    elif choice == "ChequeTruncationSys":
        cheque_truncation_sys()  # Call the function for ChequeTruncationSys
    elif choice == "SchedulerPro.AI":
        st.write("SchedulerPro.AI functionality here")  # Placeholder for the actual function
    elif choice == "Stock Statement Analysis":
        stock_stat_pro()


if __name__ == "__main__":
    main()
