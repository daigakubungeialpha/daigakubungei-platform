from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.novel import Novel
from app.models.like import Like
from datetime import datetime

novels_bp = Blueprint('novels', __name__)

# --- 新規投稿 ---
@novels_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        title = request.form.get('title')
        summary = request.form.get('summary')
        novel_type = request.form.get('novel_type')
        genre = request.form.get('genre')
        tags = request.form.get('tags')

        if novel_type == 'series':
            content = summary
        else:
            content = request.form.get('content')

        if not title:
            flash('タイトルは必須です')
            return redirect(url_for('novels.create'))

        new_novel = Novel(
            title=title,
            content=content,
            summary=summary,
            novel_type=novel_type,
            genre=genre,
            tags=tags,
            author=current_user,
            created_at=datetime.now()
        )
        db.session.add(new_novel)
        db.session.commit()

        flash('作品を作成しました！')
        if novel_type == 'series':
            return redirect(url_for('novels.novel_detail', novel_id=new_novel.id))
        else:
            return redirect(url_for('main.index'))

    return render_template('novels/create.html')

# --- エピソード追加 ---
@novels_bp.route('/<int:series_id>/add_chapter', methods=['GET', 'POST'])
@login_required
def add_chapter(series_id):
    series = Novel.query.get_or_404(series_id)
    if series.author != current_user:
        abort(403)
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        chapter = Novel(
            title=title, content=content, novel_type='chapter',
            parent_id=series.id, author=current_user, genre=series.genre,
            created_at=datetime.now()
        )
        db.session.add(chapter)
        db.session.commit()
        flash('投稿しました！')
        return redirect(url_for('novels.novel_detail', novel_id=series.id))
    recent_chapters = series.children.order_by(Novel.created_at.desc()).limit(3).all()
    recent_chapters = list(reversed(recent_chapters))
    return render_template('novels/add_chapter.html', series=series, recent_chapters=recent_chapters)

# --- 編集機能 ---
@novels_bp.route('/<int:novel_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(novel_id):
    novel = Novel.query.get_or_404(novel_id)
    if novel.author != current_user:
        abort(403)
    if request.method == 'POST':
        novel.title = request.form.get('title')
        novel.content = request.form.get('content')
        novel.summary = request.form.get('summary')
        novel.genre = request.form.get('genre')
        novel.tags = request.form.get('tags')
        db.session.commit()
        flash('更新しました')
        return redirect(url_for('novels.novel_detail', novel_id=novel.id))
    return render_template('novels/edit.html', novel=novel)

# --- 詳細表示 ---
@novels_bp.route('/<int:novel_id>')
def novel_detail(novel_id):
    novel = Novel.query.get_or_404(novel_id)  # ←元々あるコード

    novel.pv += 1
    db.session.commit()

    # ▼▼▼ ここに「PVセンサー」の2行を追加 ▼▼▼
    novel.pv += 1
    db.session.commit()
    # ▲▲▲ ここまで ▲▲▲
    liked = False
    if current_user.is_authenticated:
        liked = Like.query.filter_by(user_id=current_user.id, novel_id=novel.id).first() is not None
    tag_list = novel.tags.split() if novel.tags else []
    if novel.novel_type == 'series':
        chapters = novel.children.order_by(Novel.created_at.asc()).all()
        return render_template('novels/series_view.html', novel=novel, chapters=chapters, tag_list=tag_list, liked=liked)
    elif novel.novel_type == 'chapter':
        series = novel.parent
        return render_template('novels/view.html', novel=novel, series=series, liked=liked)
    return render_template('novels/view.html', novel=novel, tag_list=tag_list, liked=liked)

# --- ★修正：いいね機能（AJAX対応） ---
@novels_bp.route('/<int:novel_id>/like', methods=['POST'])
@login_required
def like(novel_id):
    novel = Novel.query.get_or_404(novel_id)
    existing_like = Like.query.filter_by(user_id=current_user.id, novel_id=novel.id).first()

    if existing_like:
        db.session.delete(existing_like)
        status = 'unliked'
    else:
        new_like = Like(user_id=current_user.id, novel_id=novel.id)
        db.session.add(new_like)
        status = 'liked'
    db.session.commit()

    # リロードなしで状態を返す
    return jsonify({
        'status': status,
        'count': len(novel.likes)
    })

# --- 削除 ---
@novels_bp.route('/<int:novel_id>/delete', methods=['POST'])
@login_required
def delete(novel_id):
    novel = Novel.query.get_or_404(novel_id)
    if novel.author != current_user:
        abort(403)
    db.session.delete(novel)
    db.session.commit()
    flash('削除しました')
    return redirect(url_for('main.index'))

    # ▼▼▼ 管理者用：PV操作機能 ▼▼▼
from flask import request

@novels_bp.route('/<int:novel_id>/update_pv', methods=['POST'])
@login_required
def update_pv(novel_id):
    # 1. 神（管理者）以外の実行を弾く
    if not current_user.is_admin:
        return redirect(url_for('main.index'))

    # 2. 対象の小説を取得して、新しいPV数を上書き保存
    from app import db # エラー防止のためここで読み込み
    from app.models.novel import Novel

    novel = Novel.query.get_or_404(novel_id)
    new_pv = request.form.get('new_pv', type=int)

    if new_pv is not None and new_pv >= 0:
        novel.pv = new_pv
        db.session.commit()

    # 3. ダッシュボードに戻る
    return redirect(url_for('users.admin_dashboard'))
