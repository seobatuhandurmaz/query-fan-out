from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
import os

# OpenAI istemcisi (v1 client yapısı)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# FastAPI uygulaması
app = FastAPI()

# CORS – Tüm varyasyonlar eklendi
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://batuhandurmaz.com",
        "http://batuhandurmaz.com",
        "https://www.batuhandurmaz.com",
        "http://www.batuhandurmaz.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Girdi modeli
class KeywordInput(BaseModel):
    keyword: str

# Analyze endpoint
@app.post("/analyze")
async def analyze_keyword(data: KeywordInput):
    try:
        # Prompta uzman bağlamı verdik
        prompt = f"""
Sen, Google ve LLM'ler tarafından sıkça kullanılmakta olan Query Fan out ve Query Follow up konularında uzman bir araştırmacısın.

Kullanıcı tarafından sana verilen hedef kelimeyi analiz ederek, bu hedef kelime ile ilgili aşağıdaki çıktıları JSON formatında üret:

- Query Fan out sonuçları
- Query Follow up sonuçları
- Bu sonuçlara uygun entity'ler
- Bu sonuçlara uygun LSI kelimeler
- Bu sonuçlara uygun uzun kuyruk ve benzersiz sorular

Yanıtı sadece şu JSON formatında ver:

{{
  "fanOutQueries": [...],
  "followUpQueries": [...],
  "entities": [...],
  "lsiKeywords": [...],
  "longTailQuestions": [...]
}}

Kelime: {data.keyword}
"""

        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Sen bir SEO uzmanısın ve Query Fan Out analizinde uzmansın."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )

        # Dönüş metni ham JSON olacak şekilde alınır
        content = completion.choices[0].message.content
        return {"result": content}

    except Exception as e:
        return {"error": str(e)}
