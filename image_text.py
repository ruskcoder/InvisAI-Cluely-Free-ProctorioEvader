import base64
import io, os
from PIL import Image
import pytesseract
from ai_checks import disableAll

def checkTesseract():
    if os.path.exists(r"C:/Program Files/Tesseract-OCR/tesseract.exe"):
        return True
    else:
        disableAll()
        return False

pytesseract.pytesseract.tesseract_cmd = r"C:/Program Files/Tesseract-OCR/tesseract.exe"

def textFromImage(dataurl):
    try:
        if ',' in dataurl:
            header, encoded = dataurl.split(',', 1)
        else:
            encoded = dataurl
        
        image_data = base64.b64decode(encoded)
        
        image = Image.open(io.BytesIO(image_data))
        
        extracted_text = pytesseract.image_to_string(image)
        
        return extracted_text.strip()
        
    except Exception as e:
        print(f"Error extracting text from image: {e}")
        return ""
