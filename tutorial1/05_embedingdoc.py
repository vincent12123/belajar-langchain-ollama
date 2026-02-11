# 05_rag.py (versi Ollama embedding)
from langchain_ollama import OllamaLLM, OllamaEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document

# 1. Load dokumen
with open("docs/info.txt", "r", encoding="utf-8") as f:
    text = f.read()

docs = [Document(page_content=text)]

# 2. Embedding pakai Ollama (bukan HuggingFace lagi!)
embeddings = OllamaEmbeddings(model="nomic-embed-text")
vectorstore = FAISS.from_documents(docs, embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# 3. LLM juga pakai Ollama
llm = OllamaLLM(model="gemma3:4b")

# 4. Prompt RAG
prompt = ChatPromptTemplate.from_template("""
Kamu adalah asisten yang menjawab berdasarkan konteks.
Jawab dalam bahasa Indonesia yang jelas dan ringkas.
Jika jawabannya tidak ada dalam konteks, katakan "Saya tidak menemukan informasinya."

Konteks:
{context}

Pertanyaan: {question}

Jawaban:
""")

# 5. Fungsi tanya jawab
def tanya(question: str):
    relevant_docs = retriever.invoke(question)
    context = "\n\n".join(doc.page_content for doc in relevant_docs)
    chain = prompt | llm
    return chain.invoke({"context": context, "question": question})

# 6. Loop interaktif
if __name__ == "__main__":
    print("RAG Chatbot siap! Ketik 'exit' untuk keluar.\n")
    while True:
        q = input("Pertanyaan: ")
        if q.lower() == "exit":
            break
        jawab = tanya(q)
        print(f"\nJawaban: {jawab}\n")