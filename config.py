import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
  VERSION = "1.4"
  DEBUG = os.environ.get('DEBUG', False)
  TESTING = os.environ.get('TESTING', False)
  CSRF_ENABLED = True
  SECRET_KEY = os.environ.get('CSRF_SECRET_KEY', 'you-shoul-really-change-this')
  DB_TYPE = os.environ.get('DB_TYPE', "postgresql")
  PORT = os.environ.get('PORT', "5000")
  HOST = os.environ.get('HOST', "0.0.0.0")
  ANIMAL = os.environ.get('ANIMAL', None)
  SQLALCHEMY_DATABASE_URI = ''.join(["postgresql+psycopg://" if DB_TYPE == "postgresql" else "mysql+pymysql://", os.environ['DB_USER'],":",os.environ['DB_PASSWORD'],"@",os.environ['DB_HOST'],":",os.environ['DB_PORT'],"/",os.environ['DB_NAME']])

