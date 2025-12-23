import os
from dotenv import load_dotenv

load_dotenv('config.env')


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://user:password@db_user:5432/user_db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'my_secret_key')
    # Adicione esta linha:
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')