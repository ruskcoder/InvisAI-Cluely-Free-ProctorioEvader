from g4f.client import Client
import g4f
import webview
import base64
from utils.image_text import textFromImage
import threading
import ai.ai_checks as ai_checks
import io
from other.settings_manager import settings_manager
g4f.debug.logging = True 

client = Client()

# Global variable to track active AI threads
active_ai_threads = []
ai_cancelled = False

def escape(content):
    return content.replace("\\", "\\\\").replace("'", "\\'").replace("\n", "<br>")

def cancel_ai_processes():
    """Cancel all ongoing AI processes"""
    global ai_cancelled, active_ai_threads
    ai_cancelled = True
    
    # Wait for all threads to finish (they should check ai_cancelled flag)
    for thread in active_ai_threads:
        if thread.is_alive():
            # Note: Python threads can't be forcefully killed, but we set the flag
            # The threads should check this flag and exit gracefully
            pass
    
    # Clear the list
    active_ai_threads.clear()
    print("AI processes cancellation requested")

def doAI(dataurl):
    global ai_cancelled, active_ai_threads

    # Cancel any existing AI processes
    cancel_ai_processes()

    # Reset cancellation flag for new processes
    ai_cancelled = False

    image_text = textFromImage(dataurl)

    def run_ai(provider_func, provider_name):
        global ai_cancelled
        content = ""
        try:
            for chunk in provider_func(dataurl, image_text):
                if ai_cancelled:
                    print(f"AI process {provider_name} cancelled")
                    return
                content += chunk
                webview.windows[0].evaluate_js(f"updateAI('{provider_name}', '{escape(content)}', false)")
            if not ai_cancelled:
                webview.windows[0].evaluate_js(f"updateAI('{provider_name}', '{escape(content)}', true)")
        except Exception as e:
            if ai_cancelled:
                return
            error_message = str(e)
            print(f"Error in {provider_name} AI: {error_message}")
            if "Invalid access token" in error_message:
                error_message = "Invalid access token. Please delete the har_and_cookies folder and try again."
            if "502" in error_message:
                error_message = error_message + ". This error is random and cannot be controlled. "
            webview.windows[0].evaluate_js(f"aiError('{provider_name}', '{escape(error_message)}')")

    threads = []

    # Add ChatGPT if enabled in settings
    if settings_manager.get_setting("enableChatGPT", True):
        threads.append(threading.Thread(target=lambda: run_ai(gptImage, 'chatgpt')))

    # Add other AIs only if enabled in both settings and ai_checks
    if settings_manager.get_setting("enableCopilot", True) and ai_checks.enableCopilot:
        threads.append(threading.Thread(target=lambda: run_ai(copilotImage, 'copilot')))
    if settings_manager.get_setting("enableGemini", True) and ai_checks.enableGemini:
        threads.append(threading.Thread(target=lambda: run_ai(geminiImage, 'gemini')))
    if settings_manager.get_setting("enableQwen", True) and ai_checks.enableQwen:
        threads.append(threading.Thread(target=lambda: run_ai(qwenImage, 'qwen')))
    if settings_manager.get_setting("enableDeepseek", True) and ai_checks.enableDeepseek:
        threads.append(threading.Thread(target=lambda: run_ai(deepseekImage, 'deepseek')))

    # Store threads globally for potential cancellation
    active_ai_threads = threads.copy()

    for t in threads:
        t.daemon = True  # Make threads daemon so they don't prevent app shutdown
        t.start()

    # Don't join threads here - let them run in background
    # This allows for cancellation via the global flag


def gptImage(
    dataurl,
    image_text=None,
    prompt="""Solve the problem in this format: 
             The correct option is: (<option-letter A/B/C/D place in parenthesis>) <option> (no period at the end)
             <explanation>
             Give one AND ONLY One correct answer.   
        """,
):
    global ai_cancelled
    
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
        if ai_cancelled:
            return
        if chunk.choices[0].delta.content:
            yield str(chunk.choices[0].delta.content)


def geminiImage(
    dataurl,
    image_text,
    prompt="""Solve the problem in this format: 
             The correct option is: (<option-letter A/B/C/D place in parenthesis>) <option> (no period at the end)
             <explanation>
             Give one AND ONLY One correct answer. Do not question yourself, and do not change your answer in between.
 """,
):
    global ai_cancelled
    
    response = client.chat.completions.create(
        provider=g4f.Provider.Gemini,
        model="",
        messages=[{"role": "user", "content": prompt}],
        stream=True,
        image=dataurl,
        image_name="download.png",
    )
    thinking = True
    for chunk in response:
        if ai_cancelled:
            return
        if "image/png" in str(chunk.choices[0].delta.content):
            thinking = False
            content = str(chunk.choices[0].delta.content).split("image/png")[1]
            yield content
            continue
        if chunk.choices[0].delta.content and not thinking:
            yield chunk.choices[0].delta.content


def qwenImage(dataurl, image_text, prompt="""Solve the problem in this format: 
             The correct option is: (<option-letter A/B/C/D place in parenthesis>) <option>
             <newline><explanation>
             If in doubt, pick the most correct option. 
             If this question references an image, then respond with the correct option as: "Not Supported"
    """):
    global ai_cancelled
    
    response = g4f.ChatCompletion.create(
        model=g4f.models.qwen_3_4b,
        messages=[{"role": "user", "content": prompt + f"\n\n\n{image_text}"}],
        stream=True,
    )
    thinking = True
    for chunk in response:
        if ai_cancelled:
            return
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
    global ai_cancelled
    
    response = g4f.ChatCompletion.create(
        model=g4f.models.deepseek_r1,
        provider=g4f.Provider.LambdaChat,
        messages=[{"role": "user", "content": prompt + f"\n\n\n{image_text}"}],
        stream=True,
    )
    thinking = True
    for chunk in response:
        if ai_cancelled:
            return
        if "Done in " in str(chunk) or "</think>" in str(chunk) or not str(chunk).strip():
            thinking = False
            continue
        if not thinking:
            if type(chunk) is str:
                yield chunk


def copilotImage(
    dataurl,
    image_text=None,
    prompt="""Solve the question in the image provided to the text chat in this format: 
             The correct option is: (<option-letter A/B/C/D place in parenthesis>) <option> (no period at the end)
             <explanation>
             Give one AND ONLY One correct answer in chat. 
        """,
):
    global ai_cancelled

    base64_data = dataurl.split(",")[1]
    image_binary = base64.b64decode(base64_data)
    image_file = io.BytesIO(image_binary)
    response = client.chat.completions.create(
        provider=g4f.Provider.CopilotAccount,
        model=g4f.Provider.CopilotAccount.models[0],
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                ],
            }
        ],
        stream=True,
        image=image_file,
        image_name="download.png",
    )
    for chunk in response:
        if ai_cancelled:
            return
        if chunk.choices[0].delta.content:
            yield str(chunk.choices[0].delta.content)
