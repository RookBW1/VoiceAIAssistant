import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class VoiceAssistantEngine:
    def __init__(self):
        # Initializes the OpenAI client using the API key from your .env file
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.load_context_data()

    def load_context_data(self):
        """Loads the static JSON files to inject into the LLM system prompt as the source of truth."""
        with open("data/orders.json", "r") as f:
            self.orders = json.load(f)
        with open("data/policies.json", "r") as f:
            self.policies = json.load(f)

    def speech_to_text(self, audio_file_path: str) -> str:
        """Converts user speech audio file into clear text via Whisper."""
        try:
            with open(audio_file_path, "rb") as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1", 
                    file=audio_file
                )
            return transcript.text
        except Exception as e:
            raise RuntimeError(f"STT Stage Failed: {str(e)}")

    def generate_llm_response(self, user_text: str) -> str:
        """Processes the query against static database context via an LLM."""
        # Anchoring the date explicitly to match our dataset metrics dynamically
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
            response = self.client.chat.completions.create(
                model="gpt-4o-mini", # High-speed, low latency, ideal for Voice applications
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_text}
                ],
                temperature=0.2 # Low temperature ensures strict compliance, no random hallucinations
            )
            return response.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"LLM Processing Stage Failed: {str(e)}")

    def text_to_speech(self, text_input: str, output_audio_path: str):
        """Synthesizes the text response back into high-fidelity voice audio."""
        try:
            response = self.client.audio.speech.create(
                model="tts-1",
                voice="alloy", # Neutral, professional conversational voice tone
                input=text_input
            )
            response.stream_to_file(output_audio_path)
        except Exception as e:
            raise RuntimeError(f"TTS Stage Failed: {str(e)}")
