from flask import render_template,request,current_app,redirect,url_for,abort,\
    jsonify
from flask_login import current_user,login_required
from app import db
from app.user import user
from app.public.check import had_permission,can_touch_user
from app.models import UserInfo,Article,Comment,Reply,\
    Category,Tag,Permission,Article_Status,Follow
import json

@user.route('/')
def index():
    user_id = request.args.get('user_id',-1,type=int)
    user_info=current_user
    if user_id != -1:
        user_info = UserInfo.query.get_or_404(user_id)
    return render_template('user/index.html',user_info=user_info)

@user.route('/profile/<int:user_id>')
def profile(user_id):
    user_info = UserInfo.query.get_or_404(int(user_id))
    return render_template('user/profile.html',user_info=user_info)

@user.route('/preview',methods=['POST'])
@login_required
@had_permission(Permission['WRITE_ARTICLES'])
def preview():
    data = request.get_data().decode('utf-8')
    data = json.loads(data)
    opt = data['opt']
    user_id = int(data['user_id'])
    result = False
    if not can_touch_user(user_id):
        abort(403)

    if opt == 'preview_comment':
        comment_id = int(data['comment_id'])
        comment = Comment.query.get_or_404(comment_id)
        comment.is_read = True
        db.session.add(comment)
        try:
            db.session.commit()
            result = True
        except Exception:
            db.session.rollback()
        return jsonify({'result':result,'content':comment.content})
    elif opt =='preview_reply':
        reply_id = int(data['reply_id'])
        reply = Reply.query.get_or_404(reply_id)
        reply.is_read = True
        db.session.add(reply)
        try:
            db.session.commit()
            result = True
        except Exception:
            print('<{func}>-----数据库出错'.format(func='preview'))
            db.session.rollback()
        return jsonify({'result':result,'content':reply.content})

@user.route('/delete',methods=['POST'])
@login_required
@had_permission(Permission['WRITE_ARTICLES'])
def delete():
    from app.public.oprate import article_delete, comment_delete,reply_delete,category_delete,tag_delete
    from app.public.check import check_can_delete_article,check_can_delete_comment,\
        check_can_delete_reply

    data = json.loads(request.get_data().decode('utf-8'))
    opt = data['opt']
    result = True
    #删除回复
    if opt == 'del_reply' and check_can_delete_reply(int(data['reply_id'])):
        reply_id = data['reply_id']
        if not reply_delete(reply_id):
            result=False

    elif opt == 'del_replys':
        reply_id_list = data['reply_id_list']
        for reply_id in reply_id_list:
            if not check_can_delete_reply(int(reply_id)) or  not reply_delete(int(reply_id)):
                result = False
                break
    #删除评论
    elif opt == 'del_comment' and check_can_delete_comment(int(data['comment_id'])):
        comment_id = data['comment_id']
        if not check_can_delete_comment(comment_id) or  not comment_delete(comment_id):
            result=False

    elif opt == 'del_comments':
        comment_id_list = data['comment_id_list']
        for comment_id in comment_id_list:
            if  not comment_delete(comment_id):
                result=False
                break
    #删除文章
    elif opt == 'del_article' and check_can_delete_article(int(data['article_id'])):
        article_id = data['article_id']
        if not check_can_delete_article(article_id) or not article_delete(article_id):
            result=False
    elif opt == 'del_articles':
        articles_id_list = data['articles_id_list']
        for article_id in articles_id_list:
            if not check_can_delete_article(int(article_id)) or not article_delete(article_id):
                result=False
                break
    #删除分类
    elif opt == 'del_category':
        category_id = int(data['category_id'])
        if not current_user.is_admin()  or category_id == 0 or not category_delete(category_id):
            result=False

    #删除标签
    elif opt == 'del_tag':
        tag_id = int(data['tag_id'])
        if not current_user.is_admin()  or tag_id == 0 or not tag_delete(tag_id):
            result=False
    else:
        result = False
    return jsonify({'result':result})

@user.route('/article_list/<int:user_id>')
def article_list(user_id):
    page = request.args.get('page',1,type=int)
    # pagination = Article.query.order_by(Article.created_time.desc()).\
    #                 filter_by(author_id=id).\
    #                 paginate(page=page,per_page=current_app.config['ARTICLE_PER_PAGE'],error_out=False)
    articles = Article.query.filter_by(author_id=user_id)
    user_info = UserInfo.query.get_or_404(user_id)
    return render_template('user/article_list.html',articles=articles,user_info=user_info)


