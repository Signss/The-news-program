from flask import render_template, g
from . import news_blue
from info.models import  News
import logging
from info import constants, db
from info.untils.common import get_data_user


# 注册路由
@news_blue.route('/detail/<int:news_id>')
@get_data_user
def news_detail(news_id):
    # 获取用户信息
    user = g.user

    news_clicks = None
    news = None
    try:
        #　查询新闻
        news = News.query.get(news_id)
        # 查询点击排行数据
        news_clicks = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        logging.error(e)
    # 每次进入新闻详情页，修改新闻的点击量以达到修改点击排行
    news.clicks += 1
    try:
        db.session.commit()
    except Exception as e:
        db.session.roolback()
        logging.error(e)
    # 判断用户是否收藏
    is_collected = False
    if user:
        if news in user.collection_news:
            is_collected = True
    # 构造渲染数据
    context = {
        'user': user.to_dict() if user else None,
        'news_clicks': news_clicks,
        'news': news.to_dict(),
        'is_collected': is_collected
    }
    return render_template('news/detail.html', context=context)