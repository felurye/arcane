import os
import numpy as np
from sklearn.manifold import TSNE
from sklearn.metrics.pairwise import euclidean_distances
import matplotlib.pyplot as plt
from decouple import config
from langchain_openai import OpenAIEmbeddings

textos = [
    "Python é uma linguagem de programação",
    "Python serve para programação web",
    "Python é multiplataforma",
    "Gatos são animais fofos",
    "Cachorros são leais",
    "Estou fazendo um risoto",
    "O que é Python?"
]

os.environ["OPENAI_API_KEY"] = config("OPENAI_API_KEY")

embedding_model = OpenAIEmbeddings()
vetores = embedding_model.embed_documents(textos)

vetores_array = np.array(vetores)
tsne = TSNE(n_components=2, perplexity=3, random_state=42)
vetores_2d = tsne.fit_transform(vetores_array)

idx_target = textos.index("O que é Python?")
target_vector = vetores_2d[idx_target].reshape(1, -1)
distances = euclidean_distances(target_vector, vetores_2d).flatten()

closest_indices = distances.argsort()[1:4]

plt.figure(figsize=(12, 7))
for i, texto in enumerate(textos):
    x, y = vetores_2d[i]
    plt.scatter(x, y, marker='o')
    plt.text(x + 0.5, y + 0.5, f"({x:.2f}, {y:.2f}) - {texto}", fontsize=9)

x0, y0 = vetores_2d[idx_target]
plt.scatter(x0, y0, color='red', s=100, label='"O que é Python?"')

for idx in closest_indices:
    x1, y1 = vetores_2d[idx]
    plt.plot([x0, x1], [y0, y1], 'k--', alpha=0.6)

plt.title("Visualização dos Embeddings")
plt.grid(True)
plt.tight_layout()
plt.legend()
plt.savefig("embeddings_visualizacao_ligacoes.png")
print("Gráfico salvo em embeddings_visualizacao_ligacoes.png")
