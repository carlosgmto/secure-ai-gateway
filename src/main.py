from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx

app = FastAPI(title="Secure AI Gateway", version="0.1.0")

# CONFIG (Moveremos esto a variables de entorno luego)
RPI_URL = "http://xurly.local:11434/api/generate" # <--- CAMBIA POR TU IP DE LA RPi
MODEL_NAME = "tinyllama"

# Definimos qué esperamos recibir (Validación estricta)
class PromptRequest(BaseModel):
    prompt: str

@app.post("/v1/chat")
async def chat_endpoint(request: PromptRequest):
    """
    Endpoint asíncrono que hace de Proxy hacia la RPi.
    """
    payload = {
        "model": MODEL_NAME,
        "prompt": request.prompt,
        "stream": False
    }
    async with httpx.AsyncClient() as client:
        try:
            print(f"📡 Enviando a RPi: {request.prompt}")
            response = await client.post(RPI_URL, json=payload, timeout=300.0)
            response.raise_for_status()

            data = response.json()
            return {"response": data.get("response")}

        except httpx.ConnectError:
            raise HTTPException(status_code=503, detail="La RPi está apagada o inaccesible")
        except httpx.TimeoutException:
            raise HTTPException(status_code=504, detail="El modelo tardó demasiado (Timeout)")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "operational", "mode": "development"}