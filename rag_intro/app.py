import os

from decouple import config
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate

os.environ["OPENAI_API_KEY"] = config("OPENAI_API_KEY")

pdf_path = "Perceptron.pdf"

loader = PyPDFLoader(pdf_path)
documents = loader.load()

def train():
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    chunks = splitter.split_documents(documents)

    embeddings = OpenAIEmbeddings()
    db_path = "faiss_store"
    if os.path.exists(db_path):
        vectordb = FAISS.load_local(db_path, embeddings, allow_dangerous_deserialization=True)
        vectordb.add_documents(chunks)
    else:
        vectordb = FAISS.from_documents(chunks, embeddings)

    vectordb.save_local(db_path)


def retrieval(query):
    embeddings = OpenAIEmbeddings()
    db_path = "faiss_store"
    vectordb = FAISS.load_local(db_path, embeddings, allow_dangerous_deserialization=True)
    docs = vectordb.similarity_search(query, 4)

    context = "\n\n".join([
            f"Material: {doc.page_content}"
            for doc in docs
        ])

    prompt = ChatPromptTemplate.from_template(
        "Você é um assistente especializado.\n"
        "Responda a pergunta do usuário SOMENTE com base no contexto abaixo.\n"
        "Se não houver informação suficiente, diga isso claramente.\n\n"
        "Contexto:\n{context}\n\n"
        "Pergunta: {query}\n\n"
    )

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    chain = prompt | llm
    response = chain.invoke({"context": context, "query": query})
    return response.content


if __name__ == "__main__":
    print("Treinando o modelo com o PDF...")
    train()
    print("Treinamento concluído.\n")

    while True:
        query = input("Pergunta (ou 'sair'): ").strip()
        if query.lower() == "sair":
            break
        response = retrieval(query)
        print(f"\nResposta: {response}\n")
