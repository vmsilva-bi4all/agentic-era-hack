import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

db_params = {
    "host": os.environ.get("DB_HOST"),
    "port": os.environ.get("DB_PORT"),
    "dbname": os.environ.get("DB_NAME"),
    "user": os.environ.get("DB_USER"),
    "password": os.environ.get("DB_PASSWORD"),
    "connect_timeout": 10
}

print(f"Attempting to connect to host: {db_params['host']}:{db_params['port']}...")

try:
    conn = psycopg2.connect(**db_params)
    print("Connection successful!")
    conn.close()
except Exception as e:
    print(f"Connection failed: {e}")
