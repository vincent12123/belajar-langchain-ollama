from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

llm = OllamaLLM(model="gemma3:4b")

prompt = ChatPromptTemplate.from_template("""
Berikan 3 rekomendasi buku tentang {topik} dalam format JSON array.
Setiap item harus punya field: "judul", "penulis", "alasan".
Jawab HANYA dengan JSON, tanpa teks tambahan.
""")

chain = prompt | llm | JsonOutputParser()

hasil = chain.invoke({"topik": "machine learning"})
print(hasil)  # Ini sudah jadi Python dict/list