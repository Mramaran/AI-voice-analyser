# Voice AI Detector - Render Deployment Guide

## 📋 Table of Contents
- [Project Overview](#project-overview)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Local Development Setup](#local-development-setup)
- [Render Deployment](#render-deployment)
- [API Key Configuration](#api-key-configuration)
- [Testing the API](#testing-the-api)
- [Security Best Practices](#security-best-practices)
- [Troubleshooting](#troubleshooting)
- [Monitoring & Maintenance](#monitoring--maintenance)

---

## 📖 Project Overview

**Voice AI Detector** is a FastAPI-based REST API that analyzes audio samples to determine whether they are **Human** or **AI-generated** voice recordings.

### Key Features
- ✅ Real-time voice classification
- ✅ MFCC-based feature extraction
- ✅ Scikit-learn ML model
- ✅ API key authentication
- ✅ Base64 audio input support
- ✅ Health check endpoints
- ✅ CORS enabled for web integration

### Tech Stack
- **Backend**: FastAPI + Uvicorn
- **ML**: scikit-learn, librosa, numpy
- **Deployment**: Render (PaaS)
- **Authentication**: API Key (Header-based)

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         CLIENT                              │
│  (Web App / Mobile / Postman / curl)                        │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ POST /api/voice-detection
                         │ Header: x-api-key
                         │ Body: { audioBase64, language, format }
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    FASTAPI SERVER                           │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  1. API Key Validation (app/security/api_key.py)    │   │
│  └──────────────────────┬───────────────────────────────┘   │
│                         │                                    │
│  ┌──────────────────────▼───────────────────────────────┐   │
│  │  2. Audio Decoding (Base64 → Binary)                │   │
│  └──────────────────────┬───────────────────────────────┘   │
│                         │                                    │
│  ┌──────────────────────▼───────────────────────────────┐   │
│  │  3. Feature Extraction (librosa)                     │   │
│  │     - 13 MFCC coefficients                           │   │
│  │     - 13 Delta MFCC                                  │   │
│  │     - 1 Spectral Centroid                            │   │
│  │     = 27 features total                              │   │
│  └──────────────────────┬───────────────────────────────┘   │
│                         │                                    │
│  ┌──────────────────────▼───────────────────────────────┐   │
│  │  4. Model Inference (voice_auth_model.pkl)          │   │
│  │     - Binary Classification: HUMAN / AI_GENERATED    │   │
│  │     - Confidence Score: 0.0 - 1.0                    │   │
│  └──────────────────────┬───────────────────────────────┘   │
│                         │                                    │
│  ┌──────────────────────▼───────────────────────────────┐   │
│  │  5. Response JSON                                    │   │
│  │     { classification, confidenceScore, explanation } │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 Prerequisites

### Required Tools
- **Python**: 3.9 - 3.11 (3.13 has compatibility issues with some libraries)
- **pip**: Latest version
- **Git**: For version control
- **GitHub Account**: For repository hosting
- **Render Account**: https://render.com (free tier available)

### Required Files
Ensure these files exist in your project:
```
voice-ai-detector/
├── api.py                          # Main FastAPI application
├── requirements.txt                # Python dependencies
├── voice_auth_model.pkl            # Trained ML model
├── scaler.pkl                      # Feature scaler (optional)
├── .env                            # Local environment variables (DO NOT commit)
├── .gitignore                      # Git ignore rules
├── render.yaml                     # Render configuration (optional)
└── README.md                       # Project documentation
```

---

## 💻 Local Development Setup

### Step 1: Clone Repository
```bash
git clone https://github.com/your-username/voice-ai-detector.git
cd voice-ai-detector
```

### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Create `.env` File
Create a `.env` file in the project root:
```env
API_KEY=sk_test_local_development_key_123456789
PYTHON_VERSION=3.11.0
```

### Step 5: Run Locally
```bash
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

### Step 6: Test Locally
Open browser: http://127.0.0.1:8000/docs

Or use curl:
```bash
curl -X POST "http://127.0.0.1:8000/api/voice-detection" \
  -H "x-api-key: sk_test_local_development_key_123456789" \
  -H "Content-Type: application/json" \
  -d '{
    "language": "en",
    "audioFormat": "wav",
    "audioBase64": "UklGRiQAAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQAAAAA="
  }'
```

---

## 🚀 Render Deployment

### Option A: GitHub Integration (Recommended)

#### Step 1: Prepare Repository

**Update `.gitignore`:**
```gitignore
# Environment variables
.env
.env.local
.env.production

# Virtual environment
venv/
env/
ENV/

# Python cache
__pycache__/
*.py[cod]
*$py.class
*.so

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Large files (if models > 100MB)
# voice_auth_model.pkl
# scaler.pkl
```

**Commit and Push:**
```bash
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

#### Step 2: Create Render Web Service

1. Go to https://dashboard.render.com/
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure service:

| Setting | Value |
|---------|-------|
| **Name** | `voice-ai-detector` |
| **Runtime** | Python 3 |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn api:app --host 0.0.0.0 --port $PORT` |
| **Plan** | Free (or Starter for production) |

5. Click **"Create Web Service"**

#### Step 3: Configure Environment Variables

In Render Dashboard → **Environment** tab:

**Add Environment Variable:**
```
Key: API_KEY
Value: sk_prod_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6  ← Generate secure key (see below)
```

**Generate Secure API Key:**
```python
# Run this locally to generate a secure key
import secrets
api_key = f"sk_prod_{secrets.token_urlsafe(32)}"
print(api_key)
```

Example output: `sk_prod_X4j9K2mP_L7nQ3wR8vY5zT6bN1cH0dF4gS2eA9kM`

#### Step 4: Handle Model Files

**If models < 100MB:**
```bash
# Include in Git
git add voice_auth_model.pkl scaler.pkl
git commit -m "Add trained models"
git push
```

**If models > 100MB:**

1. **Upload to Render Disk:**
   - Render Dashboard → **Disks** → **Add Disk**
   - Name: `ml-models`
   - Size: 1GB
   - Mount Path: `/models`

2. **Update Code:**
```python
# In api.py
MODEL_PATH = os.getenv("MODEL_PATH", "/models/voice_auth_model.pkl")
SCALER_PATH = os.getenv("SCALER_PATH", "/models/scaler.pkl")
```

3. **Upload Models via SSH or Render Dashboard**

### Option B: Manual Deploy (Docker - Alternative)

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libsndfile1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
```

Deploy to Render using Docker:
```bash
render deploy --docker
```

---

## 🔑 API Key Configuration

### Understanding API Keys on Render

Render doesn't provide a built-in "API Key" service. Instead, you manage API keys through **Environment Variables**.

### Two Types of Keys

#### 1. **Application API Key** (Your Voice Detector API)
This is the key your **clients** use to authenticate with your API.

**Setup:**
- Render Dashboard → Your Service → **Environment** tab
- Add variable: `API_KEY=sk_prod_your_secure_key`
- Your code reads it via `os.getenv("API_KEY")`

#### 2. **Render API Key** (Render Platform Access)
This is for **programmatic access** to Render's platform API (manage services, deployments, etc.).

**Setup:**
1. Render Dashboard → Profile (top right) → **Account Settings**
2. Scroll to **"API Keys"** section
3. Click **"Create API Key"**
4. Name: `voice-detector-admin`
5. Copy key (shows once!) → Store in password manager

**Usage Example:**
```python
import requests

RENDER_API_KEY = "rnd_xxx..."  # Your Render platform API key

headers = {
    "Authorization": f"Bearer {RENDER_API_KEY}",
    "Content-Type": "application/json"
}

# List all services
response = requests.get(
    "https://api.render.com/v1/services",
    headers=headers
)
print(response.json())
```

### Security Configuration

**Create `.env.production` (NOT committed to Git):**
```env
# Production API Key
API_KEY=sk_prod_SECURE_RANDOM_STRING_HERE

# Optional: Add to Render Environment
ALLOWED_ORIGINS=https://yourfrontend.com,https://app.yoursite.com
RATE_LIMIT_PER_MINUTE=100
LOG_LEVEL=INFO
```

**Update Render Environment Variables:**
```
API_KEY=sk_prod_SECURE_RANDOM_STRING_HERE
ALLOWED_ORIGINS=https://yourfrontend.com
RATE_LIMIT_PER_MINUTE=100
LOG_LEVEL=INFO
```

---

## 🧪 Testing the API

### Health Check
```bash
curl https://your-service.onrender.com/health
```

**Expected Response:**
```json
{
  "status": "ok"
}
```

### Voice Detection Test

**Prepare Test Audio:**
```bash
# Create a test WAV file (or use existing)
# Convert to Base64
base64 test_audio.wav > audio_base64.txt
```

**API Request:**
```bash
curl -X POST "https://your-service.onrender.com/api/voice-detection" \
  -H "x-api-key: sk_prod_YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "language": "en",
    "audioFormat": "wav",
    "audioBase64": "UklGRiQAAABXQVZFZm10..."
  }'
```

**Expected Response:**
```json
{
  "classification": "HUMAN",
  "confidenceScore": 0.87,
  "explanation": "Analysis based on MFCC Texture, Delta, and Spectral Centroid."
}
```

### Python Test Script

Create `test_api.py`:
```python
import requests
import base64
import json

# Configuration
API_URL = "https://your-service.onrender.com/api/voice-detection"
API_KEY = "sk_prod_YOUR_API_KEY"

# Load audio file
with open("test_audio.wav", "rb") as f:
    audio_bytes = f.read()
    audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')

# API Request
payload = {
    "language": "en",
    "audioFormat": "wav",
    "audioBase64": audio_base64
}

headers = {
    "x-api-key": API_KEY,
    "Content-Type": "application/json"
}

response = requests.post(API_URL, json=payload, headers=headers)

# Print results
print(f"Status Code: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")
```

Run test:
```bash
python test_api.py
```

---

## 🔒 Security Best Practices

### 1. Generate Strong API Keys
```python
import secrets
import string

def generate_api_key(prefix="sk_prod", length=32):
    """Generate cryptographically secure API key"""
    alphabet = string.ascii_letters + string.digits
    random_part = ''.join(secrets.choice(alphabet) for _ in range(length))
    return f"{prefix}_{random_part}"

# Generate multiple keys for different environments
print("Development:", generate_api_key("sk_dev"))
print("Staging:", generate_api_key("sk_stg"))
print("Production:", generate_api_key("sk_prod"))
```

### 2. Implement Rate Limiting

Add to `requirements.txt`:
```
slowapi
```

Update `api.py`:
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/api/voice-detection")
@limiter.limit("10/minute")  # 10 requests per minute per IP
def detect_voice(req: AudioRequest, x_api_key: str = Header(None)):
    # ... existing code
```

### 3. Configure CORS Properly

Update `api.py`:
```python
# Development
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  # Don't use ["*"] in production!
    allow_credentials=True,
    allow_methods=["POST", "GET", "HEAD"],
    allow_headers=["*"],
)
```

Render Environment:
```
ALLOWED_ORIGINS=https://yourfrontend.com,https://app.yoursite.com
```

### 4. Add Request Logging

```python
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.post("/api/voice-detection")
def detect_voice(req: AudioRequest, x_api_key: str = Header(None)):
    start_time = datetime.now()
    
    # ... existing code ...
    
    duration = (datetime.now() - start_time).total_seconds()
    logger.info(f"Request processed in {duration:.2f}s - Classification: {label}")
    
    return response
```

### 5. Rotate API Keys Regularly

Create `rotate_keys.py`:
```python
import secrets
from datetime import datetime

def rotate_api_key():
    """Generate new API key with timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d")
    new_key = f"sk_prod_{timestamp}_{secrets.token_urlsafe(24)}"
    
    print("=" * 60)
    print("NEW API KEY GENERATED")
    print("=" * 60)
    print(f"Key: {new_key}")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nACTIONS REQUIRED:")
    print("1. Update Render Environment Variable: API_KEY")
    print("2. Notify all API consumers")
    print("3. Set old key deprecation date (30 days)")
    print("4. Store in secure password manager")
    print("=" * 60)
    
    return new_key

if __name__ == "__main__":
    rotate_api_key()
```

---

## 🐛 Troubleshooting

### Common Issues

#### Issue 1: Model File Not Found
```
Error: [Errno 2] No such file or directory: 'voice_auth_model.pkl'
```

**Solutions:**
1. Ensure model files are committed to Git
2. Check file paths in `api.py`
3. Verify Render build logs show model files copied
4. Use absolute paths: `/app/voice_auth_model.pkl`

#### Issue 2: API Key Not Working
```
Error: {"detail": "Invalid API key"}
```

**Solutions:**
1. Verify environment variable set in Render: `API_KEY`
2. Check spelling: must be `API_KEY` not `API_SECRET`
3. Ensure no quotes in Render env var: ✅ `sk_prod_xxx` ❌ `"sk_prod_xxx"`
4. Test with curl: `curl -H "x-api-key: YOUR_KEY" ...`

#### Issue 3: Import Errors
```
Error: ModuleNotFoundError: No module named 'librosa'
```

**Solutions:**
1. Verify `requirements.txt` is complete
2. Check Python version compatibility (3.9-3.11)
3. Add system dependencies in Render:
   ```bash
   # Add to build command
   apt-get update && apt-get install -y libsndfile1 ffmpeg
   ```

#### Issue 4: Port Binding Error
```
Error: Address already in use
```

**Solutions:**
1. Ensure start command uses `$PORT`: `--port $PORT`
2. Don't hardcode port in code
3. Render automatically assigns port via `$PORT` env var

#### Issue 5: Memory Errors
```
Error: MemoryError during model inference
```

**Solutions:**
1. Upgrade Render plan (free tier has 512MB RAM)
2. Optimize model: reduce features, use quantization
3. Implement audio chunking for large files
4. Add memory monitoring

### Debug Mode

Enable debug logging in `api.py`:
```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.post("/api/voice-detection")
def detect_voice(...):
    logger.debug(f"Received request: {req.language}, {req.audioFormat}")
    logger.debug(f"Audio size: {len(req.audioBase64)} bytes")
    # ... rest of code
```

View logs in Render Dashboard → **Logs** tab

---

## 📊 Monitoring & Maintenance

### Health Monitoring with UptimeRobot

1. Sign up at https://uptimerobot.com (free)
2. Add monitor:
   - **Type**: HTTP(s)
   - **URL**: `https://your-service.onrender.com/health`
   - **Interval**: 5 minutes
   - **Alert**: Email when down

### Render Dashboard Metrics

Monitor in Render Dashboard:
- **CPU Usage**: Should be < 50% average
- **Memory**: Should be < 80% of allocated
- **Response Time**: Track P50, P95, P99
- **Request Count**: Monitor traffic patterns

### Log Analysis

Create `analyze_logs.py`:
```python
import re
from collections import Counter

def analyze_render_logs(log_file):
    """Analyze Render logs for patterns"""
    with open(log_file) as f:
        logs = f.read()
    
    # Extract classifications
    classifications = re.findall(r'Classification: (\w+)', logs)
    
    # Count occurrences
    stats = Counter(classifications)
    
    print("Classification Statistics:")
    print(f"  HUMAN: {stats['HUMAN']}")
    print(f"  AI_GENERATED: {stats['AI_GENERATED']}")
    print(f"  Total Requests: {sum(stats.values())}")

# Download logs from Render, then run:
# analyze_render_logs("render_logs.txt")
```

### Performance Optimization

**Add Response Caching:**
```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=128)
def cached_inference(audio_hash: str):
    """Cache results for identical audio files"""
    # ... inference logic
    pass

@app.post("/api/voice-detection")
def detect_voice(...):
    # Generate hash of audio
    audio_hash = hashlib.sha256(audio_bytes).hexdigest()
    
    # Check cache
    result = cached_inference(audio_hash)
    # ...
```

### Backup Strategy

**Weekly Model Backups:**
```bash
# Add to cron job or GitHub Actions
#!/bin/bash
DATE=$(date +%Y%m%d)
scp render:/app/voice_auth_model.pkl ./backups/model_$DATE.pkl
```

---

## 📚 Additional Resources

### Official Documentation
- **Render**: https://render.com/docs
- **FastAPI**: https://fastapi.tiangolo.com
- **Librosa**: https://librosa.org/doc/latest/
- **Scikit-learn**: https://scikit-learn.org

### Useful Tools
- **API Testing**: Postman, Insomnia, curl
- **Monitoring**: UptimeRobot, Pingdom, New Relic
- **CI/CD**: GitHub Actions, GitLab CI
- **Secret Management**: 1Password, AWS Secrets Manager

### Sample Projects
- FastAPI on Render: https://github.com/render-examples/fastapi
- ML API Deployment: https://github.com/render-examples/ml-api

---

## 📝 Deployment Checklist

Use this before going to production:

- [ ] ✅ Code tested locally
- [ ] ✅ All dependencies in `requirements.txt`
- [ ] ✅ Model files accessible (`voice_auth_model.pkl`, `scaler.pkl`)
- [ ] ✅ `.env` file created locally (not committed)
- [ ] ✅ `.gitignore` configured properly
- [ ] ✅ Repository pushed to GitHub
- [ ] ✅ Render service created and connected
- [ ] ✅ Build command configured: `pip install -r requirements.txt`
- [ ] ✅ Start command configured: `uvicorn api:app --host 0.0.0.0 --port $PORT`
- [ ] ✅ `API_KEY` environment variable set in Render
- [ ] ✅ Strong API key generated (32+ characters)
- [ ] ✅ Health check endpoint working: `/health`
- [ ] ✅ CORS configured with actual frontend URL
- [ ] ✅ Rate limiting implemented
- [ ] ✅ API tested with real audio samples
- [ ] ✅ Error handling tested (invalid key, bad audio, etc.)
- [ ] ✅ Logs monitored in Render dashboard
- [ ] ✅ Uptime monitoring configured (UptimeRobot)
- [ ] ✅ API documentation updated
- [ ] ✅ Client SDK/integration tested
- [ ] ✅ Backup strategy in place
- [ ] ✅ API key rotation schedule planned
- [ ] ✅ Team trained on API usage

---

## 🤝 Support

**Issues?**
- Check [Troubleshooting](#troubleshooting) section
- Review Render logs: Dashboard → Logs
- Open GitHub issue: [Project Issues](https://github.com/your-username/voice-ai-detector/issues)

**Questions?**
- Render Support: https://render.com/support
- FastAPI Discord: https://discord.com/invite/VQjSZaeJmf

---

## 📄 License

MIT License - See LICENSE file for details

---

**Last Updated**: February 2026  
**Maintained By**: ChainAim Technologies  
**Version**: 1.0.0
