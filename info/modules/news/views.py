from flask import render_template, g, request, jsonify
from . import news_blue
from info.models import News, Comment, CommentLike
import logging
from info import constants, db, response_code
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
        # 　查询新闻
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
    is_followed = False
    if user:
        if news.user and news.user in user.followed:
            is_followed = True
    # 渲染用户点赞数据
    comment_like_ids = []
    comment_likes = None
    if user:
        try:
            # 1.查询出用户点赞的所有评论
            comment_likes = CommentLike.query.filter(CommentLike.user_id == user.id).all()
            # 2.找出用户点赞的所有评论的id
            comment_like_ids = [comment_like.comment_id for comment_like in comment_likes]
        except Exception as e:
            logging.error(e)

    # 渲染用户评论数据
    comments_list = []
    comments = None
    try:
        comments = Comment.query.filter(Comment.news_id==news_id).all()
    except Exception as e:
        logging.error(e)
    for comment in comments:
        comment_dict = comment.to_dict()
        comment_dict['is_like'] = False
        if comment.id in comment_like_ids:
            comment_dict['is_like'] = True
        comments_list.append(comment_dict)
    # 构造渲染数据
    context = {
        'user': user.to_dict() if user else None,
        'news_clicks': news_clicks,
        'news': news.to_dict(),
        'is_collected': is_collected,
        'comments': comments_list
    }
    return render_template('news/detail.html', context=context)


# 新闻收藏接口
@news_blue.route('/news_collect', methods=['POST'])
@get_data_user
def news_collect():
    # 判断用户是否登录
    user = g.user
    if not user:
        return jsonify(errno=response_code.RET.SESSIONERR, errmsg='用户未登录')
    # 接收参数
    json_dict = request.json
    news_id = json_dict.get('news_id')
    action = json_dict.get('action')
    # 校验参数
    if not all([news_id, action]):
        return jsonify(erron=response_code.RET.PARAMERR, errmsg='参数错误')
    if action not in ('collect', 'cancel_collect'):
        return jsonify(erron=response_code.RET.PARAMERR, errmsg='参数错误')
    # 判断新闻是否存在
    try:
        news = News.query.get(news_id)
    except Exception as e:
        logging.error(e)
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='数据库错误')
    if not news:
        return jsonify(errno=response_code.RET.NODATA, errmsg='新闻不存在')
    # 判断用户行为
    if action == 'collect':
        # 判断新闻在不在用户的新闻收藏表中
        if news not in user.collection_news:
            user.collection_news.append(news)
    else:
        if news in user.collection_news:
            user.collection_news.remove(news)

    # 同步到数据库
    try:
        db.session.commit()
    except Exception as e:
        logging.error(e)
        db.session.rollback()
        return jsonify(errno=response_code.RET.DATAERR, errmsg='数据库错误')
    # 返回用户操作状态
    return jsonify(errno=response_code.RET.OK, errmsg='操作成功')


# 用户评论接口
@news_blue.route('/news_comment', methods=['POST'])
@get_data_user
def news_comment():
    # 判断用户是否登录
    user = g.user
    if not user:
        return jsonify(errno=response_code.RET.SESSIONERR, errmsg='用户未登录')
    # 接收参数
    json_dict = request.json
    news_id = json_dict.get('news_id')
    comment_context = json_dict.get('comment')
    parent_id = json_dict.get('parent_id')
    # 判断参数是否齐全
    if not all([news_id, comment_context]):
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='参数错误')
    try:
        news_id = int(news_id)
        if parent_id:
            parent_id = int(parent_id)
    except Exception as e:
        logging.error(e)
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='参数错误')
    # 判断评论的新是否存在
    try:
        news = News.query.get(news_id)
    except Exception as e:
        logging.error(e)
        return jsonify(errno=response_code.RET.DATAERR, errmsg='数据库查询错误')
    if not news:
        return jsonify(errno=response_code.RET.NODATA, errmsg='数据不存在')
    # 创建评评论模型
    comment = Comment()
    comment.user_id = user.id
    comment.news_id = news.id
    comment.content = comment_context
    if parent_id:
        comment.parent_id = parent_id
    # 数据同步到数据库
    try:
        db.session.add(comment)
        db.session.commit()
    except Exception as e:
        logging.error(e)
        return jsonify(errno=response_code.RET.DATAERR, errmsg='数据库错误')
    # 返回给前台数据和状态
    return jsonify(errno=response_code.RET.OK, errmsg='OK', data=comment.to_dict())

# 用户点赞接口

@news_blue.route('/comment_like', methods=['POST'])
@get_data_user
def comment_like():
    #　判断用户是否登录
    user = g.user
    if not user:
        return jsonify(errno=response_code.RET.SESSIONERR, errmsg='用户未登录')
    # 接收参数
    json_dict = request.json
    comment_id = json_dict.get('comment_id')
    action = json_dict.get('action')
    # 判断参数
    if not all([comment_id, action]):
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='缺少参数')
    if action not in ('add', 'remove'):
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='参数错误')
    # 判断评论是否存在
    try:
        comment = Comment.query.get(comment_id)
    except Exception as e:
        return jsonify(errno=response_code.RET.DATAERR, errmsg='数据库查询错误')
    if not comment:
        return jsonify(errno=response_code.RET.NODATA, errmsg='评论不存在')
    # 判断点赞是否存在
    like_model = None
    try:
        like_model = CommentLike.query.filter(CommentLike.comment_id==comment_id,
                                              CommentLike.user_id==user.id).first()
    except Exception as e:
        logging.error(e)
        return jsonify(errno=response_code.RET.DATAERR, errmsg='数据库查询错误')
    # 判断用户操作
    if action=='add':
        if not like_model:
            # 构建点赞模型
            comment.like_count += 1
            like_model = CommentLike()
            like_model.comment_id = comment_id
            like_model.user_id = user.id
            db.session.add(like_model)
    else:
        if like_model:
            comment.like_count -= 1
            db.session.delete(like_model)
    # 数据同步到数据库
    try:
        db.session.commit()
    except Exception as e:
        return jsonify(errno=response_code.RET.DATAERR, errmsg='数据库查询错误')
    # 返回给前端点赞状态
    return jsonify(errno=response_code.RET.OK, errmsg='操作成功')
