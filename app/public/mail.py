from threading import Thread
from flask_mail import Message
from flask import render_template
from app import app
from app import mail

#发送邮件的征文
def send_mail(template,receiver,**kwargs):
    msg = Message(app.config['MAIL_SUBJECT'],sender=app.config['MAIL_SENDER'],recipients=[receiver])
    msg.html = render_template(template +'.html',**kwargs)
    msg.body = render_template(template +'.txt',**kwargs)

    t = Thread(target=async_send_mail,args=[app,msg])
    t.start()

#当然是异步发送啦
def async_send_mail(app,msg):
    with app.app_context():
        mail.send(msg)