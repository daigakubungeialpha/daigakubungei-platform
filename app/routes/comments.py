from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.comment import Comment
from app.models.novel import Novel
from datetime import datetime

comments_bp = Blueprint('comments', __name__)

@comments_bp.route('/create/<int:novel_id>', methods=['POST'])
@login_required
def create_comment(novel_id):
    novel = Novel.query.get_or_404(novel_id)
    content = request.form.get('content')
    quote_text = request.form.get('quote_text')
    parent_id = request.form.get('parent_id')

    if not content:
        return jsonify({'error': 'コメント内容を入力してください'}), 400

    if not parent_id:
        parent_id = None
    else:
        parent_id = int(parent_id)

    comment = Comment(
        content=content,
        quote_text=quote_text,
        parent_id=parent_id,
        user_id=current_user.id,
        novel_id=novel_id,
        created_at=datetime.now()
    )
    
    db.session.add(comment)
    db.session.commit()
    
    # リロードせずに画面に追加するためのデータを返す
    return jsonify({
        'status': 'success',
        'id': comment.id,
        'author': current_user.username,
        'content': comment.content,
        'created_at': comment.created_at.strftime('%m/%d %H:%M'),
        'quote_text': comment.quote_text,
        'parent_id': comment.parent_id
    })
