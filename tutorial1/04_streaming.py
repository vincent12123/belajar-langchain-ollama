from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage

chat = ChatOllama(model="gpt-oss:120b-cloud")

messages = [
    SystemMessage(content="Kamu adalah asisten yang membantu dalam bahasa Indonesia."),
    HumanMessage(content="Ceritakan sejarah singkat tentang Python programming language."),
]

print("Bot: ", end="", flush=True)
for chunk in chat.stream(messages):
    print(chunk.content, end="", flush=True)
print()  # newline di akhir