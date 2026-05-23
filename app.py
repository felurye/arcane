import os
import warnings

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.prompts import ChatPromptTemplate

os.environ["OPENAI_API_KEY"] = "SUA_API_KEY"

caminho_pdf = "Perceptron.pdf"

loader = PyPDFLoader(caminho_pdf)
documentos = loader.load()

def train():
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    chunks = splitter.split_documents(documentos)

    embeddings = OpenAIEmbeddings()
    db_path = "banco_faiss"
    if os.path.exists(db_path):
        vectordb = FAISS.load_local(db_path, embeddings, allow_dangerous_deserialization=True)
        vectordb.add_documents(chunks)
    else:
        vectordb = FAISS.from_documents(chunks, embeddings)

    vectordb.save_local(db_path)

def train():
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    chunks = splitter.split_documents(documentos)

    embeddings = OpenAIEmbeddings()
    db_path = "banco_faiss"
    if os.path.exists(db_path):
        vectordb = FAISS.load_local(db_path, embeddings, allow_dangerous_deserialization=True)
        vectordb.add_documents(chunks)
    else:
        vectordb = FAISS.from_documents(chunks, embeddings)

    vectordb.save_local(db_path)


def retrieval(pergunta):
    embeddings = OpenAIEmbeddings()
    db_path = "banco_faiss"
    vectordb = FAISS.load_local(db_path, embeddings, allow_dangerous_deserialization=True)
    docs = vectordb.similarity_search(pergunta, 4)

    contexto = "\n\n".join([
            f"Material: {doc.page_content}"
            for doc in docs
        ])
    
    prompt = ChatPromptTemplate.from_template(
        "Você é um assistente especializado.\n"
        "Responda a pergunta do usuário SOMENTE com base no contexto abaixo.\n"
        "Se não houver informação suficiente, diga isso claramente.\n\n"
        "Contexto:\n{contexto}\n\n"
        "Pergunta: {pergunta}\n\n"
    )

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    chain = prompt | llm
    resposta = chain.invoke({"contexto": contexto, "pergunta": pergunta})
    return resposta.content