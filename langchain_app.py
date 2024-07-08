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

class Response:
    def load_context(self):
        # Load information from text files
        text_files = os.listdir("information_txt")
        for i in range(len(text_files)):
            text_files[i] = "information_txt/" + text_files[i]
            if text_files[i].endswith(".txt"):
                text_loader = TextLoader(text_files[i], encoding = 'UTF-8')
                doc = text_loader.load()
                self.all_docs.append(doc)

        # Index information into vectorstore
        embeddings = OpenAIEmbeddings()
        text_splitter = RecursiveCharacterTextSplitter()
        documents = []
        for doc in self.all_docs:
            documents = documents + text_splitter.split_documents(doc)
        vector = FAISS.from_documents(documents, embeddings)
        self.retriever = vector.as_retriever()

    def __init__(self, bot_name, instructions, model_name):
        self.bot_name = bot_name
        self.instructions = instructions
        self.model_name = model_name
        self.llm = ChatOpenAI(api_key=st.secrets["OPENAI_API_KEY"], model=self.model_name)
        self.all_docs = []
        self.load_context()
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", self.instructions),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{input}"),
            ("system", "Given the conversation and context, respond to the most recent message:\n\n{context}")
        ])
        self.document_chain = create_stuff_documents_chain(self.llm, self.prompt)
        self.retrieval_chain = create_retrieval_chain(self.retriever, self.document_chain)
        self.chat_history = []

    def ask_question(self, question):
        formatted_history = []
        for message in self.chat_history:
            if isinstance(message, HumanMessage):
                formatted_history.append(("user", message.content))
            elif isinstance(message, AIMessage):
                formatted_history.append(("system", message.content))

        # Get the response from the retrieval
        response = self.retrieval_chain.invoke({
            "chat_history": self.chat_history,
            "input": question
        })

        # Update the chat history with the current question and its response
        self.chat_history.extend([
            HumanMessage(content=question),
            AIMessage(content=response["answer"])
        ])

        return response["answer"]
    