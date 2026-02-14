from openai import OpenAI
import os

client = OpenAI(
    api_key=os.environ.get("BLACKBOX_API_KEY"),
    base_url="https://api.blackbox.ai",
)

response = client.chat.completions.create(
    model="flux-pro",
    messages=[
        {
            "role": "user",
            "content": "A futuristic cityscape at sunset",
        }
    ],
)

print(response.choices[0].message.content)  # URL to the generated image