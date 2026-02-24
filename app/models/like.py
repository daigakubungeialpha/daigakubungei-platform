from app import db
from datetime import datetime

class Like(db.Model):
    __tablename__ = 'like'  # ★名前を固定
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # ★ user.id, novel.id（単数）を参照
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    novel_id = db.Column(db.Integer, db.ForeignKey('novel.id'), nullable=False)
