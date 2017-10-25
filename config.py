import os
from app.public.error import put_err
basedir = os.path.abspath(os.path.dirname(__file__))

class Config():
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    #如果设置为True，flask-sqlalchemy将跟踪对象的修改并发出信号。默认值是None，
    # 它支持跟踪，但是会发出警告，警告它在将来会被禁用。这需要额外的内存，如果不需要，应该禁用。
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True   #将其设为True时，每次请求结束后都会自动提交数据库中的变动。

    #邮件相关
    MAIL_SERVER = 'smtp.163.com'
    MAIL_PORT = 25
    MAIL_USE_TLS = False
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or put_err('MAIL_USERNAME NOT EXISTS!')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or put_err('MAIL_PASSWORD NOT EXISTS!')
    MAIL_SENDER = '落云飘雪<laiwenjunhhh@163.com>'
    MAIL_SUBJECT = '通知 from 落云飘雪'

    ARTICLE_PER_PAGE = 10
    COMMENT_PER_PAGE = 8
    REPLY_PER_PAGE = 10

class DevConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'dev_app.db')

class ProConfig(Config):
    # MYSQL_DATABASE_USER = 'root'
    # MYSQL_DATABASE_PASSWORD = '123'
    # MYSQL_DATABASE_DB = 'Myblog'
    # MYSQL_DATABASE_HOST = '192.168.8.136'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://lai:123@192.168.8.137/MyBlog_Flask'

config={
    'default':DevConfig,
    'product':ProConfig,
}

