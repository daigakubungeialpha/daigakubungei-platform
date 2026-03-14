from app import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.now)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.now)

    # ▼▼ ここから追加 ▼▼
    is_admin = db.Column(db.Boolean, default=False)  # 管理者かどうか（初期値はFalse）
    is_banned = db.Column(db.Boolean, default=False) # BANされているか（初期値はFalse）
    # ▲▲ ここまで追加 ▲▲

    # 小説との関係
    novels = db.relationship('Novel', backref='author', lazy=True)
    # 小説との関係
    novels = db.relationship('Novel', backref='author', lazy=True)

    # パスワード機能
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
