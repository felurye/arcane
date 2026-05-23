import json
import os
import numpy as np
from decouple import config
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

os.environ["OPENAI_API_KEY"] = config("OPENAI_API_KEY")

db_path = "faiss_store"
db = FAISS.load_local(db_path, OpenAIEmbeddings(), allow_dangerous_deserialization=True)

faiss_index = db.index
documents = list(db.docstore._dict.values())

data = []

for i, doc in enumerate(documents):
    vector = faiss_index.reconstruct(i)
    item = {
        "id": i,
        "content": doc.page_content.replace("\n", " ").strip(),
        "partial_vector": vector[:10].tolist()
    }
    data.append(item)

with open("faiss_exported.json", "w", encoding="utf-8") as jsonfile:
    json.dump(data, jsonfile, ensure_ascii=False, indent=2)

print("Arquivo faiss_exportado.json criado com sucesso.")
