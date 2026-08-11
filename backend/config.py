import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "swiftshop-production-secret-key-2026")
    PRODUCTS_CSV = os.path.join(os.path.dirname(os.path.dirname(__file__)), "products.csv")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    DEFAULT_PORT = int(os.getenv("PORT", 8080))
    DEBUG = os.getenv("FLASK_ENV") == "development"
