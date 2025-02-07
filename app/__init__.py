from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
import logging
from logging.handlers import RotatingFileHandler

# 创建全局 SQLAlchemy 实例
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # 配置数据库
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://finance_user:123456@localhost/finance_data'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # 添加host和port配置
    app.config['HOST'] = '0.0.0.0'  # 允许外部访问
    app.config['PORT'] = 5000  # 设置默认端口
    
    # 初始化数据库
    db.init_app(app)
    
    # 设置日志
    if not app.debug:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/finance.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Finance data startup')

    # 注册蓝图
    from app.routes import main
    app.register_blueprint(main)
    
    return app