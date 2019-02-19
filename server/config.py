import os
import datetime
from dotenv import load_dotenv

# Load our config variables from our .env file
basedir = os.path.abspath(os.path.dirname(__file__))
dotenv_path = os.path.join(basedir, '.env')
load_dotenv(dotenv_path)

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(days=1)
    JWT_REFRESH_TOKEN_EXPIRES = datetime.timedelta(days=1)
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @staticmethod
    def init_app(app):
        # Any other extra config steps?
        pass

class ProductionConfig(Config):
    """Production configuration"""
    ENV = 'production'
    REDIS_URL = os.environ.get('REDIS_PRODUCTION_URL')
    SQLALCHEMY_DATABASE_URI = os.environ.get('MYSQL_PRODUCTION_DATABASE_URI')

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    ENV = 'development'
    SQLALCHEMY_ECHO = True
    REDIS_URL = os.environ.get('REDIS_DEVELOPMENT_URL')
    SQLALCHEMY_DATABASE_URI = os.environ.get('MYSQL_DEVELOPMENT_DATABASE_URI')

class TestingConfig(Config):
    """Testing configuration (TODO)"""
    TESTING = True
    ENV = 'testing'

# Use this dictionary by importing this object
# and passing the key you want to the app's create_app,
# e.g:
#
# from config import config
# from app import create_app
# app = create_app(config['development'])
# app.run()
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig
}
