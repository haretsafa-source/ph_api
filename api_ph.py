from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import base64
import numpy as np
import matplotlib.pyplot as plt
import io

app = FastAPI()

# =========================
# CORS (ضروري لـ WebGL)
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # في الإنتاج خليه دومين Unity فقط
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# routes
@app.post("/analyse")
async def analyse():
    return {"message": "ok"}

# =========================
# API KEY
# =========================
API_KEY = "ChangeThisKey123"

# =========================
# Request Model
# =========================
class RequestData(BaseModel):
    ph: float
    volume: float

# =========================
# Analyse Endpoint
# =========================
@app.post("/analyse")
def analyse(
    data: RequestData,
    x_api_key: str = Header(None)
):
    # -------------------------
    # Check API Key
    # -------------------------
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")

    ph = data.ph
    volume = data.volume

    # =========================
    # Example Physics/Chemistry Logic
    # =========================
    h_concentration = 10 ** (-ph)
    concentration = h_concentration * volume

    # =========================
    # Create Graph
    # =========================
    x = np.linspace(0, 14, 100)
    y = 10 ** (-x)

    plt.figure()
    plt.plot(x, y)
    plt.title("pH Curve")
    plt.xlabel("pH")
    plt.ylabel("[H+]")

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)

    img_base64 = base64.b64encode(buf.read()).decode("utf-8")
    plt.close()

    # =========================
    # Response
    # =========================
    return {
        "type": "acid" if ph < 7 else "basic",
        "concentration": concentration,
        "h_concentration": h_concentration,
        "graph": img_base64
    }
# =========================
# Test GET (اختياري فقط)
# =========================
@app.get("/")
def home():
    return {"status": "API is running"}

