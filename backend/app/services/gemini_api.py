import requests
import logging
from fastapi import HTTPException
from app.core.config import GEMINI_API_KEY

logger = logging.getLogger(__name__)


def call_gemini_api(question, extracted_text):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [
            {"parts": [{"text": f"Question: {question}\n\nText: {extracted_text}"}]}
        ]
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code != 200:
        logger.error(f"Error from Gemini API: {response.status_code} - {response.text}")
        raise HTTPException(
            status_code=response.status_code, detail="Error from Gemini API"
        )

    response_json = response.json()
    logger.info(f"Response from Gemini API: {response_json}")

    if "candidates" in response_json and len(response_json["candidates"]) > 0:
        candidate = response_json["candidates"][0]
        if "content" in candidate and "parts" in candidate["content"]:
            parts = candidate["content"]["parts"]
            if len(parts) > 0 and "text" in parts[0]:
                answer = parts[0]["text"]
            else:
                answer = "No text found in the response parts"
        else:
            answer = "No content or parts found in the response"
    else:
        logger.error(f"Unexpected response structure: {response_json}")
        raise HTTPException(
            status_code=500, detail="Unexpected response structure from Gemini API"
        )

    return answer
