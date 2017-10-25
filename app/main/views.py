from flask import request,current_app,render_template,g,session,render_template_string
from flask_login import current_user

import json
from app.main import  main
from app.models import Article,Category,Tag,\
    Comment,Reply,\
    UserInfo,Article_PutPorC,Comment_PutPorC,Reply_PutPorC,\
    Anonymous


#首页
#返回文章
@main.route('/',methods=['GET','POST'])
def index():
    page = request.args.get('page',1,type=int)
    search_category = request.args.get('category','',type=str)
    search_tag = request.args.get('tag','',type=str)
    search_text = request.args.get('search','',type=str)
    if search_category:
        pagination = Category.query.filter_by(name=search_category).first()\
                    .get_articles()\
                    .paginate(page=page,per_page=current_app.config['ARTICLE_PER_PAGE'],error_out=False)
    if search_tag:
        pagination = Tag.query.filter_by(name=search_tag).first()\
                    .get_articles()\
                    .paginate(page=page,per_page=current_app.config['ARTICLE_PER_PAGE'],error_out=False)
    if search_text:
        pagination = Article.query.filter(Article.title.like('%'+ search_text + '%'))\
                    .paginate(page=page,per_page=current_app.config['ARTICLE_PER_PAGE'],error_out=False)

    if not (search_category or search_tag or search_text):
        pagination = Article.query.order_by(Article.created_time.desc()).paginate(
                page,per_page=current_app.config['ARTICLE_PER_PAGE'],error_out=False)

    categories = Category.query.all()
    tags = Tag.query.all()
    articles = pagination.items
    return  render_template('blog/index.html',user_info=current_user,
                            articles=articles,pagination=pagination,comment='',
                            categories=categories,tags=tags,
                            search_category=search_category,search_tag=search_tag,search_text=search_text)

@main.app_errorhandler(403)
def err403(e):
    return render_template('blog/404.html',info=e)

@main.app_errorhandler(404)
def err404(e):
    return render_template('blog/404.html',info=e,user_info='')

@main.route('/test')
def test():
    data={
        'code':session['check_code'],
    }
    return json.dumps(data)