import os
import psycopg2
from fastapi import FastAPI, File, UploadFile, HTTPException, Body
from fastapi.responses import JSONResponse
import PyPDF2
import logging
import requests

app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
DATABASE_URL = os.getenv("DATABASE_URL")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


def get_db_connection():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except psycopg2.OperationalError as e:
        logger.error(f"Error connecting to the database: {e}")
        raise HTTPException(status_code=500, detail="Database connection error")


def extract_text_from_pdf(pdf_file):
    try:
        with open(pdf_file, "rb") as f:
            pdf_reader = PyPDF2.PdfReader(f)
            num_pages = len(pdf_reader.pages)
            text = ""
            for page_num in range(num_pages):
                page_object = pdf_reader.pages[page_num]
                text += page_object.extract_text()
        return text
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {e}")
        raise HTTPException(status_code=500, detail="Error extracting text from PDF")


@app.post("/upload_pdf")
async def upload_pdf(pdf_file: UploadFile = File(...)):
    local_pdf_path = f"uploaded_{pdf_file.filename}"
    try:
        # Save the PDF file locally
        with open(local_pdf_path, "wb") as f:
            f.write(pdf_file.file.read())

        # Extract text from the PDF
        extracted_text = extract_text_from_pdf(local_pdf_path)

        # Store extracted text in PostgreSQL
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
        # Clean up local file
        if os.path.exists(local_pdf_path):
            os.remove(local_pdf_path)


@app.post("/ask_question")
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

        # Call the Gemini API with the question and extracted text
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
        headers = {"Content-Type": "application/json"}
        data = {
            "contents": [
                {"parts": [{"text": f"Question: {question}\n\nText: {extracted_text}"}]}
            ]
        }

        response = requests.post(url, headers=headers, json=data)

        if response.status_code != 200:
            logger.error(
                f"Error from Gemini API: {response.status_code} - {response.text}"
            )
            raise HTTPException(
                status_code=response.status_code, detail="Error from Gemini API"
            )

        # Log the full response for debugging purposes
        response_json = response.json()
        logger.info(f"Response from Gemini API: {response_json}")

        # Check the actual structure of the response JSON
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

        return JSONResponse(content={"answer": answer})
    except Exception as e:
        logger.error(f"Error processing question: {e}")
        raise HTTPException(status_code=500, detail="Error processing question")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
