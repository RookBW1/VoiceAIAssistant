import streamlit as st
import requests
import os

# Configure page metadata layout
st.set_page_config(page_title="Astrixx Voice Support Desk", page_icon="🎙️", layout="centered")

st.title("🎙️ Voice AI Support Assistant (E-commerce Returns)")
st.write("Welcome to the Astrixx Prototype Dashboard. Test the real-time local Voice-RAG pipeline by either recording your voice or uploading an audio file.")

st.markdown("---")

# Section 1: Dual Audio Input Processing (Microphone vs File Upload)
input_mode = st.radio("Choose Input Method:", ["Record via Microphone", "Upload Audio File"], horizontal=True)

audio_to_process = None

if input_mode == "Record via Microphone":
    # Captures live speech natively from browser microphone
    audio_to_process = st.audio_input("Record your query (e.g., 'Where is my order ORD124?')")
else:
    # Explicit file upload path for pre-recorded test cases
    audio_to_process = st.file_uploader("Upload an audio file (.wav or .mp3 format)", type=["wav", "mp3"])

st.markdown("---")

# Section 2: Fire Backend Processing Pipeline
if audio_to_process is not None:
    if st.button("Process Query", type="primary"):
        with st.spinner("Executing Local Pipeline: STT ➔ Gemini RAG ➔ Native TTS..."):
            
            # Pack file payload as multipart/form-data to send to FastAPI
            files = {"file": ("query.wav", audio_to_process.getvalue(), "audio/wav")}
            
            try:
                # Issue synchronous REST post request to local FastAPI instance
                backend_url = "http://127.0.0.1:8000/api/process-voice-support"
                response = requests.post(backend_url, files=files)
                
                if response.status_code == 200:
                    result = response.json()
                    
                    if result.get("status") == "success":
                        st.success(f"Pipeline Executed Successfully! Total Turnaround Time: {result['metrics']['latency_seconds']} seconds")
                        
                        # Display Text Transcript from local Speech Recognition
                        st.subheader("📝 User Speech Transcription")
                        st.info(result["data"]["user_transcript"])
                        
                        # Display AI Text Response bounding context checks
                        st.subheader("🤖 Assistant Context Response")
                        st.success(result["data"]["ai_response_text"])
                        
                        # Stream back and display native synthesized playback audio
                        st.subheader("🔊 Synthesized Voice Response")
                        download_stream_url = f"http://127.0.0.1:8000{result['data']['audio_download_url']}"
                        audio_response_bytes = requests.get(download_stream_url).content
                        st.audio(audio_response_bytes, format="audio/wav")
                        
                    else:
                        st.error(f"Engine Warning: {result.get('detail')}")
                else:
                    st.error(f"Backend Server returned status code: {response.status_code}")
                    
            except requests.exceptions.ConnectionError:
                st.error("Connection Refused: Could not sync with FastAPI. Ensure your FastAPI server backend is running locally on port 8000!")
