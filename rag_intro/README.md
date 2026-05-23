# RAG Intro

Exemplo introdutório de RAG (Retrieval-Augmented Generation) usando LangChain, FAISS e OpenAI.

O script carrega um PDF, gera embeddings e armazena em um banco vetorial local (FAISS). Em seguida, responde perguntas com base apenas no conteúdo do documento.

## Pré-requisitos

- Python 3.10+
- Chave de API da OpenAI

## Instalação

```bash
cd rag-intro
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Configuração

Crie um arquivo `.env` na pasta `rag-intro/` com base no exemplo:

```bash
cp .env.example .env
```

Edite o `.env` e preencha sua chave:

```
OPENAI_API_KEY=sk-...
```

## Uso

Coloque o PDF que deseja indexar na pasta `rag-intro/` e ajuste o nome do arquivo na variável `caminho_pdf` dentro de `app.py` (padrão: `Perceptron.pdf`).

Execute o script:

```bash
python app.py
```

O script vai:

1. Carregar e indexar o PDF (salva o banco vetorial em `banco_faiss/`)
2. Abrir um loop interativo para perguntas

```
Treinando o modelo com o PDF...
Treinamento concluído.

Pergunta (ou 'sair'): O que é um Perceptron?
Resposta: ...

Pergunta (ou 'sair'): sair
```

> Na segunda execução em diante o banco vetorial já existe, então os documentos são adicionados incrementalmente.

## Scripts extras

### Visualizar embeddings

Gera um gráfico 2D dos vetores semânticos usando t-SNE e marca as 3 frases mais próximas de uma query de exemplo.

```bash
python visualizar_embeddings.py
```

Saída: `embeddings_visualizacao_ligacoes.png` na pasta `rag-intro/`.

### Visualizar FAISS

Exporta todos os documentos indexados no banco vetorial junto com os primeiros 10 valores de cada vetor.

> Requer que o banco `banco_faiss/` já exista (rode `app.py` primeiro).

```bash
python visualizar_faiss.py
```

Saída: `faiss_exportado.json` na pasta `rag-intro/`.

## Estrutura

```
rag-intro/
├── app.py                         # script principal (RAG interativo)
├── visualizar_embeddings.py       # gráfico t-SNE dos embeddings
├── visualizar_faiss.py            # exporta o banco vetorial para JSON
├── Perceptron.pdf                 # PDF de exemplo
├── banco_faiss/                   # banco vetorial gerado (ignorado pelo git)
├── requirements.txt
├── .env.example
└── .gitignore
```
