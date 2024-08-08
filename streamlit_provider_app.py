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
        "feedback": st.session_state.fb_k_faces['score'],
        "feedback information": st.session_state.fb_k_text,
        "timestamp": datetime.now()
    }
    collection.insert_one(document)
    fdbk = ""
    if st.session_state.fb_k_faces['score']:
        fdbk += st.session_state.fb_k_faces['score']
    if st.session_state.fb_k_text:
        fdbk += st.session_state.fb_k_text
    st.session_state.messages.append({"role": "feedback", "content": fdbk})

def give_response(prompt, response):
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
    if 'fb_k_faces' not in st.session_state:
        st.session_state.fb_k_faces = None
    if 'fb_k_text' not in st.session_state:
        st.session_state.fb_k_text = None
    with st.form('feedback form'):
        streamlit_feedback(feedback_type="faces", key="fb_k_faces")
        st.text_input("How is the response?", key="fb_k_text")
        submitted_feedback = st.form_submit_button("Submit feedback", on_click=handle_feedback)

def streamlit_bot(bot_name, assistant_id):
    response = Response(assistant_id)

    # Streamlit app
    st.title(bot_name)
    st.session_state.bot_name = bot_name

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input and handle response
    if prompt := st.chat_input("What is your question?"):
        give_response(prompt, response)
    
    # Display buttons for common questions and handle response
    common_questions = [
        "What are the main GLP-1 side effects? (group them as common to rare)", 
        "What is the best diet for weight loss?",
        "What blood tests to monitor the patient when on GLP-1s?",
        "What is the GLP-1 dosing schedule?",
        "What to consider when switching between obesity medications?"
    ]
    clicked_question = None
    for question in common_questions:
        if st.button(question):
            clicked_question = question
    if clicked_question:
        give_response(clicked_question, response)


def main():
    streamlit_bot("Provider Copilot For Obesity Care", st.secrets["PROVIDER_ASSISTANT_ID"])


if __name__ == "__main__":
    main()