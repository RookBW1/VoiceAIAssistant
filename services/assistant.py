import os
import json
import speech_recognition as sr
from gtts import gTTS
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

class VoiceAssistantEngine:
    def __init__(self):
        # Configure the Google GenAI Client
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        self.model_name = 'gemini-2.5-flash'
        self.load_context_data()

    def load_context_data(self):
        """Loads the static JSON files to inject into the LLM system prompt as the source of truth."""
        with open("data/orders.json", "r") as f:
            self.orders = json.load(f)
        with open("data/policies.json", "r") as f:
            self.policies = json.load(f)

    def speech_to_text(self, audio_file_path: str) -> str:
        """Converts user speech audio file into clear text using free speech recognition."""
        recognizer = sr.Recognizer()
        try:
            with sr.AudioFile(audio_file_path) as source:
                audio_data = recognizer.record(source)
            # Uses free web engine to transcribe
            text = recognizer.recognize_google(audio_data)
            return text
        except sr.UnknownValueError:
            return "Error: Could not understand the audio speech clearly."
        except Exception as e:
            raise RuntimeError(f"STT Stage Failed: {str(e)}")

    def generate_llm_response(self, user_text: str) -> str:
        """Processes the query against static database context via Gemini's Free Tier."""
        system_prompt = f"""
        You are an elite, crisp, and empathetic E-commerce Voice Support Assistant. 
        Your primary directive is to answer user queries strictly using the provided Dataset below.
        
        CRITICAL RULES:
        1. If the user asks about an order, query the dataset. If they don't provide an Order ID, ask them for it directly.
        2. Calculate return eligibility carefully. Today's date is strictly June 1, 2026. Compare this with delivery_date and return_window_days.
        3. Keep your responses short, concise, and conversational (max 2-3 sentences) because your output will be read aloud over a voice interface.
        4. If a query cannot be answered via the dataset or policies, politely state that you are transferring them to a human specialist. Do not hallucinate data.

        DATASET CONTEXT:
        Orders DB: {json.dumps(self.orders)}
        Policies DB: {json.dumps(self.policies)}
        """

        try:
            config = types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.2
            )
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=user_text,
                config=config
            )
            return response.text
        except Exception as e:
            raise RuntimeError(f"LLM Processing Stage Failed: {str(e)}")

    def text_to_speech(self, text_input: str, output_audio_path: str):
        """Synthesizes text response to an audio file smoothly using gTTS."""
        try:
            # Generate speech file natively and save it to our tmp path
            tts = gTTS(text=text_input, lang='en', slow=False)
            tts.save(output_audio_path)
        except Exception as e:
            raise RuntimeError(f"TTS Stage Failed: {str(e)}")