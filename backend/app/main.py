from fastapi import FastAPI
from app.api.endpoints import pdf, question
from app.core.logging import setup_logging
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

setup_logging()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(pdf.router, prefix="/pdf", tags=["pdf"])
app.include_router(question.router, prefix="/question", tags=["question"])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
