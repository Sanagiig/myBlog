from flask import render_template,abort,request,current_app,\
    redirect,url_for,jsonify
from flask_login import login_required,current_user

import json
from app.models import Article,Comment,Reply,\
    UserInfo
from app.article import art
from app.models import Permission,Category,Tag
from app.public.check import had_permission
from app import db

@art.route('/<int:article_id>')
@had_permission(Permission['WRITE_ARTICLES'])
def article(article_id):
    article = Article.query.get(article_id)
    page = request.args.get('page',1,type=int)
    if not article:
        abort(403)
    else:
        pagination = Comment.query.order_by(Comment.created_time.desc())\
                                .filter_by(article=article).paginate(page,
                                per_page=current_app.config['COMMENT_PER_PAGE'],error_out=False)
        comments=pagination.items
        categories = Category.query.all()
        tags = Tag.query.all()
        return render_template('blog/article.html',article=article,comments=comments,pagination=pagination,user_info=current_user,
                               categories=categories,tags=tags)


@art.route('/comment',methods=['POST','GET'])
@login_required
@had_permission(Permission['COMMENT'])
def comment():
    if request.method != 'POST':
        return redirect(url_for('main.index'))
    else:
        article_id = int(request.form.get('article_id'))
        CommentBody = request.form.get('CommentBody')
        article = Article.query.get(article_id)
        if not article :
            info = '''
                你所评论的文章并不存在，请刷新后再试。
            '''
            return  render_template('blog/404.html',info=info)
        else:
            comment = Comment(article_id=article_id,author_id=current_user.id,content=CommentBody,receiver_id=article.author_id)
            db.session.add(comment)
            try:
                db.session.commit()
            except Exception:
                db.session.rollback()
            return redirect(url_for('art.article',article_id=article_id))

@art.route('/reply',methods=['POST','GET'])
@login_required
@had_permission(Permission['COMMENT'])
def reply():
    if request.method != 'POST':
        return redirect(url_for('main.index'))
    else:
        article_id = int(request.form.get('article_id'))
        comment_id = int(request.form.get('comment_id'))
        receiver_id = int(request.form.get('receiver_id'))
        ReplyBody = request.form.get('ReplyBody')
        c = Comment.query.get(comment_id)
        if not c:
            info = '''
                你所恢复的评论并不存在，请刷新后再试。
            '''
            return  render_template('blog/404.html',info=info)
        else:
            reply = Reply(comment_id=comment_id,author_id=current_user.id,
                            receiver_id=receiver_id,content=ReplyBody)
            try:
                db.session.add(reply)
            except Exception:
                db.session.commit()
            return redirect(url_for('art.article',article_id=article_id))

@art.route('/put_poc',methods=['POST','GET'])
@login_required
@had_permission(Permission['PUT_PC'])
def put_poc():
    from app.public.oprate import article_put_poc,comment_put_poc
    if request.method != 'POST':
        return redirect(url_for('main.index'))
    else:
        data = json.loads(request.get_data().decode('utf-8'))
        opt = data['opt']
        obj = data['obj']
        obj_id = int(data['obj_id'])
        poc = int(data['poc'])
        result = False
        poll_num = 0
        critical_num = 0
        if opt == 'put_poc' and obj == 'article':
            result = True
            poll_num,critical_num = article_put_poc(current_user.id,obj_id,poc)
        elif opt == 'put_poc' and obj == 'comment':
            result = True
            poll_num,critical_num = comment_put_poc(current_user.id,obj_id,poc)

        return jsonify({'result':result,
                        'poll_num':poll_num,
                        'critical_num':critical_num})


