import json
import os
import numpy as np
from decouple import config
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

os.environ["OPENAI_API_KEY"] = config("OPENAI_API_KEY")

db_path = "banco_faiss"
db = FAISS.load_local(db_path, OpenAIEmbeddings(), allow_dangerous_deserialization=True)

faiss_index = db.index
documentos = list(db.docstore._dict.values())

dados = []

for i, doc in enumerate(documentos):
    vetor = faiss_index.reconstruct(i)
    item = {
        "id": i,
        "conteudo": doc.page_content.replace("\n", " ").strip(),
        "vetor_parcial": vetor[:10].tolist()
    }
    dados.append(item)

with open("faiss_exportado.json", "w", encoding="utf-8") as jsonfile:
    json.dump(dados, jsonfile, ensure_ascii=False, indent=2)

print("Arquivo faiss_exportado.json criado com sucesso.")
