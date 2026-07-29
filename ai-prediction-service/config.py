import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "monitoring_db")
DB_USER = os.getenv("DB_USER", "monitoring")
DB_PASSWORD = os.getenv("DB_PASSWORD", "monitoring")

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
WINDOW_SECONDS = int(os.getenv("WINDOW_SECONDS", "60"))

MODEL_DIR = "models"
ISOLATION_FOREST_MODEL_PATH = f"{MODEL_DIR}/isolation_forest.joblib"
SCALER_PATH = f"{MODEL_DIR}/scaler.joblib"

DB_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"