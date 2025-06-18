from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import openai
import json

# OpenAI API anahtarını ortam değişkeninden al
openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

# Tüm domain varyasyonlarını tanımla (www ile olanlar dahil)
origins = [
    "https://batuhandurmaz.com",
    "http://batuhandurmaz.com",
    "https://www.batuhandurmaz.com",
    "http://www.batuhandurmaz.com"
]

# CORS middleware: OPTIONS dahil tüm istek türlerine izin ver
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # ← POST ve OPTIONS dahil tüm methodlara izin verildi
    allow_headers=["*"],
)

# Anahtar kelime input modeli
class KeywordRequest(BaseModel):
    keyword: str

@app.post("/analyze")
async def analyze(request: Request, body: KeywordRequest):
    # Origin güvenlik kontrolü
    origin = request.headers.get("origin")
    if origin not in origins:
        raise HTTPException(status_code=403, detail="Forbidden origin")

    prompt = (
        f"Analyze the keyword '{body.keyword}' and provide JSON with keys: "
        "fanOutQueries, followUpQueries, entities, lsiKeywords, longTailQuestions"
    )

    try:
        completion = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert in query fan-out and follow-up analysis."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )

        # Yanıtı JSON formatında döndür
        return json.loads(completion.choices[0].message.content)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
