from flask import render_template, current_app, session, request, jsonify
from . import index_blur
from info.models import User, Category, News
import logging
from info import constants, response_code


# 主页渲染
@index_blur.route('/')
def index():
    # 通过session获取登陆状态
    user_id = session.get('user_id', None)
    user = None
    if user_id:
        try:
            user = User.query.get(user_id)
        except Exception as e:
            logging.error(e)

    categories = None
    news_clicks = None
    try:
        # 查询分类数据
        categories = Category.query.all()
        # 查询点击排行数据
        news_clicks = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as  e:
        logging.error(e)


    context = {
        "user": user.to_dict() if user else None,
        "categories": categories,
        "news_clicks": news_clicks
    }

    return render_template('news/index.html', context=context)


# 首页图标渲染
@index_blur.route('/favicon.ico')
def favicon():
    return current_app.send_static_file('news/favicon.ico')

# 新闻列表页数据
@index_blur.route('/news_list')
def index_news_list():
    # 获取参数　
    cid = request.args.get('cid', 1)
    page = request.args.get('page', 1)
    per_page = request.args.get('per_page', 10)
    # 判断参数
    if not all([cid,page,per_page]):
        return jsonify(erron=response_code.RET.PARAMERR, errmsg='参数错误')
    try:
        cid = int(cid)
        page = int(page)
        per_page = int(per_page)
    except Exception as e:
        logging.error(e)
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='参数错误')
    # 根据cid查询新闻列表页数据
    if cid == 1:
        try:
            paginate = News.query.order_by(News.create_time.desc()).paginate(page,per_page,False)
        except Exception as e:
            logging.error(e)
            return jsonify(errno=response_code.RET.DATAERR, errmsg='数据库错误')
    else:
        try:
            paginate = News.query.filter(News.category_id == cid).order_by(News.create_time.desc()).paginate(page,per_page,False)
        except Exception as e:
            logging.error(e)
            return jsonify(errno=response_code.RET.DATAERR, errmsg='数据库错误')

    current_page = paginate.page
    total_page = paginate.pages
    news_list = paginate.items
    # 构造响应数据
    news_dict_list = []
    for news in news_list:
        news_dict_list.append(news.to_basic_dict())

    return jsonify(errno=response_code.RET.OK, errmsg='OK', current_page=current_page,
                   total_page=total_page, news_dict_list=news_dict_list)