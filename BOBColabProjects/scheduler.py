import streamlit as st
import requests  # Assuming you will use requests to interact with the API

# Define the API key and endpoint
API_KEY = 'AIzaSyBPbjaO0qeO1oApH0AvyAmuORhWK522pD4'
API_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key=' + API_KEY

def generate_schedule(tasks):
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [{"parts": [{"text": "\n".join(tasks)}]}]
    }
    response = requests.post(API_URL, headers=headers, json=data)
    response.raise_for_status()
    return response.json()

def format_schedule(response):
    if 'candidates' in response and len(response['candidates']) > 0:
        schedule_text = response['candidates'][0]['content']['parts'][0]['text']
        return schedule_text
    else:
        return "Unexpected response format."

def scheduler_feature():
    st.title("SchedulerPro AI")
    st.write("Generate your daily schedule based on your tasks.")
    
    tasks = st.text_area("Enter your tasks for the day (one per line)")
    
    if st.button("Generate Schedule"):
        task_list = [task.strip() for task in tasks.split("\n") if task.strip()]
        try:
            schedule = generate_schedule(task_list)
            formatted_schedule = format_schedule(schedule)
            st.success("Here is your schedule for the day:")
            st.text(formatted_schedule)
        except Exception as e:
            st.error(str(e))
