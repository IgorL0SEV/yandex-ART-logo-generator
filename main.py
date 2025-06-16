import os
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()

IAM_TOKEN = os.getenv("IAM_TOKEN")
CATALOG_ID = os.getenv("CATALOG_ID")

