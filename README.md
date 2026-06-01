# ViraNova — Predict Influence. Generate Virality.

ViraNova is a premium AI-powered platform built for the creator economy, submitted for the **Ratefluencer AI Hackathon 2026 Grand Challenge**.

It includes two primary tracks:
- **Track 01 — Influencer Intelligence Engine**: Deep machine learning models (XGBoost, LightGBM, Neural Networks) and Pinecone RAG for brand matching, scoring creator authenticity, growth forecasts, and calculating the master **Ratefluencer Score™**.
- **Track 02 — Viral Reel Creator Agent**: Multi-agent orchestration (Claude, Groq, LangGraph, CrewAI) for trend discovery, script building, video/voice overlays (ElevenLabs, Runway AI), captions, and virality prediction models.

## Folder Structure

```text
viranava/
├── Dockerfile
├── docker-compose.yml
├── README.md
├── frontend/                    # Web Interface
│   ├── index.html               # Main landing page
│   ├── dashboard.html           # App dashboard placeholder
│   └── assets/
│       ├── css/
│       │   └── style.css        # Premium stylesheets (with pixel-accurate gradients)
│       └── js/
│           └── script.js        # Global interactive animations
│
└── backend/                     # Python FastAPI API
    ├── main.py                  # API entry point
    ├── requirements.txt         # Dependencies
    ├── .env                     # Configuration keys
    ├── .env.example             # Config template
    ├── api/                     # Route controllers
    │   ├── routes/
    │   │   ├── influencer.py    # Track 01 endpoints
    │   │   ├── content.py       # Track 02 endpoints
    │   │   ├── trends.py        # Trend endpoints
    │   │   └── agent.py         # Autonomous agent routing
    │   └── middleware/
    ├── core/
    │   └── config.py            # Setting configurations
    ├── services/                # Stub architectures
    │   ├── track01_intelligence/
    │   ├── track02_content/
    │   ├── ai_providers/
    │   ├── ml_models/
    │   └── vector_db/
    └── agent/                   # LangGraph agent definitions
```

## Setup & Running Locally

### Prerequisites
- Python 3.10+
- Node.js (or any static server)
- Docker (optional)

### 1. Launching the Frontend
Start a local HTTP server in the `frontend` folder:
```bash
cd frontend
python3 -m http.server 8000
```
Open `http://localhost:8000/` in your browser.

### 2. Launching the Backend
Install dependencies and run FastAPI via Uvicorn:
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```
API Documentation will be available at `http://localhost:8000/docs`.

### 3. Launching with Docker Compose
To spin up both frontend and backend automatically:
```bash
docker-compose up --build
```
The Nginx frontend container will be live at `http://localhost/` and the backend container at `http://localhost:8000/`.
