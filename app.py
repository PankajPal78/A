# importing dependencies
from dotenv import load_dotenv
import os
import streamlit as st
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain_google_genai import ChatGoogleGenerativeAI
from pymongo import MongoClient
from datetime import datetime
from htmlTemplates import css, bot_template, user_template

# ---- MongoDB connection setup ----
def connect_mongo():
    client = MongoClient(os.getenv("MONGO_URI"))
    db = client[os.getenv("MONGO_DB")]
    collection = db[os.getenv("MONGO_COLLECTION")]
    return collection

# ---- store document metadata ----
def store_metadata(filename, filesize):
    collection = connect_mongo()
    doc = {
        "filename": filename,
        "filesize_kb": round(filesize / 1024, 2),
        "upload_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    collection.insert_one(doc)

# ---- view stored metadata ----
def view_metadata():
    collection = connect_mongo()
    docs = list(collection.find({}, {"_id": 0}))
    return docs

# ---- custom prompt ----
custom_template = """Given the following conversation and a follow up question, rephrase the follow up question to be a standalone question.
Chat History:
{chat_history}
Follow Up Input: {question}
Standalone question:"""
CUSTOM_QUESTION_PROMPT = PromptTemplate.from_template(custom_template)

# ---- extract text ----
def get_pdf_text(docs):
    text = ""
    for pdf in docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

# ---- chunk text ----
def get_chunks(raw_text):
    text_splitter = CharacterTextSplitter(separator="\n", chunk_size=1000, chunk_overlap=200, length_function=len)
    chunks = text_splitter.split_text(raw_text)
    return chunks

# ---- embeddings & FAISS ----
def get_vectorstore(chunks):
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2", model_kwargs={'device': 'cpu'})
    vectorstore = FAISS.from_texts(texts=chunks, embedding=embeddings)
    return vectorstore

# ---- conversational chain ----
def get_conversationchain(vectorstore):
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.2, google_api_key=os.getenv("gemini_api_key"))
    memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True, output_key='answer')
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        condense_question_prompt=CUSTOM_QUESTION_PROMPT,
        memory=memory)
    return conversation_chain

# ---- handle user question ----
def handle_question(question):
    response = st.session_state.conversation({'question': question})
    st.session_state.chat_history = response["chat_history"]
    for i, msg in enumerate(st.session_state.chat_history):
        if i % 2 == 0:
            st.write(user_template.replace("{{MSG}}", msg.content), unsafe_allow_html=True)
        else:
            st.write(bot_template.replace("{{MSG}}", msg.content), unsafe_allow_html=True)

# ---- main app ----
def main():
    load_dotenv()
    st.set_page_config(page_title="Q&A", page_icon=":books:")
    st.write(css, unsafe_allow_html=True)

    if "conversation" not in st.session_state:
        st.session_state.conversation = None

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = None

    st.header("Q&A :books:")
    question = st.text_input("Ask question from your document:")
    if question and st.session_state.conversation:
        handle_question(question)

    with st.sidebar:
        st.subheader("📄 Your Documents")
        docs = st.file_uploader("Upload PDF and click 'Process'", accept_multiple_files=True)

        if st.button("Process"):
            with st.spinner("Processing..."):
                for pdf in docs:
                    store_metadata(pdf.name, pdf.size)

                raw_text = get_pdf_text(docs)
                text_chunks = get_chunks(raw_text)
                vectorstore = get_vectorstore(text_chunks)
                st.session_state.conversation = get_conversationchain(vectorstore)
                st.success("Documents processed and metadata stored!")

        # ---- view processed metadata ----
        st.subheader("📂 Stored Metadata")
        data = view_metadata()
        if data:
            for doc in data:
                st.write(f"**File:** {doc.get('filename', 'Unknown')} | **Size:** {doc.get('filesize_kb', 'N/A')} KB | **Uploaded:** {doc.get('upload_time', 'N/A')}")
        else:
            st.write("No document metadata found.")

if __name__ == '__main__':
    main()
