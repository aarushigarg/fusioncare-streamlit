from assistant_app import Response
import streamlit as st

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
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)
        answer = response.ask_question(prompt)
        # Add system message to chat history
        st.session_state.messages.append({"role": "assistant", "content": answer})
        # Display system message in chat message container
        with st.chat_message("assistant"):
            st.markdown(answer)


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