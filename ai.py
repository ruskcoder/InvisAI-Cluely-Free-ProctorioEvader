from g4f.client import Client
import g4f
import webview
import base64
from image_text import textFromImage
import threading
from ai_checks import enableGemini, enableDeepseek, enableQwen

client = Client()

def escape(content):
    return content.replace("\\", "\\\\").replace("'", "\\'").replace("\n", "<br>")

def doAI(dataurl):
    image_text = textFromImage(dataurl)
    
    def run_ai(provider_func, provider_name):
        content = ""
        for chunk in provider_func(dataurl, image_text):
            content += chunk
            webview.windows[0].evaluate_js(f"updateAI('{provider_name}', '{escape(content)}', false)")
        webview.windows[0].evaluate_js(f"updateAI('{provider_name}', '{escape(content)}', true)")

    threads = [threading.Thread(target=lambda: run_ai(gptImage, 'chatgpt'))]
    
    if enableGemini:
        threads.append(threading.Thread(target=lambda: run_ai(geminiImage, 'gemini')))
    if enableQwen:
        threads.append(threading.Thread(target=lambda: run_ai(qwenImage, 'qwen')))
    if enableDeepseek:
        threads.append(threading.Thread(target=lambda: run_ai(deepseekImage, 'deepseek')))

    for t in threads:
        t.start()
    for t in threads:
        t.join()


def gptImage(dataurl, image_text=None, prompt="""Solve the problem in this format: 
             The correct option is: (<option-letter A/B/C/D place in parenthesis>) <option> (no period at the end)
             <explanation>
             If in doubt, pick the most correct option. 
        """):
    response = client.chat.completions.create(
        provider=g4f.Provider.OIVSCodeSer2,
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": dataurl}},
            ],
        }],
        stream=True,
    )
    for chunk in response:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content

def geminiImage(dataurl, image_text, prompt="""Solve the problem in this format: 
             The correct option is: (<option-letter A/B/C/D place in parenthesis>) <option> (no period at the end)
             <explanation>
             If in doubt, pick the most correct option. 
             If this question references an image, then respond with the correct option as: "Not Supported"
 """):
    response = client.chat.completions.create(
        provider=g4f.Provider.Gemini,
        model="gemini-2.5-flash",
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt + f"\n\n\n{image_text}"},
                {"type": "image_url", "image_url": dataurl},
            ],
        }],
        stream=True,
    )
    for chunk in response:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content

def qwenImage(dataurl, image_text, prompt="""Solve the problem in this format: 
             The correct option is: (<option-letter A/B/C/D place in parenthesis>) <option>
             <newline><explanation>
             If in doubt, pick the most correct option. 
             If this question references an image, then respond with the correct option as: "Not Supported"
    """):
    response = g4f.ChatCompletion.create(
        model=g4f.models.qwen_3_4b,
        messages=[{"role": "user", "content": prompt + f"\n\n\n{image_text}"}],
        stream=True,
    )
    thinking = True
    for chunk in response:
        if "End of Thought" in str(chunk):
            thinking = False
            continue
        if not thinking:
            yield chunk

def deepseekImage(dataurl, image_text, prompt="""Solve the problem in this format: 
             The correct option is: (<option-letter A/B/C/D place in parenthesis>) <option>
             <br><explanation>
             If in doubt, pick the most correct option. 
             If this question references an image, then respond with the correct option as: "Not Supported"
    """):
    response = g4f.ChatCompletion.create(
        model=g4f.models.deepseek_r1,
        provider=g4f.Provider.LambdaChat,
        messages=[{"role": "user", "content": prompt + f"\n\n\n{image_text}"}],
        stream=True,
    )
    thinking = True
    for chunk in response:
        if "Done in " in str(chunk) or "</think>" in str(chunk) or not str(chunk).strip():
            thinking = False
            continue
        if not thinking:
            if type(chunk) is str:
                yield chunk


# if __name__ == "__main__":
#     with open("download.png", "rb") as img_file:
#         img_bytes = img_file.read()
#         dataurl = "data:image/png;base64," + base64.b64encode(img_bytes).decode("utf-8")

#     image_text = textFromImage(dataurl)
#     for chunk in geminiImage(dataurl, image_text):
#         print(chunk, end="", flush=True)
