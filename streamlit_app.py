from assistant_app import Response
import streamlit as st
from streamlit_feedback import streamlit_feedback

def handle_feedback():
    # Put feedback in a file
    with open("feedback.txt", "a") as f:
        f.write(f"Question: {st.session_state.prompt}\n")
        f.write(f"Answer: {st.session_state.answer}\n")
        f.write(f"Feedback: {st.session_state.fb_k}\n\n")
    st.session_state.messages.append({"role": "feedback", "content": st.session_state.fb_k})

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
        with st.form('form'):
            feedback = st.text_input("How is the response?", key="fb_k")
            submitted_feedback = st.form_submit_button("Submit feedback", on_click=handle_feedback)


def main():
    st.sidebar.title("Navigation")

    # Initialize the current_bot session state variable
    if 'current_bot' not in st.session_state:
        st.session_state.current_bot = None

    # Get the user's choice of chatbot
    choice = st.sidebar.radio("Select chatbot", ["Provider Copilot", "Patient Copilot"])

    # Clear the chat history if the user switches chatbots
    if st.session_state.current_bot != choice:
        st.session_state.messages = []
        st.session_state.current_bot = choice

    # Call the streamlit_bot function with the appropriate assistant ID
    if (choice == "Provider Copilot"):
        streamlit_bot("Provider Copilot For Obesity Care", st.secrets["PROVIDER_ASSISTANT_ID"])
    if (choice == "Patient Copilot"):
        streamlit_bot("Patient Assistant For Obesity Care", st.secrets["PATIENT_ASSISTANT_ID"])


if __name__ == "__main__":
    main()