from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from app.services.pdf_extraction import extract_text_from_pdf
from app.db.connection import get_db_connection
import os
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/api/upload")
async def upload_pdf(pdf_file: UploadFile = File(...)):
    local_pdf_path = f"uploaded_{pdf_file.filename}"
    try:
        with open(local_pdf_path, "wb") as f:
            f.write(pdf_file.file.read())

        extracted_text = extract_text_from_pdf(local_pdf_path)

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO pdf_texts (file_name, extracted_text) VALUES (%s, %s)",
            (pdf_file.filename, extracted_text),
        )
        conn.commit()
        cursor.close()
        conn.close()

        return JSONResponse(
            content={"message": "PDF uploaded and text extracted successfully."}
        )
    except Exception as e:
        logger.error(f"Error processing PDF file: {e}")
        raise HTTPException(status_code=500, detail="Error processing PDF file")
    finally:
        if os.path.exists(local_pdf_path):
            os.remove(local_pdf_path)
