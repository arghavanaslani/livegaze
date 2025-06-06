import os
STIMULI_UPLOAD_PATH = 'static/artworks/'
DB_TYPE = 'postgresql+psycopg2'
DB_NAME = 'livegaze'
DB_HOST = 'localhost'
DB_USER = 'testuser'
DB_PORT = 5432
DB_PASSWORD = 'testPassword'
SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL",DB_TYPE+"://"+DB_USER+":"+DB_PASSWORD+"@"+DB_HOST+":"+str(DB_PORT)+"/"+DB_NAME)
SECRET_KEY="powerful secretkey"
WTF_CSRF_SECRET_KEY="a csrf secret key"
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
YOUTUBE_API_KEY = "EXAMPLE_YOUTUBE_KEY"