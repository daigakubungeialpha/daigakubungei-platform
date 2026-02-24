from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models.novel import Novel
from app.models.like import Like

users_bp = Blueprint('users', __name__)

@users_bp.route('/mypage')
@login_required
def mypage():
    # 自分が投稿した作品（最新順）
    # 短編と連載の親のみを表示
    my_novels = Novel.query.filter_by(author_id=current_user.id)\
                .filter(Novel.novel_type.in_(['short', 'series']))\
                .order_by(Novel.created_at.desc()).all()

    # 自分がいいねした作品（Likeモデルから取得）
    liked_items = Like.query.filter_by(user_id=current_user.id).all()
    # いいねしたNovelオブジェクトのリストを作成
    liked_novels = [item.novel for item in liked_items if item.novel.novel_type in ['short', 'series']]
    
    return render_template('users/mypage.html', 
                           my_novels=my_novels, 
                           liked_novels=liked_novels)
