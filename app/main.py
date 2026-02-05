from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.schemas import VoiceDetectionRequest, VoiceDetectionResponse
from app.security.api_key import verify_api_key
from app.services.audio_utils import load_audio_from_base64
from app.services.feature_extractor import extract_features
from app.services.inference import classify_voice

app = FastAPI(title="AI Voice Detection API")

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {"status": "ok", "message": "AI Voice Detection API is running"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/voice-detection", response_model=VoiceDetectionResponse)
def detect_voice(
    request: VoiceDetectionRequest,
    api_key: str = Depends(verify_api_key)
):
    y, sr = load_audio_from_base64(request.audioBase64)
    features = extract_features(y, sr)

    classification, confidence, explanation = classify_voice(features)

    return {
        "status": "success",
        "language": request.language,
        "classification": classification,
        "confidenceScore": confidence,
        "explanation": explanation
    }
