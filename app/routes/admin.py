from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps
from app import db
from app.models.user import User
from app.models.novel import Novel
from app.models.comment import Comment

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('管理者権限が必要です', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated

@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    stats = {
        'total_users': User.query.count(),
        'total_novels': Novel.query.count(),
        'total_comments': Comment.query.count()
    }
    return render_template('admin/dashboard.html', stats=stats)
