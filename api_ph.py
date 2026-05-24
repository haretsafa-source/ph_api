from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import matplotlib.pyplot as plt
import io
import base64

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
# نموذج البيانات القادمة من Unity
class PHData(BaseModel):
    ph: float
    volume: float

# حساب التركيز
def calculate_concentration(ph, volume):
    h_concentration = 10 ** (-ph)
    concentration = h_concentration * volume
    return h_concentration, concentration

# تصنيف المحلول
def classify_solution(ph):
    if ph < 7:
        return "acid"
    elif ph > 7:
        return "base"
    else:
        return "neutrals"

# رسم بياني
def create_graph(ph, h_conc):
    x = np.linspace(0, 14, 100)
    y = 10 ** (-x)

    plt.figure()
    plt.plot(x, y, label="H+ curve")
    plt.scatter([ph], [h_conc], color='red', label="Your point")
    plt.xlabel("pH")
    plt.ylabel("[H+]")
    plt.legend()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()

    return img_base64


@app.post("/analyse")
def analyse(data: PHData):
    h_conc, conc = calculate_concentration(data.ph, data.volume)
    type_solution = classify_solution(data.ph)
    graph = create_graph(data.ph, h_conc)

    return {
        "type": type_solution,
        "h_concentration": h_conc,
        "concentration": conc,
        "graph": graph
    }