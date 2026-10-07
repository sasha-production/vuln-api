import os

SECRET_KEY = "super-secret-jwt-key-do-not-change-1234567890"

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")

WEATHER_API_KEY = "sk_live_51H8xQ2eZvKYlo2C9pQ3rF7tN1bX4mW6dS8gA0jL5cV2uB3nM"
INTERNAL_ADMIN_TOKEN = "admin-token-please-rotate-me"

ACCESS_TOKEN_EXPIRE_MINUTES = 60
ALGORITHM = "HS256"
UPLOAD_DIR = "/tmp/uploads"
ALLOWED_HOSTS = ["*"]
