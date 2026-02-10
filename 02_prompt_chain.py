from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

llm = OllamaLLM(model="gpt-oss:120b-cloud")

# Buat template prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", "Kamu adalah guru pemrograman yang menjelaskan konsep dengan bahasa Indonesia sederhana."),
    ("human", "Jelaskan konsep {topik} untuk pemula."),
])

# Rangkai chain: prompt → LLM
chain = prompt | llm

# Invoke dengan parameter
jawaban = chain.invoke({"topik": "API REST"})
print(jawaban)