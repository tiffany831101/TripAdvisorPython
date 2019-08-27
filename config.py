import os 
import redis
basedir = os.path.abspath(os.path.dirname(__file__))
class Config:
    SECRET_KEY = os.environ.get('SECREY_KEY') or 'hard to guess string'
    UPLOADED_PHOTOS_DEST = os.path.join(os.getcwd(),"app","static","images")
    MAX_CONTENT_LENTH= 2 *1024 * 1024
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    FLASKY_MAIL_SUBJECT_PREFIX = '[Flasky]'

    
    FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN')
    REDIS_HOST="localhost"
    REDIS_PORT= 6379

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    MAIL_SERVER = 'smtp@googlemail.com'
    MAIL_PORT =587
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:a828215362@localhost:3306/web_flask'
    # sqlalchemy.url = "mysql+mysqldb://root:a828215362@localhost:3306/alembic_demo?charset=utf8"

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI='mysql+pymysql://root:********@localhost:3306/web_flask'

config = {
    'development':DevelopmentConfig,
    'production':ProductionConfig,
    'default':DevelopmentConfig
}
