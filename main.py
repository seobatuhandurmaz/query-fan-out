class KeywordInput(BaseModel):
    keyword: str
    language: str = "Türkçe"

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
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Sen bir SEO uzmanısın ve Query Fan Out analizinde uzmansın."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )

        content = completion.choices[0].message.content
        content = content.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        return json.loads(content)

    except Exception as e:
        return {"error": str(e)}
