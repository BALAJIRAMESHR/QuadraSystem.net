import speech_recognition as sr
from googletrans import Translator
from gtts import gTTS
import sounddevice as sd
import numpy as np
import io
import pyaudio
import wave


class RealTimeVoiceTranslator:
    def __init__(self):
        """
        Initialize translation components
        """
        self.recognizer = sr.Recognizer()
        self.translator = Translator()
        self.pyaudio = pyaudio.PyAudio()

        # Expanded Language Mapping with complete language codes
        self.languages = {
            "English": "en",
            "French": "fr",
            "Spanish": "es",
            "German": "de",
            "Chinese": "zh-CN",
            "Arabic": "ar",
            "Russian": "ru",
            "Tamil": "ta",
            "Hindi": "hi",
            "Telugu": "te",
            "Kannada": "kn",
            "Malayalam": "ml",
        }

    def record_and_translate(self, source_lang="English", target_lang="Tamil"):
        """
        Continuous real-time translation with voice playback
        """
        print(f"Translation mode: {source_lang} → {target_lang}")
        print("Press Ctrl+C to exit")

        while True:
            try:
                # Record audio
                print("\nSpeak now...")
                audio_data = self.record_audio(duration=3)

                # Convert speech to text
                original_text = self.speech_to_text(audio_data, source_lang)
                if not original_text:
                    print("No speech detected. Try again.")
                    continue

                # Translate text
                translated_text = self.translate_text(original_text, target_lang)

                # Print translation
                print(f"\nOriginal ({source_lang}): {original_text}")
                print(f"Translation ({target_lang}): {translated_text}")

                # Text to speech for original and translated text
                print("Playing original text...")
                self.text_to_speech(original_text, source_lang)

                print("Playing translated text...")
                self.text_to_speech(translated_text, target_lang)

            except KeyboardInterrupt:
                print("\nTranslation stopped.")
                break
            except Exception as e:
                print(f"An error occurred: {e}")

    def record_audio(self, duration=3):
        """
        Record audio from microphone
        """
        print(f"Recording for {duration} seconds...")
        audio = sd.rec(
            int(duration * 44100), samplerate=44100, channels=1, dtype="float64"
        )
        sd.wait()
        return audio

    def speech_to_text(self, audio_data, source_lang="English"):
        """
        Convert recorded audio to text
        """
        try:
            # Convert numpy array to wav format in memory
            audio_bytes = self._convert_to_wav_bytes(audio_data)

            # Use BytesIO to simulate file
            with sr.AudioFile(io.BytesIO(audio_bytes)) as source:
                audio = self.recognizer.record(source)
                # Use Google's speech recognition
                text = self.recognizer.recognize_google(
                    audio, language=self.languages[source_lang]
                )
                return text
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print(f"Speech recognition error: {e}")
        except Exception as e:
            print(f"Unexpected error in speech recognition: {e}")
        return ""

    def translate_text(self, text, target_lang="Tamil"):
        """
        Translate given text
        """
        try:
            translation = self.translator.translate(
                text, dest=self.languages[target_lang]
            )
            return translation.text
        except Exception as e:
            print(f"Translation error: {e}")
            return "Translation failed"

    def text_to_speech(self, text, lang="English"):
        """
        Convert text to speech and play directly
        """
        try:
            # Create text-to-speech object
            tts = gTTS(text=text, lang=self.languages[lang])

            # Save to memory
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)

            # Play audio
            self._play_audio_from_memory(fp)

        except Exception as e:
            print(f"Text-to-speech error: {e}")

    def _convert_to_wav_bytes(self, audio_data, sample_rate=44100):
        """
        Convert numpy audio data to WAV bytes
        """
        # Normalize and convert to 16-bit PCM
        audio_int16 = (audio_data * 32767).astype(np.int16)

        # Create in-memory bytes buffer
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(audio_int16.tobytes())

        return wav_buffer.getvalue()

    def _play_audio_from_memory(self, fp):
        """
        Play audio from in-memory file using PyAudio
        """
        try:
            # Open the in-memory file as a wave file
            with wave.open(fp, "rb") as wf:
                # Get wave file parameters
                channels = wf.getnchannels()
                rate = wf.getframerate()
                frames = wf.readframes(wf.getnframes())

                # Open PyAudio stream
                stream = self.pyaudio.open(
                    format=self.pyaudio.get_format_from_width(wf.getsampwidth()),
                    channels=channels,
                    rate=rate,
                    output=True,
                )

                # Play the sound
                stream.write(frames)

                # Close stream
                stream.stop_stream()
                stream.close()

        except Exception as e:
            print(f"Audio playback error: {e}")


def main():
    translator = RealTimeVoiceTranslator()

    # Get user input for languages
    print("Available Languages:", list(translator.languages.keys()))

    source_lang = input("Enter source language: ")
    target_lang = input("Enter target language: ")

    # Start real-time translation
    translator.record_and_translate(source_lang, target_lang)


if __name__ == "__main__":
    main()

# Installation Instructions:
# pip install SpeechRecognition googletrans==3.1.0a0
# pip install gTTS sounddevice numpy pyaudio
# - Good internet connection recommended
# - Press Ctrl+C to exit
# - May need system-specific PyAudio installation
"""
System-Specific PyAudio Installation:
- Ubuntu/Debian: sudo apt-get install python3-pyaudio
- macOS: brew install portaudio
- Windows: pip install pipwin && pipwin install pyaudio
"""
