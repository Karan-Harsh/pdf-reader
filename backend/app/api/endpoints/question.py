from fastapi import APIRouter, HTTPException, Body
from fastapi.responses import JSONResponse
from app.db.connection import get_db_connection
from app.services.gemini_api import call_gemini_api
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/ask")
async def ask_question(request_data: dict = Body(...)):
    try:
        question = request_data.get("question")
        file_name = request_data.get("file_name")

        if not question or not file_name:
            raise HTTPException(status_code=400, detail="Missing required fields")

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT extracted_text FROM pdf_texts WHERE file_name = %s", (file_name,)
        )
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        if not result:
            raise HTTPException(status_code=404, detail="PDF not found")

        extracted_text = result[0]
        answer = call_gemini_api(question, extracted_text)

        return JSONResponse(content={"answer": answer})
    except Exception as e:
        logger.error(f"Error processing question: {e}")
        raise HTTPException(status_code=500, detail="Error processing question")