@user.route('/add_article',methods=['POST','GET'])
@login_required
@had_permission(Permission['WRITE_ARTICLES'])
def add_article():
    if request.method == 'GET':
        user_id=request.args.get('user_id',-1,type=int)
        if not can_touch_user(user_id):
            abort(403)
        user_info = UserInfo.query.get_or_404(user_id)
        categories = Category.query.order_by(Category.created_time.desc())
        tags = Tag.query.order_by(Tag.created_time.desc())
        return render_template('user/add_article.html',user_info=user_info,categories=categories,tags=tags)
    else:
        '''
        对于管理员来说，进入某个用户的空间，就能以某个用户的名义发送数据
        '''
        from app.public.oprate import article_add_categories,article_add_tags
        data=json.loads(request.get_data().decode('utf-8'))
        user_id = data['user_id']
        if not can_touch_user(user_id):
            abort(403)

        result = False
        author_id = user_id
        title = data['title']
        content = data['content']
        status = data['status']
        categories = data['categories']
        tags = data['tags']

        if(data['author'] == '2'):
            author_id = current_user.id
        article = Article(author_id = author_id,title=title,content=content,status=status)
        article_add_categories(article,categories)
        article_add_tags(article,tags)
        db.session.add(article)
        try:
            db.session.commit()
            result = True
        except Exception:
            db.session.rollback()
        return jsonify({'result':result})

@user.route('/edit_article/', methods=['POST','GET'])
@login_required
@had_permission(Permission['WRITE_ARTICLES'])
def edit_article():
    if request.method == 'GET':
        article_id = request.args.get('article_id',-1,type=int)
        user_id = request.args.get('user_id',-1,type=int)
        if not can_touch_user(user_id):
            abort(403)
        article = Article.query.get_or_404(article_id)
        user_info = UserInfo.query.get_or_404(user_id)
        categories = Category.query.all()
        tags = Tag.query.all()
        return render_template('user/edit_article.html',article=article,user_info=user_info,
                               categories=categories,tags=tags)
    else:
        from datetime import datetime
        from app.public.oprate import article_add_categories,article_add_tags
        data = json.loads(request.get_data().decode('utf-8'))
        user_id = data['user_id']

        if not can_touch_user(user_id):
            abort(403)

        result = False
        author_id = user_id
        article_id = data['article_id']
        title = data['title']
        content = data['content']
        status = data['status']
        categories = data['categories']
        tags = data['tags']
        if(data['author'] == '2'):
            author_id = current_user.id
        article = Article.query.get_or_404(article_id)
        article.author_id = author_id
        article.title = title
        article.content = content
        article.status = status
        article_add_categories(article,categories)
        article_add_tags(article,tags)
        article.release_time = datetime.utcnow()
        db.session.add(article)
        try:
            db.session.commit()
            result = True
        except Exception:
            db.session.rollback()

        return jsonify({'result':result})



@user.route('/add_categories',methods=['POST'])
@login_required
@had_permission(Permission['ADMINISTRATOR'])
def add_categories():
    from app.public.oprate import create_categories
    result = False
    data = request.get_data().decode('utf-8')
    data = json.loads(data)
    category_list = data['category_list']
    if  create_categories(category_list):
        result = True
    return jsonify({'result':result})

@user.route('/edit_categories',methods=['POST','GET'])
@login_required
@had_permission(Permission['ADMINISTRATOR'])
def edit_categories():
    if request.method == 'GET':
        user_info = UserInfo.query.get_or_404(request.args.get('user_id'))
        categories = Category.query.all()
        return render_template('user/categories.html',user_info=user_info,categories=categories)
    elif request.method == 'POST':
        result = False
        data = request.get_data().decode('utf-8')
        data = json.loads(data)
        category_id = int(data['category_id'])
        category_name = data['category_name']
        c = Category.query.get_or_404(category_id)
        c.name = category_name
        db.session.add(c)
        try:
            db.session.commit()
            result = True
        except Exception:
            db.session.rollback()
        return jsonify({'result':result})

@user.route('/add_tags',methods=['POST'])
@login_required
@had_permission(Permission['ADMINISTRATOR'])
def add_tags():
    from app.public.oprate import create_tags
    result = False
    data = request.get_data().decode('utf-8')
    data = json.loads(data)
    tag_list = data['tag_list']
    print('------------',tag_list)
    if  create_tags(tag_list):
        result = True
    return jsonify({'result':result})

