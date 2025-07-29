# backend.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Set frontend URL here for prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TextPayload(BaseModel):
    text: str

@app.post("/process_receipt")
async def process_text(payload: TextPayload):
    print("\n[✅ CLEANED TEXT RECEIVED FROM FRONTEND]\n")
    print(payload.text)
    return {"received": payload.text[:300] + "..."}

# To run backend:
# uvicorn backend:app --reload --port 8000
