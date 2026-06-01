import os
import time
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from services.assistant import VoiceAssistantEngine

# Initialize FastAPI application
app = FastAPI(title="Astrixx Voice AI Support Platform")

# Instantiate our free-tier local AI engine
engine = VoiceAssistantEngine()

# Ensure a safe temporary directory exists to process incoming audio chunks
TEMP_DIR = "tmp"
os.makedirs(TEMP_DIR, exist_ok=True)

@app.post("/api/process-voice-support")
async def process_voice_support(file: UploadFile = File(...)):
    """
    Core API endpoint: Accepts user audio, runs it through the 3-stage local 
    AI pipeline, tracks execution speed, and returns the structural results.
    """
    start_time = time.time()
    
    # Create secure local paths for processing input and generating output audio
    input_path = os.path.join(TEMP_DIR, f"input_{int(time.time())}_{file.filename}")
    output_filename = f"output_{int(time.time())}.wav"
    output_path = os.path.join(TEMP_DIR, output_filename)
    
    try:
        # Save incoming uploaded audio stream chunk directly onto local disk safely
        contents = await file.read()
        with open(input_path, "wb") as buffer:
            buffer.write(contents)
            
        # 1. STT Stage: Transcribe local audio to plain text
        user_text = engine.speech_to_text(input_path)
        
        # 2. LLM RAG Stage: Map text context against our dataset via Gemini
        ai_response_text = engine.generate_llm_response(user_text)
        
        # 3. TTS Stage: Synthesize text answer into native offline voice audio
        engine.text_to_speech(ai_response_text, output_path)
        
        # Calculate overall execution turnaround time (crucial metric for voice bots)
        execution_latency = round(time.time() - start_time, 2)
        
        return JSONResponse(content={
            "status": "success",
            "metrics": {
                "latency_seconds": execution_latency
            },
            "data": {
                "user_transcript": user_text,
                "ai_response_text": ai_response_text,
                "audio_download_url": f"/api/download-audio/{output_filename}"
            }
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline Interrupted: {str(e)}")
        
    finally:
        # Clean up the raw uploaded input audio file to preserve local memory and disk space
        if os.path.exists(input_path):
            os.remove(input_path)

@app.get("/api/download-audio/{filename}")
async def download_audio(filename: str):
    """Endpoint allowing the frontend UI to fetch and playback the generated response voice."""
    file_path = os.path.join(TEMP_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(path=file_path, media_type="audio/wav", filename=filename)
    raise HTTPException(status_code=404, detail="Audio file has expired or does not exist.")
