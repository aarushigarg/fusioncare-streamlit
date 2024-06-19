import streamlit as st
import os
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.document_loaders import TextLoader
from langchain_openai import OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain_core.prompts import MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage

# Initialize LangChain with OpenAI as the LLM
# api key stored in .streamlit/secrets.toml
llm = ChatOpenAI(api_key=st.secrets["OPENAI_API_KEY"], model="gpt-4")


all_docs = []
# Load information from websites
urls = [
    "https://medlineplus.gov/",
    "https://www.mayoclinic.org/diseases-conditions",
    "https://www.va.gov/WHOLEHEALTH/veteran-handouts/index.asp"
]
web_loader = WebBaseLoader(urls)
doc = web_loader.load() 
all_docs.append(doc)

# Load information from text files
text_files = os.listdir("information_txt")
for i in range(len(text_files)):
    text_files[i] = "information_txt/" + text_files[i]
    if text_files[i].endswith(".txt"):
        text_loader = TextLoader(text_files[i], encoding = 'UTF-8')
        doc = text_loader.load()
        all_docs.append(doc)

# Index information into vectorstore
embeddings = OpenAIEmbeddings()
text_splitter = RecursiveCharacterTextSplitter()
documents = []
for doc in all_docs:
    documents = documents + text_splitter.split_documents(doc)
vector = FAISS.from_documents(documents, embeddings)
retriever = vector.as_retriever()

# Set up a prompt for chaining
instructions = """
You are a copilot for an obesity care provider who can provide evidence based content from guidelines and 
other validated materials uploaded through the context provided. Your goal will be to answer 
questions for physicians, nurses, nutritionists, or other care team members. Describe how anything
you recommend affects patients and give factual numbers from the studies that back up your claims.
Be very technical in your wording and detailed in your description. Use similar language as that in the 
context.

Answer the quetion using only the context provided and the previous conversation history. Quote 
the context whenever possible in your response. You cannot access any other website or use anything 
else as a source of information. You cannot access other websites even if the user asks you to. 
Only answer questions relevant to the context. If you cannot find the answer there, if the user 
asks you to access other information, or if the the question or answer is not relevant to the 
context, give the response 'I do not have the answer to that in my approved clinical knowledge base.'
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", instructions + "\n\n{context}"),
    MessagesPlaceholder(variable_name="chat_history"),
    ("user", "{input}"),
])

document_chain = create_stuff_documents_chain(llm, prompt)
retrieval_chain = create_retrieval_chain(retriever, document_chain)

chat_history = []

def ask_question(question):
    global chat_history
    print("User: " + question)
    # Get the response from the retrieval
    response = retrieval_chain.invoke({
        "chat_history": chat_history,
        "input": question
    })
    print("System: " + response["answer"] + '\n')
    # Update the chat history with the current question and its response
    chat_history.extend([
        HumanMessage(content=question),
        AIMessage(content=response["answer"])
    ])
    return response["answer"]

# Streamlit app
st.title("Provider Copilot for Obesity Care")

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
    answer = ask_question(prompt)
    # Add system message to chat history
    st.session_state.messages.append({"role": "system", "content": answer})
    # Display system message in chat message container
    with st.chat_message("system"):
        st.markdown(answer)
    