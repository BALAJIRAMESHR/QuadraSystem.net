from gtts import gTTS
import gradio as gr
import os
import speech_recognition as sr
from googletrans import Translator
from moviepy import VideoFileClip, AudioFileClip, CompositeAudioClip


def video_to_translate(file_obj, initial_language, final_language):
    # Insert Local Video File Path
    videoclip = VideoFileClip(file_obj.name)
    # Extract audio from the video
    videoclip.audio.write_audiofile("test.wav", codec="pcm_s16le")

    # Initialize the recognizer
    r = sr.Recognizer()

    # Language Mapping for Speech Recognition
    language_map = {
        "English": "en-US",
        "Italian": "it-IT",
        "Spanish": "es-MX",
        "Russian": "ru-RU",
        "German": "de-DE",
        "Japanese": "ja-JP",
        "Portuguese": "pt-BR",
        "Tamil": "ta-IN",
        "Kannada": "kn-IN",
        "Telugu": "te-IN",
        "Malayalam": "ml-IN",
        "Hindi": "hi-IN",
    }

    lang_in = language_map.get(initial_language, "en-US")

    # Perform speech-to-text
    with sr.AudioFile("test.wav") as source:
        audio_data = r.record(source)
        text = r.recognize_google(audio_data, language=lang_in)

    # Translate the text to the final language
    lang_out_map = {
        "English": "en",
        "Italian": "it",
        "Spanish": "es",
        "Russian": "ru",
        "German": "de",
        "Japanese": "ja",
        "Portuguese": "pt",
        "Tamil": "ta",
        "Kannada": "kn",
        "Telugu": "te",
        "Malayalam": "ml",
        "Hindi": "hi",
    }

    lang_out = lang_out_map.get(final_language, "en")

    # Initialize the Google API translator
    translator = Translator()
    translation = translator.translate(text, dest=lang_out)
    trans = translation.text

    # Convert the translated text back to speech
    myobj = gTTS(text=trans, lang=lang_out, slow=False)
    myobj.save("audio.wav")

    # Loading the translated audio file
    audioclip = AudioFileClip("audio.wav")

    # Combine the translated audio with the video
    new_audioclip = CompositeAudioClip([audioclip])
    videoclip.audio = new_audioclip
    new_video = "video_translated_" + lang_out + ".mp4"

    # Save the final video with translated audio
    videoclip.write_videofile(new_video)

    return new_video


# Dropdown for selecting initial and final languages
initial_language = gr.inputs.Dropdown(
    [
        "English",
        "Italian",
        "Japanese",
        "Russian",
        "Spanish",
        "German",
        "Portuguese",
        "Tamil",
        "Kannada",
        "Telugu",
        "Malayalam",
        "Hindi",
    ]
)

final_language = gr.inputs.Dropdown(
    [
        "Russian",
        "Italian",
        "Spanish",
        "German",
        "English",
        "Japanese",
        "Portuguese",
        "Tamil",
        "Kannada",
        "Telugu",
        "Malayalam",
        "Hindi",
    ]
)

# Gradio interface
gr.Interface(
    fn=video_to_translate,
    inputs=["file", initial_language, final_language],
    outputs="video",
    verbose=True,
    title="Video Translator",
    description="Upload a video to translate its audio to another language.",
    article="""<div>
                <p style="text-align: center"> Upload your video file, select the original and translated language, and wait for the process to complete. The translated video will be available for download.</p>
                </div>""",
).launch()
