from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import AnonymousUserMixin,UserMixin
from app import db
from app import login_manager
from datetime import datetime
gender_choice = dict(
        male= '男',
        female= '女',
        unknown='未知',
    )
Permission = dict(
    PUT_PC = 0x01,
    FOLLOW = 0x02,
    COMMENT = 0x04,
    WRITE_ARTICLES = 0x08,
    MODERATE_COMMENTS = 0x10,
    ADMINISTRATOR = 0x80,
)
Article_Status=dict(
        s1=u'草稿',
        s2=u'发布',
        s3=u'仅好友可见',
        s4=u'亲密好友可见',
    )


class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer,primary_key=True)
    permission = db.Column(db.Integer)
    name = db.Column(db.String(64))
    user = db.relationship('UserInfo',backref='role',lazy='dynamic',cascade='all, delete-orphan')

    def __repr__(self):
        return '<Role:%s>'%self.name


class Follow(db.Model):
    __tablename__='follow'
    status=dict(
        comm='普通',
        follow='关注',
        friend='朋友',
        close='知己',
        black='拉黑',
    )
    follower_id = db.Column(db.Integer, db.ForeignKey('userinfo.id'),
                            primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('userinfo.id'),
                            primary_key=True)
    relationship = db.Column(db.String(20),default=status['comm'])
    created_time = db.Column(db.DateTime,default=datetime.utcnow)
    def __repr__(self):
        return '<Relationship:%s>'%self.relationship

category_registration = db.Table('category_registration',
                                 db.Column('category_id',db.Integer,db.ForeignKey('category.id')),
                                 db.Column('article_id',db.Integer,db.ForeignKey('article.id')),)

tag_registration = db.Table('tag_registration',
                            db.Column('tag_id',db.Integer,db.ForeignKey('tag.id')),
                            db.Column('article_id',db.Integer,db.ForeignKey('article.id')),)


PorC_registration = db.Table
class Category(db.Model):
    __tablename__='category'
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(64))
    created_time = db.Column(db.DateTime,default=datetime.utcnow)
    article = db.relationship('Article',
                              secondary=category_registration,
                              backref=db.backref('category',lazy='dynamic'),
                              lazy='dynamic',)



    def get_articles(self):
        return self.article

    def get_article_num(self):
        num = self.article.count()
        return num
    def __repr__(self):
        return '<Category_name:%s>'%self.name
class Tag(db.Model):
    __tablename__='tag'
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(64))
    created_time = db.Column(db.DateTime,default=datetime.utcnow)
    article = db.relationship('Article',
                              secondary=tag_registration,
                              backref=db.backref('tag',lazy='dynamic'),
                              lazy='dynamic',)



    def get_article_num(self):
        num = self.article.count()
        return num

    def get_articles(self):
        a = self.article
        return a
    def __repr__(self):
        return '<Tag_name:%s>'%self.name

class Article(db.Model):
    __tablename__ = 'article'
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(64))
    description = db.Column(db.String(250))
    content = db.Column(db.Text())
    author_id = db.Column(db.Integer,db.ForeignKey('userinfo.id'))
    created_time = db.Column(db.DateTime(),default=datetime.utcnow)
    release_time = db.Column(db.DateTime(),default=datetime.utcnow)
    status = db.Column(db.String(20),default=Article_Status['s1'])
    read_num = db.Column(db.Integer,default=0)
    shared_num = db.Column(db.Integer,default=0)
    poll_num = db.Column(db.Integer,default=0)
    critical_num = db.Column(db.Integer,default=0)
    comments = db.relationship('Comment',backref='article',lazy='dynamic')

    def get_categories(self):
        categories = self.category
        result = '无'
        c = [category.name for category in categories]
        if len(c)>0:
            result = c
        return result

    def get_tags(self):
        tags = self.tag
        result = '无'
        t = [tag.name for tag in tags]
        if len(t) > 0:
            result =  t
        return result

    def get_comment_num(self):
        return  self.comments.count()
    def __repr__(self):
        return '<Article_title:%s>'%self.title

class Article_PutPorC(db.Model):
    __tablename__ = 'article_putporc'
    id = db.Column(db.Integer,primary_key=True)
    author_id = db.Column(db.Integer,db.ForeignKey('userinfo.id'))
    article_id = db.Column(db.Integer,db.ForeignKey('article.id'))
    created_time = db.Column(db.DateTime,default=datetime.utcnow)
    poll = db.Column(db.Boolean,default=False)
    critical = db.Column(db.Boolean,default=False)

    def __repr__(self):
        would = 'No thing'
        if self.poll:
            would = 'fun'
        elif self.critical:
            would = 'critical'
        return '<Have: %s>'%would

class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer,primary_key=True)
    article_id = db.Column(db.Integer,db.ForeignKey('article.id'))
    author_id = db.Column(db.Integer,db.ForeignKey('userinfo.id'))
    receiver_id = db.Column(db.Integer,db.ForeignKey('userinfo.id'),default=-1)
    content = db.Column(db.Text())
    poll_num = db.Column(db.Integer,default=0)
    critical_num = db.Column(db.Integer,default=0)
    created_time = db.Column(db.DateTime,default=datetime.utcnow)
    is_read = db.Column(db.Boolean,default=False)
    put_porc = db.relationship('Comment_PutPorC',backref='comment',lazy='dynamic',cascade='all, delete-orphan')
    replys = db.relationship('Reply',backref='comment',lazy='dynamic',cascade='all, delete-orphan')

    def __repr__(self):
        return '<author: %s>'%self.author.nick_name

