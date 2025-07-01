import streamlit as st
import os
import json
import uuid
import google.generativeai as genai
from datetime import datetime

# api key
API_KEY = "AIzaSyADTeEqdBNWDuVWCQBqncKZTmyNlzmCTsI"
genai.configure(api_key=API_KEY)

CHAT_HISTORY_FILE = "chat_history.json"

if "page" not in st.session_state:
    st.session_state.page = "welcome"
if "chat_id" not in st.session_state:
    st.session_state.chat_id = None
if "history" not in st.session_state:
    st.session_state.history = []

# loads chat hsitory
def load_history():
    if os.path.exists(CHAT_HISTORY_FILE):
        with open(CHAT_HISTORY_FILE, "r") as f:
            return json.load(f)
    return {}

# saves chat to history chats
def save_chat(chat_id, content):
    history = load_history()
    history[chat_id] = content
    with open(CHAT_HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

# geminimi model
def call_gemini_api(user_text, user_image):
    try:
        model = genai.GenerativeModel("gemini-2.0-flash")  
        input_parts = []

        if user_text:
            input_parts.append(user_text)
        if user_image:
            input_parts.append(user_image)  
        
        string = ("You are a cyber secruity analysts finding any bugs or threats and explaining it to a non-technical user."
                  "For your response, have the first sentence indicate what area has the threat, and specifically mention in this sentence where the threat(s) occurred. "
                  "Keep the response minimal yet precise. Worry about explanation more than precauation"
                  "as the user needs to know the why. Make sure to identify what type of cyber attack it is, if there is one; and physcially use bold on the type of attack to make it more obvious.")
        response = model.generate_content([string] + input_parts)
        return response.text.strip()
    except Exception as e:
        return f"Error calling Gemini API: {e}"

# welcome page
if st.session_state.page == "welcome":
    st.title("Ventura AI 💻")
    if st.button("Start New Chat"):
        st.session_state.page = "main"
        st.session_state.chat_id = str(uuid.uuid4())
        st.session_state.history = []
        st.rerun()
    st.markdown("---")
    st.subheader("Load Previous Chat 🗑️")
    history = load_history()
    for chat_id, messages in history.items():
        if messages:
            try:
                first_timestamp = messages[0].get("timestamp", "")
                date_display = datetime.strptime(first_timestamp, "%Y-%m-%d %H:%M:%S.%f").strftime("%b %d, %Y %H:%M")
            except:
                date_display = "Invalid Timestamp"
        else:
            date_display = "Empty Chat"

        if st.button(f"Open chat from {date_display}"):
            st.session_state.chat_id = chat_id
            st.session_state.page = "main"
            st.session_state.history = messages
            st.rerun()


# main page
if st.session_state.page == "main":
    st.title("💬 Ventura AI")
    st.markdown("---")
    st.markdown("**Find any bugs or threats in your request:**")

    # shistory
    for idx, item in enumerate(st.session_state.history):
        st.code(f"{item['user_input']}")
        st.markdown(f"**AI:** {item['response']}")
        st.markdown("---")

# Input
    user_input = st.text_area("")
    image = st.file_uploader("", type=["png", "jpg", "jpeg"])

    analyze_clicked = st.button("Analyze with AI")
    
    if analyze_clicked:
        ai_response = call_gemini_api(user_input, image)

        new_entry = {
            "timestamp": str(datetime.today()),
            "user_input": user_input,
            "response": ai_response
        }
        st.session_state.history.append(new_entry)
        save_chat(st.session_state.chat_id, st.session_state.history)
        st.rerun()

    if st.session_state.history:
        feedback = st.radio("Was the last AI response correct?", ["Yes", "No", "Skip"])
        submit_feedback_clicked = st.button("Submit Feedback")
        if submit_feedback_clicked:
            st.session_state.history[-1]["feedback"] = feedback
            save_chat(st.session_state.chat_id, st.session_state.history)
            st.success("Feedback submitted!")

    back_clicked = st.button("🔙 Back to Welcome Page")
    if back_clicked:
        st.session_state.page = "welcome"
        st.rerun()

 
