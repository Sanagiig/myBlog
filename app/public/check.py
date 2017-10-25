from flask_login import current_user
from flask import abort

from functools import wraps
import re

from app.models import  Permission


def check_email(email):
    pattern = '[A-Za-z0-9]+.*@[A-Za-z]+.*\..*'
    result = re.match(pattern,email)
    return result or False

def check_password(p):
    return len(p) >= 3
#判断是否是该回复的作者，或管理员
def check_can_delete_reply(reply_id):
    from app.models import Reply
    result = False
    reply = Reply.query.get_or_404(int(reply_id))
    article_author_id = reply.comment.article.author_id
    reply_author_id = reply.author_id
    role = current_user.role.name
    c_id = current_user.id
    if article_author_id == c_id or reply_author_id == c_id \
            or role == 'Administrator':
        result =True

    return result

def check_can_delete_comment(comment_id):
    from app.models import Comment
    result = False
    comment = Comment.query.get_or_404(int(comment_id))
    comment_author_id = comment.author_id
    role = current_user.role.name
    c_id = current_user.id
    if comment_author_id == c_id or role == 'Administrator':
        result =True
    return result

def check_can_delete_article(article_id):
    from app.models import Article
    result = False
    article = Article.query.get_or_404(int(article_id))
    article_author_id = article.author_id
    role = current_user.role.name
    c_id = current_user.id
    if article_author_id == c_id or role == 'Administrator':
        result =True

    return result

def can_touch_user(user_id):
    user_id = int(user_id)
    result = False
    if current_user.is_admin() or user_id == current_user.id:
        result = True
    return result

def had_permission(permission):
    def decorator(fuc):
        @wraps(fuc)
        def decorated_fuc(*args,**kwargs):
            if not current_user.can_do(permission):
                abort(403)
            return fuc(*args,**kwargs)
        return decorated_fuc
    return decorator

def is_admin(fuc):
    had_permission(Permission['ADMINISTRATOR'])(fuc)