class Comment_PutPorC(db.Model):
    __tablename__ = 'comment_putporc'
    id = db.Column(db.Integer,primary_key=True)
    user_id = db.Column(db.Integer,db.ForeignKey('userinfo.id'))
    comment_id = db.Column(db.Integer,db.ForeignKey('comment.id'))
    created_time = db.Column(db.DateTime,default=datetime.utcnow)
    poll = db.Column(db.Boolean,default=False)
    critical = db.Column(db.Boolean,default=False)

    def __repr__(self):
        would = 'No thing'
        if self.poll:
            would = 'fun'
        elif self.critical:
            would = 'critical'
        return '<Have: %s>'%would

class Reply(db.Model):
    __tablename__ = 'reply'
    id = db.Column(db.Integer,primary_key=True)
    comment_id = db.Column(db.Integer,db.ForeignKey('comment.id'))
    author_id = db.Column(db.Integer,db.ForeignKey('userinfo.id'))
    receiver_id = db.Column(db.Integer,db.ForeignKey('userinfo.id'))
    content = db.Column(db.Text())
    poll_num = db.Column(db.Integer,default=0)
    critical_num = db.Column(db.Integer,default=0)
    created_time = db.Column(db.DateTime,default=datetime.utcnow)
    is_read = db.Column(db.Boolean,default=False)
    put_porc = db.relationship('Reply_PutPorC',backref='reply',lazy='dynamic',cascade='all, delete-orphan')
    def __repr__(self):
        return '<author: %s>'%self.author.nick_name

class Reply_PutPorC(db.Model):
    __tablename__ = 'reply_putporc'
    id = db.Column(db.Integer,primary_key=True)
    user_id = db.Column(db.Integer,db.ForeignKey('userinfo.id'))
    reply_id = db.Column(db.Integer,db.ForeignKey('reply.id'))
    created_time = db.Column(db.DateTime,default=datetime.utcnow)
    poll = db.Column(db.Boolean,default=False)
    critical = db.Column(db.Boolean,default=False)

    def __repr__(self):
        would = 'No thing'
        if self.poll:
            would = 'fun'
        elif self.critical:
            would = 'critical'
        return '<Have: %s>'%would

class Anonymous(AnonymousUserMixin):

    id=999
    email = 'Anonymous'
    gender='unknown'
    profile_img = ''
    motto = 'secret is  money!'
    nick_name = '神秘人'

    def is_authenticated(self):
        return False

    def can(self, permissions):
        return False

    def is_admin(self):
        return False

    def can_do(self,do):
        return do & Permission['WRITE_ARTICLES']

class UserInfo(UserMixin,db.Model):
    __tablename__ = 'userinfo'
    id = db.Column(db.Integer,primary_key=True)
    gender = db.Column(db.String(20),default='unknown')
    profile_img = db.Column(db.String(128),default='')
    motto = db.Column(db.String(128),default='这家伙很懒，并没有留下什么...')
    email = db.Column(db.String(128),unique=True)
    password_hash = db.Column(db.String(128))
    name = db.Column(db.String(64))
    nick_name = db.Column(db.String(64),unique=True)
    role_id = db.Column(db.Integer,db.ForeignKey(Role.id),default=1)
    member_since = db.Column(db.DateTime(),default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(),default=datetime.utcnow)
    followed = db.relationship('Follow',
                               foreign_keys=[Follow.follower_id],
                               backref=db.backref('follower', lazy='joined'),
                               lazy='dynamic',
                               cascade='all, delete-orphan')
    followers = db.relationship('Follow',
                                foreign_keys=[Follow.followed_id],
                                backref=db.backref('followed', lazy='joined'),
                                lazy='dynamic',
                                cascade='all, delete-orphan')
    article = db.relationship('Article',backref='author',lazy='dynamic',cascade='all, delete-orphan')
    comment = db.relationship('Comment',
                              foreign_keys=[Comment.author_id],
                              backref=db.backref('author',lazy='joined'),
                              cascade='all, delete-orphan')

    comment_receiver = db.relationship('Comment',
                                       foreign_keys=[Comment.receiver_id],
                                       backref=db.backref('receiver',lazy='joined'),
                                       lazy='dynamic',
                                       cascade='all,delete-orphan')
    reply = db.relationship('Reply',
                            foreign_keys=[Reply.author_id],
                            backref=db.backref('author',lazy='joined'),
                            lazy='dynamic',
                            cascade='all, delete-orphan')
    reply_receiver = db.relationship('Reply',
                                     foreign_keys=[Reply.receiver_id],
                                     backref=db.backref('receiver',lazy='joined'),
                                     lazy='dynamic',
                                     cascade='all, delete-orphan')

    @property
    def password(self):
        return '你不能直接获取密码。'

    @password.setter
    def password(self,p):
        self.password_hash = generate_password_hash(p)

    def check_password(self,p):
        return check_password_hash(self.password_hash,p)


    def get_gender(self):
        return gender_choice[self.gender]

    def can_do(self,something):
        permission = self.role.permission
        return  permission & something
    def is_admin(self):
        return self.role.name == 'Administrator'

    def is_followed(self,user_id):
        result = False

        if Follow.query.filter_by(follower_id=self.id,followed_id=user_id).count():
            result = True
        return result

    def __repr__(self):
        return '<UserName:%s>'%self.name



login_manager.anonymous_user = Anonymous

@login_manager.user_loader
def load_user(user_id):
    return UserInfo.query.get(int(user_id))