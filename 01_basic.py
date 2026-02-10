from langchain_ollama import OllamaLLM

# Inisialisasi model
llm = OllamaLLM(model="gpt-oss:120b-cloud")

# Panggil model
jawaban = llm.invoke("Jelaskan apa itu LangChain dalam 3 kalimat, dalam bahasa Indonesia.")
print(jawaban)