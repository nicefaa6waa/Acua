import httpx
import json
import logging
from app.config import settings

logging.basicConfig(level=logging.INFO)

MODEL_NAME = "gemini-pro"
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1/models/{MODEL_NAME}:generateContent"


async def generate_sustainability_analysis(address: str, satellite_data: dict) -> dict:

    prompt = f"""
    Aşağıdaki verilere göre sürdürülebilir tarım raporu oluştur:

    Adres: {address}
    NDVI (Bitki Örtüsü): {satellite_data['ndvi']}
    Toprak Nem Oranı: {satellite_data['soil_moisture']}%
    Ortalama Sıcaklık: {satellite_data['temperature_avg']}°C
    Yıllık Yağış: {satellite_data['precipitation']}mm
    Su Buharlaşma Miktarı: {satellite_data['evapotranspiration']}mm

    Rapor aşağıdaki alanları içermelidir:
    1.  Genel Durum Değerlendirmesi (Overall Assessment)
    2.  Güçlü Yönler (Strengths)
    3.  Zayıf Yönler ve Riskler (Weaknesses and Risks)
    4.  Sürdürülebilirlik Önerileri (Sustainability Recommendations)
        * Su Yönetimi (Water Management)
        * Toprak Sağlığı (Soil Health)
        * Bitki Seçimi ve Yönetimi (Crop Selection and Management)
        * İklim Değişikliğine Uyum (Climate Change Adaptation)
    5.  Veri Puanlarına Dayalı Kısa Analizler (Brief Analysis based on Data Points)

    Yanıtı yalnızca geçerli bir JSON formatında, yukarıdaki anahtarları kullanarak döndür. Başka hiçbir metin ekleme.
    """

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 1536,
            "response_mime_type": "application/json"
        }
    }

    params = {"key": settings.GEMINI_API_KEY}

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            logging.info(f"Gemini API isteği gönderiliyor: {GEMINI_API_URL}")
            response = await client.post(GEMINI_API_URL, params=params, json=payload)
            response.raise_for_status()

            logging.info(f"Gemini API'den yanıt alındı: Status {response.status_code}")
            raw_response = response.json()

            if "candidates" not in raw_response or not raw_response["candidates"]:
                 raise Exception("Gemini API yanıtında 'candidates' bulunamadı.")

            content = raw_response["candidates"][0]["content"]
            if "parts" not in content or not content["parts"]:
                 raise Exception("Gemini API yanıtında 'parts' bulunamadı.")

            gemini_text = content["parts"][0]["text"].strip()

            try:
                if gemini_text.startswith("```json"):
                    gemini_text = gemini_text.strip("```json").strip()
                elif gemini_text.startswith("```"):
                     gemini_text = gemini_text.strip("```").strip()

                gemini_json = json.loads(gemini_text)
                logging.info("Gemini yanıtı başarıyla JSON olarak ayrıştırıldı.")
                return gemini_json
            except json.JSONDecodeError as e:
                error_message = f"Gemini'den dönen metin geçerli bir JSON değil. Hata: {e}. Dönen Metin: '{gemini_text}'"
                logging.error(error_message)
                raise Exception(error_message)

        except httpx.HTTPStatusError as e:
            error_message = f"Gemini API HTTP hatası: {e.response.status_code} - {e.response.text}"
            logging.error(error_message)
            raise Exception(error_message) from e
        except httpx.RequestError as e:
            error_message = f"Gemini API'ye bağlanırken hata oluştu: {e}"
            logging.error(error_message)
            raise Exception(error_message) from e
        except Exception as e:
            logging.error(f"Beklenmedik bir hata oluştu: {e}", exc_info=True)
            raise