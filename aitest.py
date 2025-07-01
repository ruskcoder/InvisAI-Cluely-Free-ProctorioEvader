import g4f
import g4f.debug
from pathlib import Path

g4f.debug.logging = True

question = "Solve this problem in the image"
# response = g4f.ChatCompletion.create(
#     model="gemini-2.5-pro",
#     provider=g4f.Provider.Gemini,
#     messages=[{"role": "user", "content": question}],
# )

response = g4f.ChatCompletion.create(
    model="gemini-2.5-flash",
    provider=g4f.Provider.Gemini,
    messages=[
        {
            "role": "user", 
            "content": question
        }
    ],
    image=open("download.png", "rb"),
    stream=False,
)
answer = response
print(f"Answer: {answer}")
