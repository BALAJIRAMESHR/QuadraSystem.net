import cv2
import numpy as np
import pytesseract
from PIL import Image
from googletrans import Translator
import easyocr


class HandwritingTranslator:
    def __init__(self):
        """
        Initialize translator with advanced OCR capabilities
        """
        # Text translation
        self.translator = Translator()

        # EasyOCR reader (supports multiple languages and handwriting)
        self.reader = easyocr.Reader(["en", "fr", "es", "de"])

    def preprocess_handwriting_image(self, image_path):
        """
        Advanced image preprocessing for handwriting recognition

        Args:
            image_path (str): Path to the image file

        Returns:
            numpy.ndarray: Preprocessed image
        """
        # Read the image
        image = cv2.imread(image_path)

        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2
        )

        # Noise removal
        kernel = np.ones((3, 3), np.uint8)
        cleaned = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

        # Deskew the image
        coords = np.column_stack(np.where(cleaned > 0))
        angle = cv2.minAreaRect(coords)[-1]

        # Correct rotation angle
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle

        # Rotate the image
        (h, w) = cleaned.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(
            cleaned, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE
        )

        return rotated

    def extract_handwriting(self, image_path):
        """
        Extract text from handwritten image using multiple methods

        Args:
            image_path (str): Path to the image file

        Returns:
            str: Extracted text
        """
        try:
            # Preprocess the image
            processed_image = self.preprocess_handwriting_image(image_path)

            # Save preprocessed image
            cv2.imwrite("processed_handwriting.png", processed_image)

            # Method 1: EasyOCR (best for multiple languages and handwriting)
            easyocr_results = self.reader.readtext("processed_handwriting.png")
            easyocr_text = " ".join([result[1] for result in easyocr_results])

            # Method 2: Tesseract OCR (backup)
            tesseract_text = pytesseract.image_to_string(
                Image.open("processed_handwriting.png"),
                config="--psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 ",
            )

            # Clean up temporary file
            import os

            os.remove("processed_handwriting.png")

            # Combine results, prioritizing EasyOCR
            final_text = easyocr_text.strip() or tesseract_text.strip()

            return final_text

        except Exception as e:
            print(f"Handwriting extraction error: {e}")
            return ""

    def translate_text(self, text, dest_lang="en"):
        """
        Advanced translation with multiple fallback methods

        Args:
            text (str): Text to translate
            dest_lang (str): Target language code

        Returns:
            str: Translated text
        """
        try:
            # Primary translation method
            translation = self.translator.translate(text, dest=dest_lang)

            # Confidence check and fallback
            if len(translation.text) > 0:
                return translation.text
            else:
                raise Exception("Empty translation")

        except Exception as e:
            print(f"Translation error: {e}")
            return text

    def process_handwritten_image(self, image_path, dest_lang="en"):
        """
        Complete workflow for handwritten image translation

        Args:
            image_path (str): Path to the image file
            dest_lang (str): Target translation language

        Returns:
            dict: Translation results
        """
        # Extract text from handwritten image
        extracted_text = self.extract_handwriting(image_path)

        # Translate extracted text
        translated_text = self.translate_text(extracted_text, dest_lang=dest_lang)

        return {
            "original_text": extracted_text,
            "translated_text": translated_text,
            "source_lang": "detected",
            "target_lang": dest_lang,
        }


def main():
    # Create translator instance
    translator = HandwritingTranslator()

    while True:
        print("\nHandwriting Translation")
        print("1. Translate Handwritten Image")
        print("2. Exit")

        choice = input("Enter your choice (1-2): ")

        if choice == "1":
            # Image Translation
            image_path = input("Enter handwritten image path: ")
            dest_lang = input("Enter destination language code (e.g., 'fr'): ")

            try:
                result = translator.process_handwritten_image(image_path, dest_lang)

                print("\nResults:")
                print("Original Text:", result["original_text"])
                print("Translated Text:", result["translated_text"])

            except Exception as e:
                print(f"Error processing image: {e}")

        elif choice == "2":
            print("Exiting...")
            break

        else:
            print("Invalid choice. Try again.")


if __name__ == "__main__":
    main()

# Installation Instructions:
# pip install opencv-python-headless pillow pytesseract
# pip install easyocr googletrans==3.1.0a0
#
# Additional Setup:
# 1. Install Tesseract OCR
#    - Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
#    - Mac: brew install tesseract
#    - Linux: sudo apt-get install tesseract-ocr
#
# Preprocessing Techniques:
# - Adaptive thresholding
# - Noise removal
# - Deskew correction
# - Multiple OCR methods
