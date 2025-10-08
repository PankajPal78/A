# 🧠 PDF Q&A App with RAG + MongoDB Integration

This Streamlit application enables users to upload PDF documents, extract their text, generate embeddings, and perform question-answering using a **Retrieval-Augmented Generation (RAG)** pipeline.  
Metadata about uploaded files is stored in **MongoDB**, and the app supports **multiple LLM backends** (e.g., Gemini, HuggingFace, OpenAI, etc.).

## 📦 Features

- Upload and process multiple PDFs.
- Extract text and split into semantically coherent chunks.
- Generate vector embeddings using HuggingFace.
- Store and view metadata (filename, size, upload time) in MongoDB.
- Perform conversational Q&A using a retrieval-augmented Gemini model.
- Easily configurable for different LLM providers (Gemini, OpenAI, etc.).

## 🗂️ Directory Structur

📁 PanScience Innovations_pankaj
│
├── app.py # Main Streamlit app
├── .env # Environment variables
├── htmlTemplates.py # HTML templates for chatbot UI
├── requirements.txt # Python dependencies
└── README.md # This file
