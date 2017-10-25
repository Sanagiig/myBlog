from flask import render_template,request,g,session,jsonify
from flask_login import current_user,login_required,login_user,logout_user
import re
import json
from datetime import datetime
from app.models import UserInfo
from app.auth import auth
from app.public.mail import send_mail
from app.public.check import check_email,check_password
from app.public.generator import code_generator,gravatar_generator
from app.models import  UserInfo
from app import db

@auth.route('/send_check_code',methods=['POST'])
def send_check_code():
    if request.method == 'POST':
        mial_template = 'mail/register'
        data = request.get_data().decode('utf-8')
        data = json.loads(data)
        opt = data['opt']
        email = data['email']
        result = False

        if opt  == 'request_email' and check_email(email):
            session['check_code'] = code_generator()
            send_mail(mial_template,receiver=email,
                      code=session['check_code'])
            result=True
        return jsonify({'result':result})

#注册
@auth.route('/register',methods=['POST'])
def register():
    if request.method == 'POST':
        data = request.get_data().decode('utf-8')
        data = json.loads(data)
        opt = data['opt']
        email = data['email']
        password = data['password']
        check_code = data['check_code']
        result = False

        if opt == 'register':
            if not check_email(email):
                result = 5
            elif not check_password(password):
                result = 4
            elif check_code != session['check_code']:
                result = 3
            elif UserInfo.query.filter_by(email=email).first():
                result = 2
            else:
                u = UserInfo(email=email,password=password,profile_img=gravatar_generator(email),
                             nick_name='第%d个用户'%(UserInfo.query.count()+1))
                db.session.add(u)
                try:
                    db.session.commit()
                except Exception:
                    session['info'] = '由于服务器数据库原因，注册失败 ！'
                else: #注册成功
                    result = 1

        return jsonify({'result':result})

#登录
@auth.route('/login',methods=['POST'])
def login():
    if request.method == 'POST':
        data = request.get_data().decode('utf-8')
        data = json.loads(data)
        email = data['email']
        password = data['password']
        result = False

        u = UserInfo.query.filter_by(email=email).first()
        if u and u.check_password(password):
            login_user(u)
            u.last_seen = datetime.now()
            result = True
            db.session.add(u)
            try:
                db.session.commit()
            except Exception:
                db.session.rollback()
        return jsonify({'result':result})


@auth.route('/logout',methods=['GET','POST'])
@login_required
def logout():
    result = False
    if request.method != 'POST' or current_user.is_anonymous:
        pass
    else:
        result = True
        logout_user()
    return jsonify({'result':result})