from openai import OpenAI
import streamlit as st
import time
import re

class Response:
    def __init__(self, assistant_id):
        open_api_key=st.secrets["OPENAI_API_KEY"]
        self.client = OpenAI(api_key=open_api_key)
        self.vector_store_id = st.secrets["VECTOR_STORE_ID"]
        self.assistant_id = assistant_id

        # Create a thread for a conversation
        self.thread = self.client.beta.threads.create()

    def ask_question(self, question):
        # Add user message to the thread
        self.client.beta.threads.messages.create(
            thread_id=self.thread.id,
            role="user",
            content=question
        )
        
        # Run the assistant on the thread
        run = self.client.beta.threads.runs.create(
            thread_id=self.thread.id,
            assistant_id=self.assistant_id
        )
        print("Assistant is running on the thread")

        # Poll for the run status until completion
        while run.status != "completed":
            time.sleep(1)
            run = self.client.beta.threads.runs.retrieve(
                thread_id=self.thread.id,
                run_id=run.id
            )
        print("Polling complete")

        # Retrieve the messages from the thread
        messages = self.client.beta.threads.messages.list(
            thread_id=self.thread.id,
            order="desc"
        )
        
        # Extract and return the assistant's response
        resp = messages.data[0].content[0].text.value
        resp = re.sub(r'【.*?】', '', resp)
        return resp