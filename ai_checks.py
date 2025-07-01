from g4f.cookies import load_cookies_from_browsers

enableGemini = True
def checkGemini():
    global enableGemini
    cook = load_cookies_from_browsers(".google.com")
    if "__Secure-1PSID" not in cook.keys():
        enableGemini = False
        return False
    return True
