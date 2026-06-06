import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings


DOCS_PATH = "data/docs"
DB_PATH = "data/faiss_index"


def load_pdf_documents():
    documents = []

    if not os.path.exists(DOCS_PATH):
        return documents

    for file_name in os.listdir(DOCS_PATH):
        if file_name.endswith(".pdf"):
            file_path = os.path.join(DOCS_PATH, file_name)
            loader = PyPDFLoader(file_path)
            docs = loader.load()
            documents.extend(docs)

    return documents


def create_vector_store():
    documents = load_pdf_documents()

    if not documents:
        return None

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )

    split_docs = text_splitter.split_documents(documents)

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vectorstore = FAISS.from_documents(split_docs, embeddings)
    vectorstore.save_local(DB_PATH)

    return vectorstore


def load_vector_store():
    if not os.path.exists(DB_PATH):
        return create_vector_store()

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vectorstore = FAISS.load_local(
        DB_PATH,
        embeddings,
        allow_dangerous_deserialization=True
    )

    return vectorstore


def retrieve_context(query, k=3):
    vectorstore = load_vector_store()

    if vectorstore is None:
        return "No PDF documents found in data/docs."

    docs = vectorstore.similarity_search(query, k=k)

    context = "\n\n".join([doc.page_content for doc in docs])
    return context