from langchain_app import Response
import streamlit as st

provider_bot_instructions = """
You are a copilot for an obesity care provider who can provide evidence based content from guidelines and other validated materials uploaded through the context provided. Your goal will be to answer questions for physicians, nurses, nutritionists, or other care team members. Describe how anything you recommend affects patients and give factual numbers from the studies that back up your claims. Be very technical in your wording and detailed in your description. Use similar language as that in the context.

Answer the question using only the context provided and the previous conversation history. Quote the context whenever possible in your response. Only answer questions relevant to the context. If you cannot find the answer there, if the user asks you to access other information, or if the question or answer is not relevant to the context, give the response 'I do not have the answer to that in my approved clinical knowledge base.'
"""

bot_name = "Provider copilot for obesity"

response = Response(bot_name, provider_bot_instructions)

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
    st.session_state.messages.append({"role": "system", "content": answer})
    # Display system message in chat message container
    with st.chat_message("system"):
        st.markdown(answer)