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
    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(minutes=60)
    JWT_REFRESH_TOKEN_EXPIRES = datetime.timedelta(days=1)
    # Configures application to store JWTs in cookies
    JWT_TOKEN_LOCATION = ['cookies']
    # Set the cookie paths, so that you are only sending your access token
    # cookie to the access endpoints, and only sending your refresh token
    # to the refresh endpoint. Technically this is optional, but it is in
    # our best interest to not send additional cookies in the request if
    # they aren't needed
    JWT_ACCESS_COOKIE_PATH = ['/api/', '/auth/']
    JWT_REFRESH_COOKIE_PATH = '/auth/refresh'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @staticmethod
    def init_app(app):
        # Any other extra config steps?
        pass

class ProductionConfig(Config):
    """Production configuration"""
    ENV = 'production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('MYSQL_PRODUCTION_DATABASE_URI')
    # Only allow JWT cookies to be sent over https
    JWT_COOKIE_SECURE = True
    JWT_COOKIE_CSRF_PROTECT = True

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    ENV = 'development'
    # When hitting the datase, print out its queries in console
    # (may not be necessary)
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('MYSQL_DEVELOPMENT_DATABASE_URI')
    # In dvelopment we dont need JWT cookies to be sent over https
    JWT_COOKIE_SECURE = False
    JWT_COOKIE_CSRF_PROTECT = False

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
