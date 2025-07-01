import base64
import io
from PIL import Image
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r'tesseract.exe'

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
