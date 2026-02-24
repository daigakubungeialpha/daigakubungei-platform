from app import db
from datetime import datetime

class Novel(db.Model):
    __tablename__ = 'novel'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    
    summary = db.Column(db.Text)
    novel_type = db.Column(db.String(20))
    genre = db.Column(db.String(50))
    tags = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # 連載用（親子関係）
    parent_id = db.Column(db.Integer, db.ForeignKey('novel.id'), nullable=True)
    children = db.relationship('Novel', 
                             backref=db.backref('parent', remote_side=[id]),
                             lazy='dynamic',
                             cascade='all, delete-orphan')

    # コメント・いいね
    comments = db.relationship('Comment', backref='novel', lazy=True, cascade="all, delete")
    likes = db.relationship('Like', backref='novel', lazy=True, cascade="all, delete")
