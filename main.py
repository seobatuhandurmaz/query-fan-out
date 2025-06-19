from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
import os
import json

# OpenAI istemcisi
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# FastAPI uygulaması
app = FastAPI()

# CORS ayarı – tüm domain varyasyonları
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
    language: str = "Türkçe"  # Varsayılan dil

# Ana endpoint
@app.post("/analyze")
async def analyze_keyword(data: KeywordInput):
    try:
        prompt = f"""
Sen, Google ve LLM'ler tarafından sıkça kullanılmakta olan Query Fan out ve Query Follow up konularında uzman bir araştırmacısın.

Kullanıcı tarafından sana verilen hedef kelimeyi analiz edeceksin.
Lütfen tüm çıktıları {data.language} dilinde oluştur.

Çıktılar şunlar olacak:

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
            model="chatgpt-4o-latest",
            messages=[
                {"role": "system", "content": """Sen, Google ve LLM'ler tarafından sıkça kullanılmakta olan Query Fan out ve Query Follow up konularında uzmansın.
Kullanıcı tarafından sana verilen hedef kelimeyi analiz ederek, bu hedef kelime ile ilgili aşağıdaki çıktıları üreteceksin:

- Söz konusu kelime ile ilgili Query Fan out sonuçları
- Söz konusu kelime ile ilgili Query follow up sonuçları
- Bu sonuçlara uygun Entityler,
- Bu sonuçlara uygun LSI kelimeler
- Bu sonuçlara uygun uzun kuyruk ve benzersiz sorular

Tüm çıktı başlıklarını kullanıcı tarafından verilen anahtar kelime ile ilgili araştırma yapacak ve çıktı olarak vereceksin."""
        },
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )

        # OpenAI yanıtı
        content = completion.choices[0].message.content

        # Eğer yanıt içinde ```json veya ``` varsa temizle
        content = content.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()

        # JSON olarak parse edip gönder
        return json.loads(content)

    except Exception as e:
        # Hata durumunda geri dönüş
        raise HTTPException(status_code=500, detail=str(e))
