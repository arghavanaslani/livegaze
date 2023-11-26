UPLOAD_PATH = '/static/artworks/'
DB_TYPE = 'postgresql+psycopg2'
DB_NAME = 'livegaze'
DB_HOST = 'localhost'
DB_USER = 'testuser'
DB_PORT = 5432
DB_PASSWORD = 'testPassword'
SQLALCHEMY_DATABASE_URI = DB_TYPE+"://"+DB_USER+":"+DB_PASSWORD+"@"+DB_HOST+" "+str(DB_PORT)+"/"+DB_NAME