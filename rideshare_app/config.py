import os

class Config:
    # Secret key for session management
    SECRET_KEY = os.environ.get('SECRET_KEY', 'b94a2cb8f87f97d2c15650e92b8c0537')

    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'mysql+pymysql://root:Anilkumar%40ak%40567@localhost/rideshareapp')
    SQLALCHEMY_TRACK_MODIFICATIONS = False