@user.route('/edit_tags',methods=['POST','GET'])
@login_required
@had_permission(Permission['ADMINISTRATOR'])
def edit_tags():
    if request.method == 'GET':
        user_info = UserInfo.query.get_or_404(request.args.get('user_id'))
        tags = Tag.query.all()
        return render_template('user/tags.html',user_info=user_info,tags=tags)
    elif request.method == 'POST':
        result = False
        data = request.get_data().decode('utf-8')
        data = json.loads(data)
        tag_id = int(data['tag_id'])
        tag_name = data['tag_name']
        t = Tag.query.get_or_404(tag_id)
        t.name = tag_name
        db.session.add(t)
        try:
            db.session.commit()
            result = True
        except Exception:
            db.session.rollback()
        return jsonify({'result':result})

@user.route('/reply_list', methods=['POST','GET'])
@login_required
@had_permission(Permission['WRITE_ARTICLES'])
def reply_list():
    if request.method == 'GET':
        user_id = int(request.args.get('user_id'))
        page = request.args.get('page',1,type=int)
        if not can_touch_user(user_id):
            abort(403)
        pagination = Reply.query.filter_by(author_id=user_id).\
                    order_by(Reply.created_time.desc()).\
                    paginate(page=page,per_page=current_app.config['REPLY_PER_PAGE'],error_out=False)
        replys = pagination.items
        user_info = UserInfo.query.get_or_404(user_id)
        return render_template('user/reply_list.html',user_info=user_info,replys=replys,pagination=pagination)

@user.route('/comment_list', methods=['POST','GET'])
@login_required
@had_permission(Permission['WRITE_ARTICLES'])
def comment_list():
    if request.method == 'GET':
        user_id = int(request.args.get('user_id'))
        page = request.args.get('page',1,type=int)
        if not can_touch_user(user_id):
            abort(403)
        pagination = Comment.query.filter_by(author_id=user_id).\
                    order_by(Comment.created_time.desc()).\
                    paginate(page=page,per_page=current_app.config['COMMENT_PER_PAGE'],error_out=False)
        comments = pagination.items
        user_info = UserInfo.query.get_or_404(user_id)
        return render_template('user/comment_list.html',user_info=user_info,comments=comments,pagination=pagination)

@user.route('/receive_comment_list',methods=['POST','GET'])
@login_required
@had_permission(Permission['WRITE_ARTICLES'])
def receive_comment_list():
    if request.method == 'GET':
        user_id = int(request.args.get('user_id'))
        page = request.args.get('page',1,type=int)
        COMMENT_PER_PAGE = request.args.get('per_page',current_app.config['COMMENT_PER_PAGE'],type=int)
        if can_touch_user(user_id):
            user_info = UserInfo.query.get_or_404(user_id)
            pagination = Comment.query.order_by(Comment.created_time.desc()).\
                         filter_by(receiver_id=user_id).\
                         paginate(page=page,per_page=COMMENT_PER_PAGE)
            comments = pagination.items
            return render_template('user/receive_comment_list.html',user_info=user_info,pagination=pagination,\
                                   comments=comments)

@user.route('/receive_reply_list',methods=['POST','GET'])
@login_required
@had_permission(Permission['WRITE_ARTICLES'])
def receive_reply_list():
    if request.method == 'GET':
        user_id = int(request.args.get('user_id'))
        page = request.args.get('page',1,type=int)
        REPLY_PER_PAGE = request.args.get('per_page',current_app.config['REPLY_PER_PAGE'],type=int)
        if can_touch_user(user_id):
            user_info = UserInfo.query.get_or_404(user_id)
            pagination = Reply.query.order_by(Reply.created_time.desc()).\
                         filter_by(receiver_id=user_id).\
                         paginate(page=page,per_page=REPLY_PER_PAGE)
            replys = pagination.items
            return render_template('user/receive_reply_list.html',user_info=user_info,pagination=pagination,\
                                   replys=replys)


@user.route('/follow',methods=['POST'])
@login_required
@had_permission(Permission['WRITE_ARTICLES'])
def follow():
    result = True
    data = request.get_data().decode('utf-8')
    data = json.loads(data)
    follower_id = int(data['follower'])
    followed_id = int(data['followed'])
    opt = data['opt']
    follower = UserInfo.query.get_or_404(follower_id)
    followed = UserInfo.query.get_or_404(followed_id)
    print('=============================================')
    try:
        if opt == 'following':
            follow = Follow(follower=follower,followed=followed)
            db.session.add(follow)

        else:
            f = follower.followed.filter_by(followed_id=followed_id).first()
            if f:
                db.session.delete(f)
        # else:
        #     f = follower.followed.filter(followed_id=followed_id)
        #     db.session.delete(f)
    except Exception as e:
        result = False
        db.session.rollback()
        print('关注对象时出错 ！ ')
        print(e)

    return jsonify({'result':result})