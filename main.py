import os
import time
import traceback  # Import the tracer
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from services.assistant import VoiceAssistantEngine

app = FastAPI(title="Astrixx Voice AI Support Platform")
engine = VoiceAssistantEngine()

TEMP_DIR = "tmp"
os.makedirs(TEMP_DIR, exist_ok=True)

@app.post("/api/process-voice-support")
async def process_voice_support(file: UploadFile = File(...)):
    start_time = time.time()
    
    input_path = os.path.join(TEMP_DIR, f"input_{int(time.time())}_{file.filename}")
    output_filename = f"output_{int(time.time())}.mp3"
    output_path = os.path.join(TEMP_DIR, output_filename)
    
    try:
        contents = await file.read()
        with open(input_path, "wb") as buffer:
            buffer.write(contents)
            
        print("--- [DIAGNOSTIC] Step 1: Starting STT Stage ---")
        user_text = engine.speech_to_text(input_path)
        print(f"--- [DIAGNOSTIC] STT Success. Transcribed: '{user_text}' ---")
        
        print("--- [DIAGNOSTIC] Step 2: Starting LLM Stage ---")
        ai_response_text = engine.generate_llm_response(user_text)
        print(f"--- [DIAGNOSTIC] LLM Success. Response: '{ai_response_text}' ---")
        
        print("--- [DIAGNOSTIC] Step 3: Starting TTS Stage ---")
        engine.text_to_speech(ai_response_text, output_path)
        print("--- [DIAGNOSTIC] TTS Success. Audio Generated ---")
        
        execution_latency = round(time.time() - start_time, 2)
        
        return JSONResponse(content={
            "status": "success",
            "metrics": {"latency_seconds": execution_latency},
            "data": {
                "user_transcript": user_text,
                "ai_response_text": ai_response_text,
                "audio_download_url": f"/api/download-audio/{output_filename}"
            }
        })
        
    except Exception as e:
        # This print block will output the exact traceback lines directly to your terminal
        print("\n=== !!! DETECTED CRITICAL PIPELINE CRASH !!! ===")
        traceback.print_exc() 
        print("================================================\n")
        raise HTTPException(status_code=500, detail=f"Pipeline Interrupted: {str(e)}")
        
    finally:
        if os.path.exists(input_path):
            os.remove(input_path)

@app.get("/api/download-audio/{filename}")
async def download_audio(filename: str):
    file_path = os.path.join(TEMP_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(path=file_path, media_type="audio/mpeg", filename=filename)
    raise HTTPException(status_code=404, detail="Audio file has expired or does not exist.")