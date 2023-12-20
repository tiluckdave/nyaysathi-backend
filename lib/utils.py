from dotenv import load_dotenv
import os
import base64
from bs4 import BeautifulSoup
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from banglaspeech2text import Speech2Text


load_dotenv()

def htmlToText(html):
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text()
    return text

def getDataChunks(data):
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=5, separator="\n", length_function=len)
    chunks = text_splitter.split_text(data)
    return chunks

def createKnowledgeHub(chunks: list):
    embeddings = OpenAIEmbeddings(api_key=os.getenv("OPENAI_KEY"), organization=os.getenv("ORG"))
    knowledge_hub = FAISS.from_texts(chunks, embeddings)
    return knowledge_hub

def createFileWithContent(filename, content):
    with open(f"docs/{filename}.txt", "w", encoding="utf-8", newline='') as f:
        f.write(content)
    return f"docs/{filename}.txt"

def deleteFile(path):
    os.remove(path)
    
def encodeImage(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

def banglaSpeechTOText(audio_path):
    s2t = Speech2Text()
    text = s2t.recognize(audio_path)
    return text