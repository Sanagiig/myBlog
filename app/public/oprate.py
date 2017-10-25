from app import db

def article_put_poc(user_id,article_id,poc):
    from app.models import Article,Article_PutPorC
    a = Article.query.get_or_404(article_id)
    ap = Article_PutPorC.query.filter_by(author_id=user_id,article_id=article_id).first()
    if not ap:
        ap = Article_PutPorC(author_id=user_id,article_id=article_id)
    if poc == 1:
        if ap.critical:
            ap.critical = False
            a.critical_num -=1

        if ap.poll :
            ap.poll = False
            a.poll_num -=1
        else:
            ap.poll = True
            a.poll_num +=1

    elif poc == 2:
        if ap.poll:
            ap.poll = False
            a.poll_num -=1

        if ap.critical:
            ap.critical = False
            a.critical_num -=1
        else:
            ap.critical = True
            a.critical_num +=1
    db.session.add(ap)
    db.session.add(a)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()

    return a.poll_num,a.critical_num

def comment_put_poc(user_id,comment_id,poc):
    from app.models import Comment,Comment_PutPorC
    c = Comment.query.get_or_404(int(comment_id))
    cp = Comment_PutPorC.query.filter_by(user_id=user_id,comment_id=comment_id).first()
    if not cp:
        cp = Comment_PutPorC(user_id=user_id,comment_id=comment_id)
    if poc == 1:
        if cp.critical:
            cp.critical = False
            c.critical_num -=1

        if cp.poll:
            cp.poll = False
            c.poll_num -=1
        else:
            cp.poll = True
            c.poll_num +=1
    elif poc == 2:
        if cp.poll:
            cp.poll = False
            c.poll_num -=1

        if cp.critical:
            cp.critical = False
            c.critical_num -=1
        else :
            cp.critical = True
            c.critical_num +=1

    db.session.add(cp)
    db.session.add(c)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()

    return c.poll_num,c.critical_num

def reply_delete(reply_id):
    from app.models import Reply
    result = False
    r = Reply.query.get_or_404(int(reply_id))
    db.session.delete(r)
    try:
        db.session.commit()
        result = True
    except Exception:
        db.session.rollback()
    return  result

def comment_delete(comment_id):
    from app.models import  Comment
    result = False
    c = Comment.query.get_or_404(int(comment_id))
    #删除相关回复
    for reply in c.replys.all():
        reply_delete(reply.id)
    db.session.delete(c)
    try:
        db.session.commit()
        result = True
    except Exception:
        db.session.rollback()
    return result

def article_delete(article_id):
    from app.models import Article
    result = False
    a = Article.query.get_or_404(int(article_id))
    #删除相关评论
    for comment in a.comments:
        comment_delete(comment.id)
    db.session.delete(a)
    try:
        db.session.commit()
        result = True
    except Exception:
        db.session.rollback()
    return  resultpri

def category_delete(category_id):
    from app.models import Category,Article
    result = False
    c = Category.query.get_or_404(int(category_id))
    db.session.delete(c)
    try:
        db.session.commit()
        result = True
    except Exception:
        db.session.rollback()
    return  result

def tag_delete(tag_id):
    from app.models import Tag,Article
    result = False
    t = Tag.query.get_or_404(int(tag_id))
    #删除标签
    db.session.delete(t)
    try:
        db.session.commit()
        result = True
    except Exception:
        db.session.rollback()
    return  result

def article_add_categories(article,cats):
    from app.models import Category
    result = False
    try:
        for cat in article.category:
            article.category.remove(cat)
        for cat in cats:
            c = Category.query.filter_by(name=cat).first()
            article.category.append(c)
        result= True
    except Exception:
        print('---------添加分类出错')
    return  result

def article_add_tags(article,tags):
    from app.models import Tag
    result = False
    try:
        for t in article.tag:
            article.tag.remove(t)
        for tag in tags:
            t = Tag.query.filter_by(name=tag).first()
            article.tag.append(t)
        result = True
    except Exception:
        print('--------添加标签出错')

    return result

def create_categories(category_list):
    from app.models import Category
    result = False
    for category in category_list:
        c = Category(name=category)
        db.session.add(c)
    try:
        db.session.commit()
        result = True
    except Exception:
        db.session.rollback()
    return result

def create_tags(tag_list):
    from app.models import Tag
    result = False
    print('----------',tag_list)
    for tag in tag_list:
        t = Tag(name=tag)
        db.session.add(t)
    try:
        db.session.commit()
        result = True
    except Exception:
        db.session.rollback()
    return result

