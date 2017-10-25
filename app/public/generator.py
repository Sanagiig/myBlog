import random
import string
import hashlib
from random import seed,randint
from app.models import Permission,Role
from app import db
import forgery_py
def roles_generator():
    roles = {
        'User':(Permission['PUT_PC']|
                Permission['FOLLOW']|
                Permission['COMMENT']|
                Permission['WRITE_ARTICLES']),
        'Moderator':(
                Permission['PUT_PC']|
                Permission['FOLLOW']|
                Permission['COMMENT']|
                Permission['WRITE_ARTICLES']|
                Permission['MODERATE_COMMENTS']),
        'Administrator':0xff
    }
    for r,p in roles.items():
        role = Role(name=r,permission=p)
        db.session.add(role)
    db.session.commit()

def userinfo_generator(count=100):
    from app.models import UserInfo
    seed()
    for i in range(count):
        email=forgery_py.internet.email_address()
        u = UserInfo(email='fk' +str(i) + email,
                     nick_name = forgery_py.internet.user_name()+str(i),
                     password='123',
                     name=forgery_py.name.full_name(),
                     motto=forgery_py.lorem_ipsum.sentence()[:-110],
                     member_since=forgery_py.date.date(True),
                     last_seen=forgery_py.date.date(True),
                     profile_img=gravatar_generator(email))
        db.session.add(u)
        try:
            db.session.commit()
        except Exception as e :
            print('生成用户信息时出错 ！')
            print(e)
            db.session.rollback()

def categories_generator(count=10):
    from app.models import Category
    from random import seed
    seed()
    for i in range(count):
        c = Category(name=forgery_py.internet.user_name(),
                     created_time=forgery_py.date.date(True),)
        db.session.add(c)
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()

def tags_generator(count=10):
    from app.models import Tag
    from random import seed
    seed()
    for i in range(count):
        t = Tag(name=forgery_py.internet.user_name(),
                     created_time=forgery_py.date.date(True),)
        db.session.add(t)
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()

def article_generator(count=100):
    from app.models import Article_Status,UserInfo,Article
    from random import seed,randint
    seed()
    total_u = UserInfo.query.count()
    for i in range(count):
        offset = randint(0,total_u -1)
        u = UserInfo.query.offset(offset).first()
        status = 's' + str(randint(1,4))
        a = Article(
                title=forgery_py.internet.user_name(),
                description=forgery_py.lorem_ipsum.sentence(),
                content=forgery_py.lorem_ipsum.sentence(),
                status=Article_Status[status],
                author=u,
                read_num = randint(0,100),
                created_time=forgery_py.date.date(True),
                release_time=forgery_py.date.date(True),)
        db.session.add(a)
        try:
            db.session.commit()
        except Exception as e:
            print(e)
            db.session.rollback()

    #为文章添加标签和分类
    from app.models import Tag,Category
    t_count=Tag.query.count()
    c_count=Category.query.count()
    a_count=Article.query.count()
    for i in range(100):
        a=Article.query.offset(randint(0,a_count-1)).first()
        t=Tag.query.offset(randint(0,t_count-1)).first()
        c=Category.query.offset(randint(0,c_count-1)).first()
        t.article.append(a)
        c.article.append(a)
        db.session.add(t)
        db.session.add(c)
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()

def comment_generator(count=1000):
    from app.models import Article,Comment,UserInfo
    from app import db
    seed()
    art_num=Article.query.count()
    user_num=UserInfo.query.count()

    for i in range(count):
        article=Article.query.offset(randint(0,art_num-1)).first()
        c = Comment(author=UserInfo.query.offset(randint(0,user_num-1)).first(),
                    receiver_id = article.author_id,
                    article=article,
                    content=forgery_py.lorem_ipsum.sentence(),
                    created_time=forgery_py.date.date(True))
        db.session.add(c)
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()

def reply_generator(count=1000):
    from app.models import UserInfo,Comment,Reply
    seed()
    u_count = UserInfo.query.count()
    c_count = Comment.query.count()
    for i in range(count):
        comment=Comment.query.offset(randint(0,c_count-1)).first()
        r=Reply(author=UserInfo.query.offset(randint(0,u_count-1)).first(),
                comment=comment,
                receiver=comment.author,
                content=forgery_py.lorem_ipsum.sentence(),
                created_time=forgery_py.date.date(True),)
        db.session.add(r)
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()

def gravatar_generator(email,size=100,default='identicon',rating='g',secure=False):
    if secure == False:
        url = 'http://www.gravatar.com/avatar'
    else:
        url = 'https://secure.gravatar.com/avatar'
    hash = hashlib.md5(email.encode('utf-8')).hexdigest()
    return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating)

def code_generator(count=4):
    code = ''
    for i in range(count):
        code += random.choice(string.ascii_lowercase)
    return code


def generate_fake():
    from  app.models import UserInfo,Role,Category,Tag,\
        Article,Comment,Reply,\
        Article_PutPorC,Comment_PutPorC,Reply_PutPorC

    import sys
    print('数据正在生成，请骚等 ... ')
    if Role.query.count() <3:
        roles_generator()
    print('角色已生成完毕...')
    if UserInfo.query.count() < 50:
        userinfo_generator()
    print('用户已生成完毕...')
    if Category.query.count()<5:
        categories_generator()
    print('分类已生成完毕...')
    if Tag.query.count()<5:
        tags_generator()
    print('标签已生成完毕...')
    if Article.query.count()<50:
        article_generator()
    print('文章已生成完毕...')
    if Comment.query.count()<800:
        comment_generator()
    print('评论已生成完毕...')
    if Reply.query.count()<800:
        reply_generator()
    print('所有用户数据已经生产完毕，请放心使用 ！')
    sys.exit(0)