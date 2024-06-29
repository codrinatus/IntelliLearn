import fitz
import pytesseract
from PIL import Image
import io


def extract_text_and_images(pdf_path):
    doc = fitz.open(pdf_path)
    full_text = ""

    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text("text")
        trim = text.replace("FII, UAIC\n", "")
        full_text += trim

        image_list = page.get_images(full=True)
        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]

            image = Image.open(io.BytesIO(image_bytes))

            image_text = pytesseract.image_to_string(image)

            full_text += "\n[Image Text]\n" + image_text + "\n[/Image Text]\n"

    return full_text
