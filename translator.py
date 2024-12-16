# translator.py
import google.generativeai as genai
from langdetect import detect

# Set your Gemini API key directly here
API_KEY = "AIzaSyAnEbQDilqTRSE1Bn8dqAVNhf6Ml_YyX18"  # Replace with your actual API key
genai.configure(api_key=API_KEY)

# Language options

LANGUAGES = {
    "English": "en",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Italian": "it",
    "Portuguese": "pt",
    "Chinese": "zh",
    "Japanese": "ja",
    "Russian": "ru",
    "Hindi": "hi",
    "Arabic": "ar",
    "Tamil": "ta",
}

# Reverse mapping for language codes to names
LANGUAGE_CODES = {v: k for k, v in LANGUAGES.items()}


class GeminiTranslator:
    def __init__(self):
        self.model = genai.GenerativeModel("gemini-pro")
        self.history = {}

    def detect_language(self, text):
        try:
            detected_lang = detect(text)
            return detected_lang if detected_lang in LANGUAGES.values() else "en"
        except:
            return "en"

    def translate(self, text, target_language):
        try:
            prompt = f"Translate the following text to {target_language}. Only return the translated text without any additional commentary. Text: {text}"
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"Error translating text: {e}"

    def add_to_history(
        self,
        chat_name,
        original_text,
        source_language,
        target_language,
        translated_text,
    ):
        if chat_name not in self.history:
            self.history[chat_name] = []
        self.history[chat_name].append(
            {
                "original": original_text,
                "source_language": source_language,
                "target_language": target_language,
                "translation": translated_text,
            }
        )

    def show_history(self, chat_name):
        return self.history.get(chat_name, [])
