from assistant_app import Response
import streamlit as st
from streamlit_feedback import streamlit_feedback
from pymongo import MongoClient
from datetime import datetime


def handle_feedback():
    connection_string = st.secrets["MONGODB_CONNECTION_STRING"]
    client = MongoClient(connection_string)
    db = client['bot_feedback']
    collection = db[st.session_state.bot_name]
    document = {
        "question": st.session_state.prompt,
        "answer": st.session_state.answer,
        "feedback": st.session_state.fb_k,
        "timestamp": datetime.now()
    }
    collection.insert_one(document)
    st.session_state.messages.append({"role": "feedback", "content": st.session_state.fb_k})

def answer_common_question(prompt):
    common_question_answers = {
        "What is obesity?": "Answer 1", 
        "What is the best diet for weight loss?": "Answer 2"
    }
    answer = common_question_answers[prompt]
    # Add user message to chat history
    st.session_state.prompt = prompt
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    # Add system message to chat history
    st.session_state.answer = answer
    st.session_state.messages.append({"role": "assistant", "content": answer})
    # Display system message in chat message container
    with st.chat_message("assistant"):
        st.markdown(answer)

def streamlit_bot(bot_name, assistant_id):
    response = Response(assistant_id)

    # Streamlit app
    st.title(bot_name)

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("What is your question?"):
        answer = response.ask_question(prompt)
        # Add user message to chat history
        st.session_state.prompt = prompt
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)
        # Add system message to chat history
        st.session_state.answer = answer
        st.session_state.messages.append({"role": "assistant", "content": answer})
        # Display system message in chat message container
        with st.chat_message("assistant"):
            st.markdown(answer)

        # Get feedback
        with st.form('feedback form'):
            feedback = st.text_input("How is the response?", key="fb_k")
            st.session_state.bot_name = bot_name
            submitted_feedback = st.form_submit_button("Submit feedback", on_click=handle_feedback)
    
    # Display buttons for common questions and handle responses
    common_questions = ["What is obesity?", "What is the best diet for weight loss?"]

    clicked_question = None
    for question in common_questions:
        if st.button(question):
            clicked_question = question
    if clicked_question:
        answer_common_question(clicked_question)


def main():
    st.sidebar.title("Navigation")

    # Initialize the current_bot session state variable
    if 'current_bot' not in st.session_state:
        st.session_state.current_bot = None

    # Get the user's choice of chatbot
    choice = st.sidebar.radio("Select chatbot", ["Provider Copilot", "Patient Assistant"])

    # Clear the chat history if the user switches chatbots
    if st.session_state.current_bot != choice:
        st.session_state.messages = []
        st.session_state.current_bot = choice

    # Call the streamlit_bot function with the appropriate assistant ID
    if (choice == "Provider Copilot"):
        streamlit_bot("Provider Copilot For Obesity Care", st.secrets["PROVIDER_ASSISTANT_ID"])
    if (choice == "Patient Assistant"):
        streamlit_bot("Patient Assistant For Obesity Care", st.secrets["PATIENT_ASSISTANT_ID"])


if __name__ == "__main__":
    main()