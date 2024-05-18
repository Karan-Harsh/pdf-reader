import psycopg2
import logging
from fastapi import HTTPException
from app.core.config import DATABASE_URL

logger = logging.getLogger(__name__)


def get_db_connection():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except psycopg2.OperationalError as e:
        logger.error(f"Error connecting to the database: {e}")
        raise HTTPException(status_code=500, detail="Database connection error")
