from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models.user import User
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

# ▼▼▼ ここから管理者の神機能 ▼▼▼

@users_bp.route('/admin')
@login_required
def admin_dashboard():
    """管理者専用ダッシュボードを表示する扉"""
    # 1. 神（管理者）以外のアクセスを弾く
    if not current_user.is_admin:
        flash('管理者権限がありません。', 'danger')
        return redirect(url_for('main.index'))

    # 2. ダッシュボードに表示するため、全ユーザーと全作品を取得
    users = User.query.all()
    novels = Novel.query.filter(Novel.novel_type.in_(['short', 'series'])).order_by(Novel.created_at.desc()).all()

    # 3. 先ほど作ったコントロールルーム（HTML）にデータを渡して表示！
    return render_template('admin_dashboard.html', users=users, novels=novels)

@users_bp.route('/<int:user_id>/toggle_ban', methods=['POST'])
@login_required
def toggle_ban(user_id):
    """ユーザーをBAN（または解除）する機能"""
    # 1. 神（管理者）以外の実行を弾く
    if not current_user.is_admin:
        flash('管理者権限がありません。', 'danger')
        return redirect(url_for('main.index'))

    target_user = User.query.get_or_404(user_id)

    # 2. 自分自身（管理者）を間違えてBANしないようにする安全装置
    if target_user.id == current_user.id:
        flash('自分自身をBANすることはできません。', 'danger')
        return redirect(url_for('users.admin_dashboard'))

    # 3. BAN状態を切り替える（BANされていれば解除、されていなければBAN）
    target_user.is_banned = not target_user.is_banned
    db.session.commit() # データベースを上書き保存！

    # 4. コントロールルームに戻る
    return redirect(url_for('users.admin_dashboard'))

# ▲▲▲ ここまで ▲▲▲