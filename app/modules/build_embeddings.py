from dotenv import load_dotenv
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

load_dotenv()

base_dir = os.path.join(os.path.dirname(__file__), "..", "..")
pdf_path = os.path.join(base_dir, "data", "Python Developer Job Description.pdf")
chroma_path = os.path.join(base_dir, "chroma_db")


def build_vector_db():
    loader = PyPDFLoader(pdf_path)
    pages = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(pages)
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    Chroma.from_documents(chunks, embeddings, persist_directory=chroma_path)
    return len(chunks)


def search_job_info(question):
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    db = Chroma(persist_directory=chroma_path, embedding_function=embeddings)
    results = db.similarity_search(question, k=2)
    return results


if __name__ == "__main__":
    number_of_chunks = build_vector_db()
    print(f"chroma_db was created with {number_of_chunks} chunks")
    results = search_job_info("What skills are required for the job?")
    for r in results:
        print("-" * 40)
        print(r.page_content)
