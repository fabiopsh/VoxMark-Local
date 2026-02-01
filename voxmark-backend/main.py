from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(title="VoxMark Local Backend")

# CORS setup for dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "VoxMark Local Backend is running"}

from pydantic import BaseModel
from fastapi.responses import Response
from model_manager import model_manager
import io

class SynthesizeRequest(BaseModel):
    text: str

@app.get("/status")
def get_status():
    return {
        "model_present": model_manager.is_model_present(),
        "espeak_present": model_manager.is_espeak_present(),
        "ready_to_synthesize": model_manager.is_ready()
    }

@app.post("/synthesize")
def synthesize(request: SynthesizeRequest):
    audio_data = model_manager.synthesize(request.text)
    if audio_data is None:
         return Response(content="Model not loaded or synthesis failed", status_code=500)
    return Response(content=audio_data, media_type="audio/wav")

@app.post("/install")
def install_model():
    success = model_manager.download_model()
    return {"success": success}

if __name__ == "__main__":
    import uvicorn
    # In production/bundled app, port might be dynamic or 0
    uvicorn.run(app, host="127.0.0.1", port=8000)
