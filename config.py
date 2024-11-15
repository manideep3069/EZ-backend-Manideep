import os

class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///file_sharing.db'
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your_jwt_secret_key')