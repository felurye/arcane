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

