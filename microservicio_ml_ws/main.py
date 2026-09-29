import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.notify import router as notify_router
import joblib
import os
from pathlib import Path

# Load or create a placeholder ML model
MODEL_PATH = Path(__file__).parent / "model.pkl"
if not MODEL_PATH.exists():
    # Create an empty placeholder file so that imports succeed
    MODEL_PATH.touch()

app = FastAPI()

# CORS: la autenticación va por header Authorization (Bearer), no por cookies,
# así que no se necesita allow_credentials=True — combinarlo con origin "*"
# es además inválido según el spec de CORS.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(notify_router)

@app.get("/", tags=["Health"])
async def health_check():
    return {"status": "OK", "service": "ML WS"}

if __name__ == "__main__":
    # Run the service on port 8001
    uvicorn.run("main:app", host="0.0.0.0", port=8011, reload=False)