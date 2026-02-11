from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

# Inisialisasi chat model
chat = ChatOllama(model="gpt-oss:120b-cloud")

# Riwayat pesan
messages = [
    SystemMessage(content="Kamu adalah asisten yang menjawab singkat dan jelas dalam bahasa Indonesia."),
]

print("Chatbot siap! Ketik 'exit' untuk keluar.\n")

while True:
    user_input = input("Kamu: ")
    if user_input.lower() in ["exit", "quit"]:
        print("Sampai jumpa!")
        break

    messages.append(HumanMessage(content=user_input))

    # Panggil model dengan seluruh riwayat
    response = chat.invoke(messages)
    print(f"Bot: {response.content}\n")

    # Simpan respons ke riwayat
    messages.append(response)