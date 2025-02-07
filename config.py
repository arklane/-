class Config:
    # 确保使用正确的数据库连接URI
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://finance_user:123456@localhost/finance_data'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_POOL_SIZE = 10
    SQLALCHEMY_POOL_TIMEOUT = 30
    SQLALCHEMY_POOL_RECYCLE = 1800
    
    # 添加错误处理配置
    PROPAGATE_EXCEPTIONS = True
    
    SECRET_KEY = 'dev'
    
    # 更新 CSV 文件路径配置
    CSV_FILES = {
        'stock': 'data/股票型.csv',
        'mixed': 'data/混合型.csv',
        'bond': 'data/债券型.csv',
        'index': 'data/指数型.csv',
        'enhanced': 'data/指数增强型.csv'  # 添加指数增强型基金
    }