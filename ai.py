from g4f.client import Client
import g4f
import webview
import base64
from image_text import textFromImage
import threading

from ai_checks import enableGemini

client = Client()

def escape(content):
    return content.replace('\\', '\\\\').replace("'", "\\'").replace('\n', '<br>')

def doAI(dataurl):
    contentGPT = ""
    contentGemini = ""

    def run_gpt():
        nonlocal contentGPT
        for chunk in gptImage(dataurl):
            contentGPT += chunk
            webview.windows[0].evaluate_js(
                f"updateAI('chatgpt', '{escape(contentGPT)}', false)"
            )
        webview.windows[0].evaluate_js(f"updateAI('chatgpt', '{escape(contentGPT)}', true)")

    def run_gemini():
        nonlocal contentGemini
        for chunk in geminiImage(dataurl):
            contentGemini += chunk
            webview.windows[0].evaluate_js(
                f"updateAI('gemini', '{escape(contentGemini)}', false)"
            )
        webview.windows[0].evaluate_js(f"updateAI('gemini', '{escape(contentGemini)}', true)")

    t1 = threading.Thread(target=run_gpt)
    if enableGemini:
        t2 = threading.Thread(target=run_gemini)
    t1.start()
    if enableGemini:
        t2.start()
    t1.join()
    if enableGemini:
        t2.join()


def gptImage(dataurl, prompt='''Solve the problem in this format: 
             The correct option is: (<option-letter A/B/C/D place in parenthesis>) <option> (no period at the end)
             <explanation>
             If in doubt, pick the most correct option. 
        '''):
    response = client.chat.completions.create(
        provider=g4f.Provider.OIVSCodeSer2,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": dataurl}},
                ],
            }
        ],
        stream=True,
    )

    for chunk in response:
        if chunk.choices[0].delta.content:
            content = chunk.choices[0].delta.content
            yield content

def geminiImage(dataurl, prompt='''Solve the problem in this format: 
             The correct option is: (<option-letter A/B/C/D place in parenthesis>) <option> (no period at the end)
             <explanation>
             If in doubt, pick the most correct option. 
             If this question references an image, then respond with the correct option as: "Not Supported"
        '''):

    q = textFromImage(dataurl)

    # response = client.chat.completions.create(
    #     # provider=g4f.Provider.LegacyLMArena,
    #     model="gemini-1.5-pro",
    #     messages=[{"role": "user", "content": prompt + f"\n\n\n{q}"}],
    #     stream=True,
    # )

    response = client.chat.completions.create(
        provider=g4f.Provider.Gemini,
        model="gemini-2.5-flash",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt + f"\n\n\n{q}"},
                    {"type": "image_url", "image_url": dataurl},
                ],
            }
        ],
        stream=True,
    )

    for chunk in response:
        if chunk.choices[0].delta.content:
            content = chunk.choices[0].delta.content
            yield content

if __name__ == "__main__":
    with open("download.png", "rb") as img_file:
        img_bytes = img_file.read()
        dataurl = "data:image/png;base64," + base64.b64encode(img_bytes).decode("utf-8")

    for chunk in geminiImage(dataurl):
        print(chunk, end='', flush=True)
