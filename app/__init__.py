from flask import Flask, render_template, session
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import config
import logging
from logging.handlers import RotatingFileHandler
from flask_wtf.csrf import CSRFProtect
import redis
from flask_uploads import UploadSet, configure_uploads, IMAGES

bootstrap = Bootstrap()
mail =Mail()
moment = Moment()
db = SQLAlchemy()

# csrf = CSRFProtect()

redis_store=None

photos= UploadSet('photos', IMAGES)

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view= 'auth.login'
login_manager.login_message =u'請登入才能瀏覽頁面'

# logging.error() #類似print()，錯誤級別
# logging.warn() #警告級別
# logging.info() #消息提示級別
# loggin.debug() #調適級別

# 設置日誌的紀錄等級
logging.basicConfig(level= logging.DEBUG) #調試debug級
#創建日誌記錄器，指名日誌保存的路徑、每個日誌文件的最大大小、保存
file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024*1024*100, backupCount=10)
# 創建日誌記錄的格式
formatter = logging.Formatter('%(levelname)s %(filename)s: %(lineno)d%(message)s')
# 為剛剛創建的日誌紀錄器設置日誌紀錄格式
file_log_handler.setFormatter(formatter)
# 為全局的日誌工具對象添加日記錄器
logging.getLogger().addHandler(file_log_handler)

def create_app(config_name):
    app=Flask(__name__)
    
    conf = config.get(config_name)
    app.config.from_object(conf)
    
    config[config_name].init_app(app)
    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    # 為flask補充csrf防護
    CSRFProtect(app)
    
    configure_uploads(app, photos)
    # 初始化redis 工具
    global redis_store
    redis_store = redis.StrictRedis(host=conf.REDIS_HOST, port = conf.REDIS_PORT)
    

    
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint,url_prefix='/auth')
    from .api_1 import api as api_blueprint
    app.register_blueprint(api_blueprint,url_prefix='/api')
    return app